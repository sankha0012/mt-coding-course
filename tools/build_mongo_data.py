"""Build the MongoDB practice data, data/mongo/*.jsonl, from the CSV tables in data/.

The same orders, restaurants, couriers and coupons, reshaped as documents: an order carries its delivery
inside it, and a list of items that adds up to its subtotal to the cent. The seed is fixed, so the output is
the same on every run and is committed. Run it again only to change the shape:

    uv run python tools/build_mongo_data.py

Dates are written as extended JSON ({"$date": ...}), which bson.json_util and mongoimport both read."""
import csv
import json
import random
import sys
from pathlib import Path

SEED = 20261125
MENUS = {  # a dish and its usual price in cents
    "pizza": [("Margherita", 3200), ("Calabresa", 3600), ("Portuguesa", 3800), ("Quatro queijos", 4200), ("Guaraná", 800)],
    "japonesa": [("Combo sushi", 5200), ("Temaki de salmão", 2800), ("Yakisoba", 3400), ("Gyoza", 2200), ("Missoshiro", 1400)],
    "hamburguer": [("Clássico", 2800), ("Cheese bacon", 3400), ("Batata frita", 1600), ("Milkshake", 1800), ("Refrigerante", 700)],
    "brasileira": [("Feijoada", 4200), ("Prato feito", 2600), ("Moqueca", 5200), ("Pastel", 900), ("Suco de caju", 800)],
    "saudavel": [("Salada Caesar", 2800), ("Bowl de açaí", 2200), ("Wrap de frango", 2600), ("Suco verde", 1200), ("Quinoa", 3000)],
    "arabe": [("Esfiha", 800), ("Kibe", 900), ("Shawarma", 2800), ("Falafel", 2400), ("Homus", 1800)],
}


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _date(text):
    """'2026-08-01 01:08:00' or '2025-07-16' as extended JSON."""
    day, _, clock = text.partition(" ")
    return {"$date": f"{day}T{clock or '00:00:00'}Z"}


def _int(text):
    return int(float(text))


def _items(rng, menu, cents):
    """Up to four distinct dishes whose quantities and prices add up to `cents` exactly. Dishes are added at
    their usual price until what is left is about one dish. That last dish takes what is left, once, so the
    sum is exact and no price is zero."""
    pool = rng.sample(menu, len(menu))
    items, total = [], 0
    for name, base in pool[:3]:
        left = cents - total
        if items and left <= base * 1.6:
            break
        price, qty = round(base * rng.uniform(0.85, 1.15)), rng.randint(1, 2)
        if total + price * qty > cents - 100:
            break
        items.append({"name": name, "qty": qty, "price": price / 100})
        total += price * qty
    items.append({"name": pool[len(items)][0], "qty": 1, "price": (cents - total) / 100})
    return items


def _order(r, delivery, cuisine, rng):
    d = {"_id": _int(r["order_id"]), "customer_id": _int(r["customer_id"]), "restaurant_id": _int(r["restaurant_id"])}
    if r["courier_id"]:
        d["courier_id"] = _int(r["courier_id"])
    d["created_at"] = _date(r["created_at"])
    d["status"] = r["status"]
    if r["subtotal"]:
        d["subtotal"] = float(r["subtotal"])
    d["delivery_fee"] = float(r["delivery_fee"])
    if r["coupon_code"]:
        d["coupon_code"] = r["coupon_code"]
    d["promised_minutes"] = _int(r["promised_minutes"])
    if r["actual_minutes"]:
        d["actual_minutes"] = float(r["actual_minutes"])
    if delivery:
        d["delivery"] = {}
        if delivery["distance_km"]:
            d["delivery"]["distance_km"] = float(delivery["distance_km"])
        d["delivery"]["rain"] = delivery["rain"] == "1"
        d["delivery"]["bag_size"] = _int(delivery["bag_size"])
    if r["subtotal"]:
        d["items"] = _items(rng, MENUS[cuisine], round(float(r["subtotal"]) * 100))
    return d


def _write(path, docs):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def build(src, out, seed=SEED):
    src, out = Path(src), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    restaurants = _read(src / "restaurants.csv")
    cuisine = {_int(r["restaurant_id"]): r["cuisine"] for r in restaurants}
    deliveries = {_int(r["order_id"]): r for r in _read(src / "deliveries.csv")}
    orders = sorted(_read(src / "orders.csv"), key=lambda r: _int(r["order_id"]))
    _write(out / "orders.jsonl", [_order(r, deliveries.get(_int(r["order_id"])), cuisine[_int(r["restaurant_id"])], rng)
                                 for r in orders])
    _write(out / "restaurants.jsonl", [
        {"_id": _int(r["restaurant_id"]), "name": r["name"], "city": r["city"], "cuisine": r["cuisine"],
         "signup_date": _date(r["signup_date"])} for r in restaurants])
    _write(out / "couriers.jsonl", [
        {"_id": _int(r["courier_id"]), "vehicle": r["vehicle"], "city": r["city"]} for r in _read(src / "couriers.csv")])
    _write(out / "coupons.jsonl", [
        {"_id": r["coupon_code"], "discount_pct": _int(r["discount_pct"])} for r in _read(src / "coupons.csv")])


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    build(root / "data", root / "data" / "mongo")
    print("wrote", *sorted(p.name for p in (root / "data" / "mongo").glob("*.jsonl")))
    sys.exit(0)
