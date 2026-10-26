"""Tests for the optional LLM pass, with a fully mocked endpoint."""

import types

import pytest
from jargon_simplifier import llm, engine


class _FakeChoice:
    def __init__(self, content):
        self.message = types.SimpleNamespace(content=content)


class _FakeCompletion:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


def _install_endpoint(monkeypatch, content=None, exc=None):
    calls = {}

    class FakeCompletions:
        def create(self, *, model, messages, temperature):
            calls["model"] = model
            calls["messages"] = messages
            calls["temperature"] = temperature
            if exc is not None:
                raise exc
            return _FakeCompletion(content)

    class FakeOpenAI:
        def __init__(self, base_url=None, api_key=None, timeout=None):
            calls["base_url"] = base_url
            calls["api_key"] = api_key
            calls["timeout"] = timeout
            self.chat = types.SimpleNamespace(completions=FakeCompletions())

    import openai
    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)
    return calls


TEXT = "Pursuant to the lease, the lessee shall remit payment post haste."


def test_llm_pass_uses_base_url_only_and_glossary_next(monkeypatch):
    calls = _install_endpoint(monkeypatch, content="Under the lease, you must pay right away.")
    result = llm.rewrite(TEXT, base_url="http://example.local/v1", model="test-model")

    # Base-URL-only configuration: placeholder key, never a real credential.
    assert calls["base_url"] == "http://example.local/v1"
    assert calls["model"] == "test-model"
    assert calls["api_key"] == "not-required-for-local-endpoints"
    assert result.source.startswith("llm (http://example.local/v1")

    # Strict no-additions prompt is actually sent.
    system = calls["messages"][0]["content"]
    assert "STRICT NO-ADDITIONS RULES" in system
    assert "<text>" in calls["messages"][1]["content"]

    # Terms absent from the LLM output are offered in the glossary.
    terms = {e.term for e in result.edits}
    assert "pursuant to" in terms
    assert "remit" not in terms  # not in our glossary, so no fake claim


def test_llm_timeout_falls_back_to_offline(monkeypatch):
    _install_endpoint(monkeypatch, exc=TimeoutError("timed out"))
    result = llm.rewrite(TEXT)
    assert result.source == "offline"
    assert "fell back to offline engine" in result.note
    assert "under" in result.plain.lower()


def test_empty_completion_falls_back(monkeypatch):
    _install_endpoint(monkeypatch, content="   ")
    result = llm.rewrite(TEXT)
    assert result.source == "offline"
    assert "fell back" in result.note


def test_refusal_completion_falls_back(monkeypatch):
    _install_endpoint(monkeypatch, content="I'm sorry, but I cannot help with that.")
    result = llm.rewrite(TEXT)
    assert result.source == "offline"


def test_offline_flag_skips_endpoint_entirely(monkeypatch):
    import openai
    real = openai.OpenAI
    monkeypatch.setattr(openai, "OpenAI", lambda *a, **k: pytest.fail("no network call expected"))
    result = llm.rewrite(TEXT, offline=True)
    monkeypatch.setattr(openai, "OpenAI", real)
    assert result.source == "offline"
    assert not result.note.startswith("fell back")


def test_wrapped_completion_quotes_are_stripped(monkeypatch):
    _install_endpoint(monkeypatch, content='"Under the lease, you must pay right away."')
    result = llm.rewrite(TEXT)
    assert result.plain == "Under the lease, you must pay right away."


def test_user_prompt_carries_tone_and_level(monkeypatch):
    calls = _install_endpoint(monkeypatch, content="ok")
    llm.rewrite("Hi.", tone="friend", reading_level="grade-6")
    user = calls["messages"][1]["content"]
    assert "friend" in user and "grade-6" in user
