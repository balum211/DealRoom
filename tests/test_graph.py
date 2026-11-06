from dealroom.agents import verify_claim
from dealroom.graph import DealRoom


EV = {"E1": {"id": "E1", "company": "Uber", "page": 53, "text": "Revenue was $17.5 billion, or up 57% year-over-year."}}


def test_verifier_accepts_supported_claim():
    ok, _ = verify_claim({"company": "Uber", "text": "Revenue was $17.5 billion, up 57%.", "quote": "up 57% year-over-year", "evidence_id": "E1"}, EV)
    assert ok


def test_verifier_rejects_wrong_number_wrong_quote_wrong_company_unknown_id():
    assert not verify_claim({"company": "Uber", "text": "Revenue grew 250%.", "quote": "", "evidence_id": "E1"}, EV)[0]
    assert not verify_claim({"company": "Uber", "text": "x", "quote": "revenue tripled", "evidence_id": "E1"}, EV)[0]
    assert not verify_claim({"company": "Lyft", "text": "x", "quote": "", "evidence_id": "E1"}, EV)[0]
    assert not verify_claim({"company": "Uber", "text": "x", "quote": "", "evidence_id": "E9"}, EV)[0]


def test_committee_end_to_end_with_stress_test_and_human_review():
    room = DealRoom()
    cfg = room.new_thread()
    nodes = [n for n, _ in room.start("Should a growth fund prefer Uber or Lyft?", cfg, mode="offline", inject_faulty=True)]
    assert {"planner", "researcher", "quant", "bull", "bear", "rebuttal", "verifier", "revise", "judge", "writer"} <= set(nodes)
    assert room.waiting_for_review(cfg)  # graph paused for the human
    s = room.state(cfg)
    injected = [c for c in s["bull_claims"] if c["by"] == "stress test"]
    assert injected and injected[0]["status"] == "dropped"
    final = [c for c in s["bull_claims"] + s["bear_claims"] if c["status"] != "dropped"]
    assert final and all(c["status"] == "supported" for c in final)
    assert {c["company"] for c in final} == {"Uber", "Lyft"}
    assert "[E" in s["memo"] and "not investment advice" in s["memo"]
    # reviewer asks for a change, then approves
    list(room.resume({"action": "revise", "notes": "lead with cash burn"}, cfg))
    assert "lead with cash burn" in room.state(cfg)["memo"]
    list(room.resume({"action": "approve"}, cfg))
    assert room.state(cfg)["final"]


def test_guard_refuses_out_of_scope():
    s = DealRoom().run("Should I buy Tesla?", mode="offline")
    assert s["refused"] and "Tesla" in s["memo"]


def test_follow_up_reuses_thread():
    room = DealRoom()
    cfg = room.new_thread()
    list(room.start("Is Uber's path to profitability credible?", cfg, mode="offline"))
    list(room.resume({"action": "follow_up", "question": "What are Lyft's biggest risks?"}, cfg))
    s = room.state(cfg)
    assert s["question"].startswith("What are Lyft") and s["plan"]["companies"] == ["Lyft"]
