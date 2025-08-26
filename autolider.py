
import requests
import os

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

    response = requests.get(url, params=params)
    data = response.json()

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
