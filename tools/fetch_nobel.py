"""Fetch the Nobel Prize laureates from the official API and keep a small, stable shape of them as documents.

Source: https://api.nobelprize.org/2.1/laureates (Nobel Prize Outreach). Licence: CC0 by the API's terms of use,
https://www.nobelprize.org/about/terms-of-use-for-api-nobelprize-org-and-data-nobelprize-org/ . The result is the
data of cold sitting C (data/real/nobel/laureates.jsonl). It is committed, so run this again only to refresh it:

    uv run python tools/fetch_nobel.py

A laureate is a document with a list of prizes, and a prize may carry a list of affiliations: lists in lists.
A missing value is an absent field, as in the course's other documents."""
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://api.nobelprize.org/2.1/laureates?limit={limit}&offset={offset}"


def _en(value):
    return value.get("en") if isinstance(value, dict) else None


def _date(text):
    """'1943-11-07' as extended JSON, or None where the month or day is unknown ('1948-00-00')."""
    return {"$date": text + "T00:00:00Z"} if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", text or "") else None


def _birth(b):
    out = {"year": int((b.get("year") or b["date"][:4]))}
    date = _date(b.get("date"))
    if date:
        out["date"] = date
    place = b.get("place", {})
    for key, field in (("city", "city"), ("country", "country")):
        if _en(place.get(key)):
            out[field] = _en(place[key])
    return out


def _prize(p):
    out = {"year": int(p["awardYear"]), "category": _en(p["category"]),
           "shared_by": int(p["portion"].split("/")[1]) if "/" in p["portion"] else 1,
           "amount": p["prizeAmount"], "status": p["prizeStatus"], "motivation": _en(p.get("motivation"))}
    affiliations = []
    for a in p.get("affiliations") or []:
        item = {"name": _en(a["name"])}
        for key in ("city", "country"):
            if _en(a.get(key)):
                item[key] = _en(a[key])
        affiliations.append(item)
    if affiliations:
        out["affiliations"] = affiliations
    return out


def trim(laureate):
    """One laureate of the API as one small document."""
    org = "orgName" in laureate
    doc = {"_id": int(laureate["id"]),
           "name": _en(laureate["orgName"] if org else laureate.get("knownName") or laureate["fullName"]),
           "kind": "organisation" if org else "person"}
    if laureate.get("gender"):
        doc["gender"] = laureate["gender"]
    if "birth" in laureate:
        doc["born"] = _birth(laureate["birth"])
    doc["prizes"] = [_prize(p) for p in laureate["nobelPrizes"]]
    return doc


def fetch_all(get, page=1000):
    """Every laureate, page by page, until the count the API reports is reached. `get(url)` returns the JSON."""
    out, offset = [], 0
    while True:
        body = get(URL.format(limit=page, offset=offset))
        out += body["laureates"]
        offset += page
        if offset >= body["meta"]["count"] or not body["laureates"]:
            return out


def build(raw):
    """The file's text: one document to a line, sorted by id, the same every time."""
    docs = sorted((trim(x) for x in raw), key=lambda d: d["_id"])
    return "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs)


def _http(url):
    # the API refuses the default Python client name, so say a generic one
    req = urllib.request.Request(url, headers={"User-Agent": "course-data-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


if __name__ == "__main__":
    out = Path(__file__).parent.parent / "data" / "real" / "nobel" / "laureates.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    text = build(fetch_all(_http))
    out.write_text(text, encoding="utf-8")
    print("wrote", out, len(text.splitlines()), "laureates")
    sys.exit(0)
