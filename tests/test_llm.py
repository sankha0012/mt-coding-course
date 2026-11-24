import json
import urllib.error

import pytest

from player import llm


class Reply:
    def __init__(self, text):
        self.body = json.dumps({"choices": [{"message": {"content": text}}]}).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake(*outcomes):
    """Each call takes the next outcome: a string is a reply, an exception is raised."""
    calls = []

    def urlopen(req, timeout=None):
        calls.append(req)
        out = outcomes[len(calls) - 1]
        if isinstance(out, Exception):
            raise out
        return Reply(out)
    urlopen.calls = calls
    return urlopen


MSGS = [{"role": "user", "content": "hi"}]
BOTH = {"GEMINI_API_KEY": "gem-key", "GROQ_API_KEY": "groq-key"}


def too_many():
    return urllib.error.HTTPError("https://x", 429, "Too Many Requests", {}, None)


def test_the_chosen_provider_is_asked():
    u = fake("from groq")
    assert llm.chat(MSGS, BOTH, u, provider="groq") == ("from groq", "groq")
    assert "groq.com" in u.calls[0].full_url
    u = fake("from gemini")
    assert llm.chat(MSGS, BOTH, u, provider="gemini") == ("from gemini", "gemini")
    assert "generativelanguage" in u.calls[0].full_url


def test_a_chosen_provider_that_fails_is_not_swapped_for_the_other():
    u = fake(too_many())
    with pytest.raises(llm.Unavailable):
        llm.chat(MSGS, BOTH, u, provider="groq")
    assert len(u.calls) == 1


def test_a_chosen_provider_without_a_key_makes_no_call():
    u = fake()
    with pytest.raises(llm.Unavailable, match="no key set"):
        llm.chat(MSGS, {"GEMINI_API_KEY": "gem-key"}, u, provider="groq")
    assert u.calls == []


def test_without_a_choice_the_first_provider_with_a_key_is_used():
    u = fake("from gemini")
    assert llm.chat(MSGS, BOTH, u)[1] == "gemini"
    u = fake("from groq")
    assert llm.chat(MSGS, {"GROQ_API_KEY": "groq-key"}, u)[1] == "groq"


def test_available_lists_the_providers_that_have_a_key():
    assert llm.available(BOTH) == ["gemini", "groq"]
    assert llm.available({"GROQ_API_KEY": "k"}) == ["groq"]
    assert llm.available({"GEMINI_API_KEY": "  "}) == []


def test_the_request_carries_the_key_the_model_and_the_messages():
    u = fake("ok")
    llm.chat(MSGS, {**BOTH, "GEMINI_MODEL": "my-model"}, u, provider="gemini")
    req = u.calls[0]
    assert req.get_header("Authorization") == "Bearer gem-key"
    body = json.loads(req.data)
    assert body["model"] == "my-model" and body["messages"] == MSGS
    assert "gem-key" not in req.data.decode()


def test_an_empty_reply_counts_as_a_failure():
    with pytest.raises(llm.Unavailable):
        llm.chat(MSGS, BOTH, fake("  "), provider="gemini")


def test_a_failure_does_not_name_a_key():
    with pytest.raises(llm.Unavailable) as e:
        llm.chat(MSGS, BOTH, fake(OSError("down")), provider="gemini")
    assert "gem-key" not in str(e.value) and "groq-key" not in str(e.value)


def test_no_key_makes_no_call():
    u = fake()
    with pytest.raises(llm.Unavailable, match="no key set"):
        llm.chat(MSGS, {}, u)
    assert u.calls == []


def test_settings_read_the_env_file_and_the_environment_wins(tmp_path):
    f = tmp_path / ".env"
    f.write_text("# comment\nGEMINI_API_KEY=from-file\nexport GROQ_API_KEY='quoted'\n\nGEMINI_MODEL = m\n")
    cfg = llm.settings({"GEMINI_API_KEY": "from-env"}, f)
    assert cfg["GEMINI_API_KEY"] == "from-env"
    assert cfg["GROQ_API_KEY"] == "quoted" and cfg["GEMINI_MODEL"] == "m"


def test_settings_without_a_file(tmp_path):
    assert llm.settings({"A": "1"}, tmp_path / "missing") == {"A": "1"}


def test_a_failure_says_why_without_a_key():
    with pytest.raises(llm.Unavailable, match=r"gemini: HTTPError 429"):
        llm.chat(MSGS, BOTH, fake(too_many()), provider="gemini")
    with pytest.raises(llm.Unavailable, match=r"gemini: empty reply"):
        llm.chat(MSGS, BOTH, fake(" "), provider="gemini")
