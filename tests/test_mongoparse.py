from datetime import datetime, timezone

import pytest
from bson.regex import Regex

from checker.mongoparse import ParseError, forbidden_in, is_write, normalise, parse


def test_a_find_with_a_filter_and_a_projection():
    c = parse('db.orders.find({status: "delivered"}, {subtotal: 1})')
    assert (c.collection, c.method) == ("orders", "find")
    assert c.args == [{"status": "delivered"}, {"subtotal": 1}] and c.mods == []


def test_a_call_with_no_arguments():
    assert parse("db.orders.find()").args == []
    assert parse("db.orders.countDocuments()").method == "countDocuments"


def test_names_may_be_bare_quoted_dotted_or_operators():
    c = parse('db.orders.find({status: 1, "delivery.rain": true, \'a b\': 2, $or: []})')
    assert list(c.args[0]) == ["status", "delivery.rain", "a b", "$or"]


def test_values_numbers_words_lists_and_documents():
    c = parse('db.x.find({a: -5, b: 3.14, c: 1e3, d: true, e: false, f: null, g: [1, "two", {h: 3}], i: {j: {k: 0}}})')
    assert c.args[0] == {"a": -5, "b": 3.14, "c": 1000.0, "d": True, "e": False, "f": None,
                         "g": [1, "two", {"h": 3}], "i": {"j": {"k": 0}}}
    assert isinstance(c.args[0]["a"], int) and isinstance(c.args[0]["b"], float)


def test_both_quote_styles_and_escapes():
    c = parse("""db.x.find({a: "it's", b: 'say "hi"', c: "tab\\there", d: "q\\"q", e: 'S\\u00e3o'})""")
    assert c.args[0] == {"a": "it's", "b": 'say "hi"', "c": "tab\there", "d": 'q"q', "e": "São"}


def test_trailing_commas_semicolon_and_new_lines_are_fine():
    c = parse("""db.orders.aggregate([
      {$match: {status: "delivered"},},
      {$limit: 5},
    ]);
    """)
    assert c.args == [[{"$match": {"status": "delivered"}}, {"$limit": 5}]]


def test_chained_words_come_after_the_call():
    c = parse("db.orders.find({}, {subtotal: 1}).sort({subtotal: -1}).limit(5).skip(2)")
    assert c.mods == [("sort", [{"subtotal": -1}]), ("limit", [5]), ("skip", [2])]


def test_a_date_and_a_pattern():
    c = parse('db.orders.find({created_at: {$gte: ISODate("2026-08-01T10:30:00Z")}, name: /^Rest/i})')
    assert c.args[0]["created_at"]["$gte"] == datetime(2026, 8, 1, 10, 30, tzinfo=timezone.utc)
    assert c.args[0]["name"] == Regex("^Rest", "i")
    assert parse('db.x.find({d: ISODate("2026-08-01")})').args[0]["d"] == datetime(2026, 8, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize("text", [
    "SELECT 1",
    "db.orders.find(",
    "db.orders",
    "db.orders.find({status: })",
    "var x = db.orders.find()",
    "db.orders.find(); db.orders.find()",
    "db.orders.find({a: function() { return 1 }})",
    "db.orders.find({a: new Date()})",
    "db.dropDatabase()",
    "db.orders.find({a: 1}) extra",
    "db.orders.find({a: ISODate()})",
    "db.orders.find({a: ISODate(\"not a date\")})",
    'db.orders.find({a: "unterminated})',
    "",
])
def test_text_that_is_not_one_mongodb_sentence_is_refused_calmly(text):
    with pytest.raises(ParseError) as e:
        parse(text)
    assert str(e.value)


def test_spacing_and_quote_style_do_not_change_the_normal_form():
    a = normalise('db.orders.find({status: "delivered", promised_minutes: 30}, {subtotal: 1})')
    b = normalise("db.orders.find( { status:'delivered' ,promised_minutes : 30 } ,{ subtotal : 1 } );")
    c = normalise('db.orders.find({"status": "delivered", "promised_minutes": 30}, {"subtotal": 1})')
    assert a == b == c


def test_a_different_sentence_has_a_different_normal_form():
    assert normalise('db.orders.find({status: "delivered"})') != normalise('db.orders.find({status: "cancelled"})')
    assert normalise("db.orders.find().limit(5)") != normalise("db.orders.find().limit(6)")


def test_text_that_cannot_be_read_normalises_to_its_words():
    assert normalise("  not   a   sentence ") == "not a sentence"


def test_write_methods_are_known():
    assert is_write(parse('db.orders.updateOne({_id: 1}, {$set: {status: "x"}})'))
    assert is_write(parse("db.orders.deleteMany({})"))
    assert not is_write(parse("db.orders.find()"))


@pytest.mark.parametrize("value,found", [
    ({"$match": {"a": 1}}, None),
    ([{"$out": "x"}], "$out"),
    ({"a": {"b": [{"$merge": {"into": "x"}}]}}, "$merge"),
    ({"$where": "this.a == 1"}, "$where"),
    ([{"$group": {"_id": 1, "f": {"$function": {"body": "x", "args": [], "lang": "js"}}}}], "$function"),
    ({"$accumulator": {}}, "$accumulator"),
    ([{"$lookup": {"from": {"db": "admin", "coll": "x"}, "as": "y"}}], "$lookup from another database"),
    ([{"$collStats": {}}], "$collStats"),
])
def test_stages_and_words_that_write_or_run_code_are_found(value, found):
    assert forbidden_in(value) == found
