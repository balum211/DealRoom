"""LLM-mode agents with a fake chat model: JSON parsing, citation checks and fallbacks."""
import json

import pytest

from dealroom import agents, config
from dealroom.llm import parse_json


def test_parse_json_tolerates_fences_and_chatter():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Sure! Here it is: {"claims": []} hope that helps') == {"claims": []}


@pytest.fixture
def fake_llm(monkeypatch):
    replies = {}

    def fake_chat(system, user, temperature=0.2):
        for key, reply in replies.items():
            if key in system:
                return reply
        raise RuntimeError("no fake reply")

    import dealroom.llm as llm_mod

    monkeypatch.setattr(llm_mod, "chat", fake_chat)
    monkeypatch.setattr(config, "llm_enabled", lambda mode=None: True)
    return replies


def _state():
    ev = [{"id": "E1", "company": "Uber", "page": 53, "item": "7", "item_title": "MD&A", "topic": "growth",
           "text": "Revenue was $17.5 billion, or up 57% year-over-year.", "score": 0.9}]
    return {"question": "Uber growth?", "evidence": ev, "plan": {"companies": ["Uber"]}, "profile": {"mandate": "growth"}}


def test_llm_claims_are_verified_and_bad_ones_rejected(fake_llm):
    fake_llm["Bull analyst"] = json.dumps({"claims": [
        {"company": "Uber", "text": "Revenue rose 57% to $17.5 billion.", "evidence_id": "E1", "quote": "up 57% year-over-year"},
        {"company": "Uber", "text": "Revenue rose 99%.", "evidence_id": "E1", "quote": "up 99%"}]})
    fake_llm["fact-checker"] = json.dumps({"results": [{"id": "B1", "supported": True}]})
    state = _state()
    state.update(agents.bull(state))
    state["bear_claims"] = []
    out = agents.verifier(state)
    statuses = [c["status"] for c in out["bull_claims"]]
    assert statuses == ["supported", "unsupported"]
    assert all(c["by"] == "llm" for c in out["bull_claims"])


def test_llm_failure_falls_back_to_offline(fake_llm):
    state = _state()
    out = agents.bear(state)  # no fake reply registered for the Bear -> exception -> offline
    assert "offline" in out["trace"][0]["summary"]
