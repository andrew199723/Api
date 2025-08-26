
import os
import sys
import argparse
import urllib.request
import urllib.parse
import json


def search(article):
    city = "krasnoyarsk"
    access_token = "cNQZgrN3NzmmxUM7"
    brand_name = ""  # Можно уточнять по надобности

    url = f"https://{city}.autoleader1.ru/api/v1/search/"
    params = {
        "access-token": access_token,
        "query": article,
        "brand_name": brand_name
    }

    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url=f"{url}?{query}",
        headers={"User-Agent": "autolider-cli/1.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if data["code"] != 0:
        return []

    results = []
    for item in data["data"]:
        filtered_stocks = [
            stock for stock in item["stock_list"]
            if float(stock["quantity"]) > 0 and
               ("новая" in stock["warehouse_name"].lower() or "гайдашовка" in stock["warehouse_name"].lower())
        ]
        for stock in filtered_stocks:
            results.append({
                "source": "Autolider",
                "brand": item.get("brand_name"),
                "article": item.get("article"),
                "name": item.get("name"),
                "price": float(stock["price"]),
                "stock": float(stock["quantity"]),
                "warehouse": stock["warehouse_name"],
                "delivery": f"{stock['delivery_min']}-{stock['delivery_max']} дн."
            })
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Поиск автозапчастей через API autoleader1.ru")
    parser.add_argument("article", help="Артикул для поиска")
    parser.add_argument("--city", default="krasnoyarsk", help="Город поддомена (по умолчанию krasnoyarsk)")
    parser.add_argument("--token", default=os.getenv("AUTOLEADER_TOKEN", "cNQZgrN3NzmmxUM7"), help="Токен доступа или переменная окружения AUTOLEADER_TOKEN")
    args = parser.parse_args()

    url = f"https://{args.city}.autoleader1.ru/api/v1/search/"
    params = {
        "access-token": args.token,
        "query": args.article,
        "brand_name": ""
    }

    try:
        query = urllib.parse.urlencode(params)
        req = urllib.request.Request(
            url=f"{url}?{query}",
            headers={"User-Agent": "autolider-cli/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)
        sys.exit(2)

    if payload.get("code") != 0:
        print("Поиск не удался или нет данных")
        sys.exit(1)

    out_rows = []
    for item in payload.get("data", []):
        for stock in item.get("stock_list", []):
            if float(stock.get("quantity", 0)) <= 0:
                continue
            if not ("новая" in stock.get("warehouse_name", "").lower() or "гайдашовка" in stock.get("warehouse_name", "").lower()):
                continue
            out_rows.append([
                item.get("brand_name"),
                item.get("article"),
                item.get("name"),
                float(stock.get("price", 0)),
                float(stock.get("quantity", 0)),
                stock.get("warehouse_name"),
                f"{stock.get('delivery_min')}-{stock.get('delivery_max')} дн."
            ])

    if not out_rows:
        print("Ничего не найдено")
        sys.exit(0)

    print("brand\tarticle\tname\tprice\tstock\twarehouse\tdelivery")
    for row in out_rows:
        print("\t".join(str(x) for x in row))
