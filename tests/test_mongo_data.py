import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_mongo_data import build  # noqa: E402


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def rows(name):
    with open(ROOT / "data" / f"{name}.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("mongo")
    build(ROOT / "data", out)
    return out


def test_every_collection_is_written_and_counts_match_the_tables(built):
    assert len(read(built / "orders.jsonl")) == 6000
    assert len(read(built / "restaurants.jsonl")) == 60
    assert len(read(built / "couriers.jsonl")) == 200
    assert len(read(built / "coupons.jsonl")) == 4


def test_the_output_never_changes_between_runs(built, tmp_path):
    build(ROOT / "data", tmp_path)
    for name in ("orders", "restaurants", "couriers", "coupons"):
        assert (tmp_path / f"{name}.jsonl").read_bytes() == (built / f"{name}.jsonl").read_bytes()


def test_the_committed_files_are_what_the_generator_writes(built):
    for name in ("orders", "restaurants", "couriers", "coupons"):
        assert (ROOT / "data" / "mongo" / f"{name}.jsonl").read_bytes() == (built / f"{name}.jsonl").read_bytes()


def test_an_order_keeps_its_values_and_a_missing_cell_is_an_absent_field(built):
    by_id = {d["_id"]: d for d in read(built / "orders.jsonl")}
    for r in rows("orders"):
        d = by_id[int(r["order_id"])]
        assert d["status"] == r["status"] and d["promised_minutes"] == int(r["promised_minutes"])
        assert d["delivery_fee"] == float(r["delivery_fee"]) and d["customer_id"] == int(r["customer_id"])
        for col, key in (("subtotal", "subtotal"), ("actual_minutes", "actual_minutes"),
                         ("coupon_code", "coupon_code"), ("courier_id", "courier_id")):
            assert (key in d) == (r[col] != ""), (r["order_id"], key)


def test_dates_are_real_dates(built):
    d = read(built / "orders.jsonl")[0]
    assert d["created_at"] == {"$date": "2026-08-01T00:00:00Z"} or set(d["created_at"]) == {"$date"}
    assert set(read(built / "restaurants.jsonl")[0]["signup_date"]) == {"$date"}


def test_a_delivery_is_embedded_only_when_there_is_one(built):
    by_id = {d["_id"]: d for d in read(built / "orders.jsonl")}
    deliveries = {int(r["order_id"]): r for r in rows("deliveries")}
    assert sum(1 for d in by_id.values() if "delivery" in d) == 5601
    for oid, r in deliveries.items():
        got = by_id[oid]["delivery"]
        assert got["rain"] is (r["rain"] == "1") and got["bag_size"] == int(r["bag_size"])
        assert ("distance_km" in got) == (r["distance_km"] != "")


def test_items_add_up_to_the_subtotal_to_the_cent(built):
    for d in read(built / "orders.jsonl"):
        if "subtotal" not in d:
            assert "items" not in d
            continue
        assert 1 <= len(d["items"]) <= 4
        assert len({i["name"] for i in d["items"]}) == len(d["items"])
        assert sum(round(i["qty"] * i["price"] * 100) for i in d["items"]) == round(d["subtotal"] * 100), d["_id"]
        assert all(i["qty"] >= 1 and i["price"] > 0 for i in d["items"])


def test_item_names_belong_to_the_restaurants_cuisine(built):
    cuisine = {int(r["restaurant_id"]): r["cuisine"] for r in rows("restaurants")}
    names = {}
    for d in read(built / "orders.jsonl"):
        for i in d.get("items", []):
            names.setdefault(cuisine[d["restaurant_id"]], set()).add(i["name"])
    assert len(names) == 6 and all(len(v) >= 4 for v in names.values())
    assert not set.intersection(*names.values())  # no dish sits on every menu


def test_references_and_one_coupon_that_nobody_used(built):
    orders = read(built / "orders.jsonl")
    coupons = {d["_id"] for d in read(built / "coupons.jsonl")}
    assert {d["restaurant_id"] for d in orders} <= {d["_id"] for d in read(built / "restaurants.jsonl")}
    assert {d["coupon_code"] for d in orders if "coupon_code" in d} <= coupons
    assert coupons - {d["coupon_code"] for d in orders if "coupon_code" in d} == {"VOLTA15"}
