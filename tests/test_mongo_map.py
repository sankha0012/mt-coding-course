import re
from pathlib import Path

import pytest

from checker import mongo

ROOT = Path(__file__).parent.parent
needs_mongod = pytest.mark.skipif(not mongo.available(), reason="mongod is not installed here")

# the document counts the map quotes for its eight closing sentences, in the order they appear
QUOTED = [142, 5, 5, 5, 4, 1, 1475, 3]


def sentences():
    text = (ROOT / "docs" / "maps" / "mongodb.md").read_text(encoding="utf-8")
    return re.findall(r"```js\n(.*?)\n```", text, re.S)


def test_the_map_still_has_its_eight_closing_sentences():
    assert len(sentences()) == len(QUOTED)


@needs_mongod
@pytest.mark.parametrize("n", range(len(QUOTED)))
def test_every_closing_sentence_of_the_map_is_read_and_run_as_quoted(n):
    server = mongo.server_for(ROOT / "data")
    r = mongo.run_mongo(server, "mongo", sentences()[n])
    assert r.error is None
    assert r.total == QUOTED[n]


@needs_mongod
def test_the_map_quotes_the_right_values():
    server = mongo.server_for(ROOT / "data")
    s = sentences()
    pipeline = mongo.run_mongo(server, "mongo", s[2])
    assert sorted(v for _, v in pipeline.full) == [108, 109, 109, 112, 113]
    dishes = mongo.run_mongo(server, "mongo", s[3])
    assert sorted(x[1] for x in dishes.full) == [695, 723, 744, 748, 753]
    assert mongo.run_mongo(server, "mongo", s[5]).full == [("VOLTA15", 15)]
    months = mongo.run_mongo(server, "mongo", s[7])
    assert sorted(months.full) == [("2026-08", 1929, 802), ("2026-09", 1813, 776), ("2026-10", 1859, 808)]
