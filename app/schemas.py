from typing import Optional
from pydantic import BaseModel, Field


class ProviderBase(BaseModel):
	name: str = Field(min_length=1, max_length=255)
	enabled: bool = True
	method: str = Field(default="GET", pattern=r"^(GET|POST)$")
	url_template: str = Field(min_length=1)
	headers_json: Optional[str] = None
	jmespath_expr: Optional[str] = None
	timeout_seconds: int = Field(default=10, ge=1, le=120)


class ProviderCreate(ProviderBase):
	pass


class ProviderUpdate(BaseModel):
	name: Optional[str] = Field(default=None, min_length=1, max_length=255)
	enabled: Optional[bool] = None
	method: Optional[str] = Field(default=None, pattern=r"^(GET|POST)$")
	url_template: Optional[str] = None
	headers_json: Optional[str] = None
	jmespath_expr: Optional[str] = None
	timeout_seconds: Optional[int] = Field(default=None, ge=1, le=120)


class ProviderOut(ProviderBase):
	id: int

	class Config:
		from_attributes = True