import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
import jmespath
from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select

from .database import Base, engine, SessionLocal
from .models import Provider
from .schemas import ProviderCreate, ProviderOut, ProviderUpdate

app = FastAPI(title="Parts Search Aggregator")
templates = Jinja2Templates(directory="app/templates")


# -------------------- DB Dependency --------------------

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


# -------------------- Startup --------------------

@app.on_event("startup")
def on_startup() -> None:
	Base.metadata.create_all(bind=engine)


# -------------------- HTML Views --------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, article: Optional[str] = None, db: Session = Depends(get_db)):
	results: List[Dict[str, Any]] = []
	errors: List[Dict[str, Any]] = []
	if article:
		agg = await aggregate_search(article, db)
		results = agg["results"]
		errors = agg["errors"]
	return templates.TemplateResponse("index.html", {"request": request, "results": results, "errors": errors, "article": article or ""})


@app.get("/providers", response_class=HTMLResponse)
async def providers_page(request: Request, db: Session = Depends(get_db)):
	providers = db.execute(select(Provider).order_by(Provider.id.desc())).scalars().all()
	return templates.TemplateResponse("providers.html", {"request": request, "providers": providers})


@app.get("/providers/new", response_class=HTMLResponse)
async def new_provider_page(request: Request):
	return templates.TemplateResponse("provider_form.html", {"request": request, "provider": None})


@app.get("/providers/{provider_id}/edit", response_class=HTMLResponse)
async def edit_provider_page(provider_id: int, request: Request, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	return templates.TemplateResponse("provider_form.html", {"request": request, "provider": provider})


@app.post("/providers/save")
async def save_provider(
	request: Request,
	provider_id: Optional[int] = Form(default=None),
	name: str = Form(...),
	enabled: Optional[bool] = Form(default=False),
	method: str = Form(default="GET"),
	url_template: str = Form(...),
	headers_json: Optional[str] = Form(default=None),
	jmespath_expr: Optional[str] = Form(default=None),
	timeout_seconds: int = Form(default=10),
	db: Session = Depends(get_db),
):
	if headers_json:
		try:
			json.loads(headers_json)
		except Exception as exc:  # noqa: BLE001
			return templates.TemplateResponse(
				"provider_form.html",
				{"request": request, "provider": None, "error": f"Invalid headers JSON: {exc}"},
				status_code=400,
			)

	if provider_id:
		provider = db.get(Provider, provider_id)
		if not provider:
			raise HTTPException(status_code=404, detail="Provider not found")
		provider.name = name
		provider.enabled = bool(enabled)
		provider.method = method
		provider.url_template = url_template
		provider.headers_json = headers_json
		provider.jmespath_expr = jmespath_expr
		provider.timeout_seconds = timeout_seconds
	else:
		provider = Provider(
			name=name,
			enabled=bool(enabled),
			method=method,
			url_template=url_template,
			headers_json=headers_json,
			jmespath_expr=jmespath_expr,
			timeout_seconds=timeout_seconds,
		)
		db.add(provider)
	try:
		db.commit()
		db.refresh(provider)
	except Exception as exc:  # noqa: BLE001
		db.rollback()
		return templates.TemplateResponse(
			"provider_form.html",
			{"request": request, "provider": provider, "error": f"Save error: {exc}"},
			status_code=400,
		)
	return RedirectResponse(url="/providers", status_code=303)


@app.post("/providers/{provider_id}/delete")
async def delete_provider(provider_id: int, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	db.delete(provider)
	db.commit()
	return RedirectResponse(url="/providers", status_code=303)


@app.post("/providers/{provider_id}/toggle")
async def toggle_provider(provider_id: int, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	provider.enabled = not provider.enabled
	db.commit()
	return RedirectResponse(url="/providers", status_code=303)


# -------------------- JSON API --------------------

@app.get("/api/providers", response_model=List[ProviderOut])
def list_providers(db: Session = Depends(get_db)):
	providers = db.execute(select(Provider).order_by(Provider.id.desc())).scalars().all()
	return providers


@app.post("/api/providers", response_model=ProviderOut)
def create_provider(payload: ProviderCreate, db: Session = Depends(get_db)):
	provider = Provider(**payload.model_dump())
	db.add(provider)
	try:
		db.commit()
		db.refresh(provider)
	except Exception as exc:  # noqa: BLE001
		db.rollback()
		raise HTTPException(status_code=400, detail=str(exc))
	return provider


@app.get("/api/providers/{provider_id}", response_model=ProviderOut)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	return provider


@app.put("/api/providers/{provider_id}", response_model=ProviderOut)
def update_provider(provider_id: int, payload: ProviderUpdate, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	for field, value in payload.model_dump(exclude_unset=True).items():
		setattr(provider, field, value)
	try:
		db.commit()
		db.refresh(provider)
	except Exception as exc:  # noqa: BLE001
		db.rollback()
		raise HTTPException(status_code=400, detail=str(exc))
	return provider


@app.delete("/api/providers/{provider_id}")
def remove_provider(provider_id: int, db: Session = Depends(get_db)):
	provider = db.get(Provider, provider_id)
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")
	db.delete(provider)
	db.commit()
	return {"ok": True}


@app.get("/api/search")
async def api_search(article: str, db: Session = Depends(get_db)):
	return JSONResponse(await aggregate_search(article, db))


# -------------------- Aggregator --------------------

async def aggregate_search(article: str, db: Session) -> Dict[str, Any]:
	providers = db.execute(select(Provider).where(Provider.enabled == True)).scalars().all()  # noqa: E712
	results: List[Dict[str, Any]] = []
	errors: List[Dict[str, Any]] = []
	if not providers:
		return {"results": results, "errors": errors}

	async def fetch_from_provider(provider: Provider) -> None:
		url = provider.url_template.format(article=article)
		headers: Dict[str, str] = {}
		if provider.headers_json:
			try:
				headers = json.loads(provider.headers_json)
			except Exception as exc:  # noqa: BLE001
				errors.append({"provider": provider.name, "error": f"Invalid headers JSON: {exc}"})
				return
		try:
			async with httpx.AsyncClient(timeout=provider.timeout_seconds) as client:
				resp = await client.request(provider.method.upper(), url, headers=headers)
				resp.raise_for_status()
				data: Any
				try:
					data = resp.json()
				except Exception:
					data = {"text": resp.text}
				if provider.jmespath_expr:
					try:
						extracted = jmespath.search(provider.jmespath_expr, data)
						if isinstance(extracted, list):
							for item in extracted:
								if isinstance(item, dict):
									item.setdefault("provider", provider.name)
									item.setdefault("article", article)
									results.append(item)
						else:
							results.append({"provider": provider.name, "article": article, "value": extracted})
					except Exception as exc:  # noqa: BLE001
						errors.append({"provider": provider.name, "error": f"JMESPath error: {exc}"})
				else:
					results.append({"provider": provider.name, "article": article, "data": data})
		except httpx.HTTPError as exc:
			errors.append({"provider": provider.name, "error": str(exc)})

	await asyncio.gather(*(fetch_from_provider(p) for p in providers))
	return {"results": results, "errors": errors}