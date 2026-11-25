import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fetch_nobel import build, fetch_all, trim  # noqa: E402

PERSON = {
    "id": "745", "knownName": {"en": "A. Michael Spence", "se": "x"}, "gender": "male",
    "birth": {"date": "1943-11-07", "year": "1943",
              "place": {"city": {"en": "Montclair, NJ"}, "country": {"en": "USA"}, "cityNow": {"en": "ignored"}}},
    "wikipedia": {"slug": "x"}, "links": [{"href": "x"}],
    "nobelPrizes": [{
        "awardYear": "2001", "category": {"en": "Economic Sciences", "no": "x"}, "portion": "1/3",
        "prizeStatus": "received", "prizeAmount": 10000000, "prizeAmountAdjusted": 15547541,
        "motivation": {"en": "for their analyses", "se": "x"}, "dateAwarded": "2001-10-10",
        "affiliations": [{"name": {"en": "Stanford University"}, "city": {"en": "Stanford, CA"},
                          "country": {"en": "USA"}, "nameNow": {"en": "x"}}]}]}
ORG = {"id": "482", "orgName": {"en": "Red Cross"}, "acronym": "ICRC", "nobelPrizes": [{
    "awardYear": "1917", "category": {"en": "Peace"}, "portion": "1", "prizeStatus": "received",
    "prizeAmount": 141000, "motivation": {"en": "for work"}}]}


def test_a_person_keeps_a_small_stable_shape():
    d = trim(PERSON)
    assert d == {
        "_id": 745, "name": "A. Michael Spence", "kind": "person", "gender": "male",
        "born": {"year": 1943, "date": {"$date": "1943-11-07T00:00:00Z"}, "city": "Montclair, NJ", "country": "USA"},
        "prizes": [{"year": 2001, "category": "Economic Sciences", "shared_by": 3, "amount": 10000000,
                    "status": "received", "motivation": "for their analyses",
                    "affiliations": [{"name": "Stanford University", "city": "Stanford, CA", "country": "USA"}]}]}
    assert list(d) == ["_id", "name", "kind", "gender", "born", "prizes"]


def test_an_organisation_has_no_gender_and_no_birth_and_a_prize_with_no_affiliation_has_no_such_field():
    d = trim(ORG)
    assert d["kind"] == "organisation" and d["name"] == "Red Cross"
    assert "gender" not in d and "born" not in d
    assert "affiliations" not in d["prizes"][0] and d["prizes"][0]["shared_by"] == 1


def test_a_birth_date_with_no_month_keeps_only_the_year():
    p = {**PERSON, "birth": {"date": "1948-00-00", "year": "1948", "place": {"country": {"en": "Spain"}}}}
    assert trim(p)["born"] == {"year": 1948, "country": "Spain"}


def test_a_laureate_with_two_prizes_keeps_both_in_order():
    p = {**PERSON, "nobelPrizes": [PERSON["nobelPrizes"][0], {**ORG["nobelPrizes"][0], "awardYear": "2005"}]}
    assert [x["year"] for x in trim(p)["prizes"]] == [2001, 2005]


def test_every_page_is_fetched_until_the_count_is_reached():
    pages = {0: {"laureates": [PERSON, ORG], "meta": {"count": 3}}, 2: {"laureates": [{**ORG, "id": "9"}], "meta": {"count": 3}}}
    asked = []

    def get(url):
        asked.append(url)
        return pages[int(url.split("offset=")[1])]
    assert [x["id"] for x in fetch_all(get, page=2)] == ["745", "482", "9"]
    assert len(asked) == 2


def test_the_output_is_sorted_by_id_and_the_same_every_time():
    raw = [ORG, PERSON]
    a, b = build(raw), build(list(reversed(raw)))
    assert a == b and [json.loads(line)["_id"] for line in a.splitlines()] == [482, 745]


# ---- the committed data

FILE = ROOT / "data" / "real" / "nobel" / "laureates.jsonl"


@pytest.fixture(scope="module")
def docs():
    return [json.loads(line) for line in FILE.read_text(encoding="utf-8").splitlines()]


def test_the_committed_file_holds_every_laureate_once(docs):
    assert len(docs) == len({d["_id"] for d in docs}) >= 1000
    assert sum(1 for d in docs if d["kind"] == "organisation") == 28


def test_the_committed_file_has_only_the_trimmed_fields(docs):
    top = {"_id", "name", "kind", "gender", "born", "prizes"}
    prize = {"year", "category", "shared_by", "amount", "status", "motivation", "affiliations"}
    for d in docs:
        assert set(d) <= top and d["prizes"]
        for p in d["prizes"]:
            assert set(p) <= prize and p["shared_by"] in (1, 2, 3, 4)
            for a in p.get("affiliations", []):
                assert set(a) <= {"name", "city", "country"} and a["name"]


def test_the_data_may_be_committed_to_git():
    import subprocess
    out = subprocess.run(["git", "check-ignore", str(FILE)], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 1, "data/real/nobel must not be ignored"
