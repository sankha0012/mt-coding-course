"""One call to a chat model, over the OpenAI-style endpoints that Gemini and Groq both offer."""
import json
import os
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"

# The default model names change often. Set GEMINI_MODEL and GROQ_MODEL in .env.
PROVIDERS = {
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
               "key": "GEMINI_API_KEY", "model": "GEMINI_MODEL", "default": "gemini-2.5-flash"},
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions",
             "key": "GROQ_API_KEY", "model": "GROQ_MODEL", "default": "llama-3.3-70b-versatile"},
}


class Unavailable(Exception):
    """The provider did not answer. The message names a provider, never a key."""


def settings(env=None, env_file=ENV_FILE):
    """The .env file (KEY=VALUE lines, # comments) under the environment, which wins."""
    cfg = {}
    if env_file and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                cfg[key.removeprefix("export ").strip()] = value.strip().strip("\"'")
    cfg.update(os.environ if env is None else env)
    return cfg


def available(cfg=None):
    """The providers that have a key, for the menu."""
    cfg = settings() if cfg is None else cfg
    return [n for n, p in PROVIDERS.items() if (cfg.get(p["key"]) or "").strip()]


def chat(messages, cfg=None, urlopen=urllib.request.urlopen, timeout=30, provider=None):
    """Returns (reply, provider). The learner's chosen provider is asked and no other: a choice is a
    choice. With none chosen, the first provider that has a key."""
    cfg = settings() if cfg is None else cfg
    name = provider or next(iter(available(cfg)), None)
    p = PROVIDERS.get(name)
    key = (cfg.get(p["key"]) or "").strip() if p else ""
    if not key:
        raise Unavailable("no key set")
    body = json.dumps({"model": cfg.get(p["model"]) or p["default"], "messages": messages,
                       "temperature": 0.3, "max_tokens": 1500}).encode()
    req = urllib.request.Request(p["url"], body, {
        "Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": "mt-coding-course"})
    try:
        with urlopen(req, timeout=timeout) as r:
            text = json.load(r)["choices"][0]["message"]["content"]
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        raise Unavailable(name) from None
    if not (text and text.strip()):
        raise Unavailable(name)
    return text.strip(), name
