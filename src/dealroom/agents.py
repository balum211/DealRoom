"""The DealRoom agents. Each node reads and writes the shared LangGraph state.

Every agent has two implementations:
* LLM mode (no API key): the free open-weights model (GPT-OSS 20B) writes the memo; set DR_LLM_AGENTS=all to let it
  plan, argue and check too (needs an endpoint without the free tier's one-reply-per-45-seconds limit).
* Offline mode: deterministic, extractive agents that need no key. The demo, the tests and
  CI all run end to end with no API cost, and LLM failures fall back to these.
"""
from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from filingsight.chunking import split_units

from . import config, prompts
from .guardrails import check_input, check_output
from .memory import MemoryStore
from .metrics import extract_metrics, fmt_value
from .tools import search_filings

TOPICS = (
    ("growth", "revenue growth, demand recovery and gross bookings"),
    ("profitability", "net loss, adjusted EBITDA and the path to profitability"),
    ("cash", "cash flow from operations, liquidity and cash and cash equivalents"),
    ("risks", "key risk factors including driver classification, regulation and competition"),
    ("strategy", "strategy, new products and growth initiatives"),
)

_POS = re.compile(r"\b(increas\w*|grew|growth|improv\w*|record|all-time high|recover\w*|expan\w*|profitab\w*|positive|"
                  r"strong\w*|gain\w*|accelerat\w*|leading|largest|momentum|efficien\w*|benefit\w*|higher)\b", re.I)
_NEG = re.compile(r"\b(net loss\w*|loss(es)?|declin\w*|decreas\w*|risk\w*|competiti\w*|regulat\w*|classif\w*|litigation|"
                  r"advers\w*|uncertain\w*|may not|unable|impair\w*|lawsuits?|fines?|penalt\w*|harm\w*|dilut\w*|"
                  r"volatil\w*|covid\w*|pandemic|lower|insufficient|negative\w*|down from|down \d+)\b", re.I)
_HEDGE = re.compile(r"\b(fail\w*|prevent\w*|could|might|may|if we|unable|cannot|no assurance)\b", re.I)
_BEAR_BOOST = re.compile(r"(incurred (significant )?(net )?losses|history of (net )?losses|accumulated deficit|"
                         r"classification of drivers|highly competitive|intense(ly)? competit\w*|not achieve profitab\w*|"
                         r"substantial doubt|significant penalties|reclassif\w*)", re.I)
_JUNK = re.compile(r"(for more information|see (the )?(section|note|part|item)|refer to|incorporated (herein )?by reference|"
                   r"forward-looking statements|table of contents)", re.I)
_CONNECTOR = re.compile(r"^(further|additionally|in addition|however|accordingly|as a result|these|this|such|also|moreover)\b", re.I)
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
_FAULTY_TEXT = "Revenue grew 250% in 2021 to $45 billion, so the company is already highly profitable."


# ---------------------------------------------------------------- helpers
def _use_llm(state: dict, agent: str = "") -> bool:
    return config.llm_enabled(state.get("mode")) and config.agent_uses_llm(agent)


def _trace(node: str, summary: str, t0: float, **extra) -> dict:
    from .llm import take_usage

    entry = {"node": node, "summary": summary, "ms": round((time.perf_counter() - t0) * 1000), **take_usage(), **extra}
    return {"trace": [entry]}


def _norm(text: str) -> str:
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def _evidence_map(state: dict) -> dict[str, dict]:
    return {e["id"]: e for e in state.get("evidence", [])}


def _format_evidence(evidence: list[dict], max_chars: int = 900) -> str:
    return "\n\n".join(
        f"[{e['id']}] {e['company']} | Item {e['item']} {e['item_title']} | p.{e['page']}\n{e['text'][:max_chars]}"
        for e in evidence
    )


def _companies(state: dict) -> list[str]:
    return state.get("plan", {}).get("companies") or list(config.COMPANIES)


def _short(text: str, n: int = 140) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------- guard
def input_guard(state: dict) -> dict:
    t0 = time.perf_counter()
    result = check_input(state.get("question", ""))
    store = MemoryStore()
    user = store.get_user(state.get("user_id", "default"))
    update = {"guard": result, "refused": not result["allowed"], "refusal_reason": result["reason"],
              "profile": {**user["profile"], **(state.get("profile") or {})}, "past_memos": user["memos"][-3:],
              "attempts": 0, "review": {}, "final": False}
    summary = "Request allowed" if result["allowed"] else f"Blocked: {result['reason']}"
    if result["notes"]:
        summary += " · " + " ".join(result["notes"])
    return {**update, **_trace("guard", summary, t0)}


# ---------------------------------------------------------------- planner
def _offline_plan(question: str, companies: list[str]) -> list[dict]:
    topics = []
    for key, desc in TOPICS[: config.MAX_TOPICS]:
        for c in companies:
            topics.append({"topic": key, "company": c, "question": f"{c} {desc}"})
    focus = re.sub(r"\b(uber|lyft|or|and|vs\.?|versus|compare|should|a|the|based on|their|10-?ks?|filings?)\b", " ", question, flags=re.I)
    if len(re.findall(r"[a-z]{4,}", focus, re.I)) >= 2:
        for c in companies:
            topics.append({"topic": "your question", "company": c, "question": f"{c}: {question}"})
    return topics


def planner(state: dict) -> dict:
    t0 = time.perf_counter()
    from .tools import get_index

    get_index()  # warm the index once before the parallel agents start
    q = state["question"]
    named = [c for c in config.COMPANIES if re.search(rf"\b{c}\b", q, re.I)]
    companies = named or list(config.COMPANIES)
    topics, how = None, "offline"
    if _use_llm(state, "planner"):
        try:
            data = prompts_call_planner(q, companies)
            topics = [t for t in data if t.get("company") in companies and t.get("question")][: 2 * config.MAX_TOPICS + 2]
            how = "llm"
        except Exception as exc:  # fall back, never crash the run
            how = f"offline (LLM failed: {type(exc).__name__})"
    if not topics:
        topics = _offline_plan(q, companies)
    for i, t in enumerate(topics, 1):
        t["id"] = f"T{i}"
    plan = {"companies": companies, "is_comparison": len(companies) > 1, "topics": topics}
    return {"plan": plan, **_trace("planner", f"{len(topics)} sub-questions across {', '.join(companies)} [{how}]", t0)}


def prompts_call_planner(question: str, companies: list[str]) -> list[dict]:
    from .llm import chat_json

    system = prompts.PLANNER_SYSTEM.format(companies=", ".join(companies), n=min(8, 4 * len(companies)))
    data = chat_json(system, f"Request: {question}")
    return data.get("topics", []) if isinstance(data, dict) else data


# ---------------------------------------------------------------- researcher
def researcher(state: dict) -> dict:
    t0 = time.perf_counter()
    topics = state["plan"]["topics"]

    via = "in-process tools"
    results = None
    if state.get("via_mcp", config.RESEARCH_VIA_MCP):
        try:
            from .tools import search_many_via_mcp

            reqs = [{"query": t["question"], "company": t["company"], "k": config.EVIDENCE_PER_TOPIC, "topic": t["topic"]}
                    for t in topics]
            results = list(zip(topics, search_many_via_mcp(reqs)))
            via = "MCP server"
        except Exception as exc:
            via = f"in-process tools (MCP failed: {type(exc).__name__})"
    if results is None:
        def run(t):
            return t, search_filings(t["question"], company=t["company"], k=config.EVIDENCE_PER_TOPIC, topic=t["topic"])

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(run, topics))
    results, retried = _research_again(state, results)
    evidence, seen = [], set()
    for _, hits in results:
        for e in hits:
            if e["chunk_id"] in seen:
                continue
            seen.add(e["chunk_id"])
            e["id"] = f"E{len(evidence) + 1}"
            evidence.append(e)
    pages = len({(e["company"], e["page"]) for e in evidence})
    again = f" · {retried} weak result(s) re-searched with a reformulated query" if retried else ""
    return {"evidence": evidence,
            **_trace("researcher", f"{len(topics)} searches via {via}{again} · {len(evidence)} passages from {pages} filing pages",
                     t0, research_retries=retried)}


_STOP = re.compile(r"\b(what|which|how|why|is|are|was|were|do|does|did|the|a|an|of|to|in|on|for|and|or|its|their|based|"
                   r"should|would|could|fund|prefer|vs\.?|versus|10-?ks?|fy\s?2021|compare|between)\b", re.I)


def _reformulate(t: dict, state: dict) -> str:
    """Rewrite a sub-question whose first search came back weak (agentic RAG: decide to search again)."""
    if _use_llm(state, "researcher"):
        try:
            from .llm import chat

            q = chat(prompts.REFORMULATE_SYSTEM, f"Company: {t['company']}\nSub-question: {t['question']}", temperature=0.0)
            q = q.strip().strip('"').splitlines()[0]
            if 3 <= len(q) <= 300:
                return q
        except Exception:
            pass
    hint = dict(TOPICS).get(t.get("topic", ""), "")
    keywords = " ".join(w for w in _STOP.sub(" ", t["question"]).split() if len(w) > 2)
    return f"{t['company']} 10-K {keywords} {hint}".strip()


def _research_again(state: dict, results: list) -> tuple[list, int]:
    """Re-search any sub-question with too few hits or a low top score, then keep the best passages."""
    weak = [i for i, (_, hits) in enumerate(results)
            if len(hits) < config.RESEARCH_RETRY_MIN_HITS or max((e["score"] for e in hits), default=0) < config.RESEARCH_RETRY_MIN_SCORE]
    results = list(results)
    for i in weak:
        t, hits = results[i]
        more = search_filings(_reformulate(t, state), company=t["company"], k=config.EVIDENCE_PER_TOPIC, topic=t["topic"])
        merged = {e["chunk_id"]: e for e in hits + more}
        results[i] = (t, sorted(merged.values(), key=lambda e: -e["score"])[: config.EVIDENCE_PER_TOPIC])
    return results, len(weak)


# ---------------------------------------------------------------- quant
def quant(state: dict) -> dict:
    t0 = time.perf_counter()
    metrics = extract_metrics(_companies(state))
    return {"metrics": metrics, **_trace("quant", f"{len(metrics)} metrics read from filing tables with YoY change", t0)}


# ---------------------------------------------------------------- claims (bull / bear)
def _side_score(sentence: str, side: str, item: str = "") -> float:
    pos, neg = len(_POS.findall(sentence)), len(_NEG.findall(sentence))
    if neg:  # hedges ("may", "could") only count when the sentence names a real downside
        neg += 0.5 * len(_HEDGE.findall(sentence))
    elif side == "bull" and _HEDGE.search(sentence):
        pos -= 1
    if side == "bull":
        if item == "1A":  # risk factors are never the bull case
            return 0.0
        score = pos - 1.5 * neg
    else:
        score = neg - 1.5 * pos + (2.0 if _BEAR_BOOST.search(sentence) else 0.0)
    if score <= 0:
        return 0.0
    score += 1.5 if re.search(r"\d\s?%|\$\s?\d", sentence) else (0.5 if _NUMBER.search(sentence) else 0.0)
    score -= 0.75 if _CONNECTOR.search(sentence) else 0.0
    return max(score, 0.0)


def _candidates(evidence: list[dict], side: str) -> list[dict]:
    out = []
    for e in evidence:
        for s in split_units(e["text"]):
            s = s.strip()
            if (not (60 <= len(s) <= 380) or "|" in s or s.endswith((":", ";")) or s.startswith(("•", "-", "("))
                    or _JUNK.search(s)):
                continue
            score = _side_score(s, side, e.get("item", ""))
            if score > 0:
                out.append({"score": score + e["score"] * 0.5, "sentence": s, "evidence": e})
    out.sort(key=lambda c: -c["score"])
    return out


def _pick_offline(state: dict, side: str, n: int, exclude: set[str] | None = None) -> list[dict]:
    exclude = exclude or set()
    companies = _companies(state)
    pools = {c: [x for x in _candidates(state.get("evidence", []), side) if x["evidence"]["company"] == c] for c in companies}
    picked, used_topics = [], set()
    while len(picked) < n and any(pools.values()):
        for c in companies:
            pool = pools[c]
            # prefer a topic this company has not used yet, then anything left
            idx = next((i for i, x in enumerate(pool) if (c, x["evidence"]["topic"]) not in used_topics
                        and _norm(x["sentence"]) not in exclude), None)
            if idx is None:
                idx = next((i for i, x in enumerate(pool) if _norm(x["sentence"]) not in exclude), None)
            if idx is None:
                pools[c] = []
                continue
            x = pool.pop(idx)
            exclude.add(_norm(x["sentence"]))
            used_topics.add((c, x["evidence"]["topic"]))
            picked.append(x)
            if len(picked) >= n:
                break
    prefix = "B" if side == "bull" else "R"
    return [{
        "id": f"{prefix}{i}", "side": side, "company": x["evidence"]["company"], "topic": x["evidence"]["topic"],
        "text": x["sentence"], "quote": x["sentence"], "evidence_id": x["evidence"]["id"], "status": "pending",
        "by": "offline",
    } for i, x in enumerate(picked, 1)]


def _llm_claims(state: dict, side: str, n: int) -> list[dict]:
    from .llm import chat_json

    companies = _companies(state)
    balance = (f"Cover every company ({', '.join(companies)}) with at least one claim each."
               if len(companies) > 1 else f"All claims are about {companies[0]}.")
    system = prompts.CLAIMS_SYSTEM.format(
        side_title="Bull" if side == "bull" else "Bear", n=n, balance=balance,
        side_desc="pro-investment (growth, improving economics, strengths)" if side == "bull"
        else "anti-investment (losses, risks, competition, regulation, weaknesses)")
    profile = state.get("profile", {})
    user = (f"Request: {state['question']}\nReviewer mandate: {profile.get('mandate')}\n\n"
            f"Evidence:\n{_format_evidence(state['evidence'])}")
    data = chat_json(system, user, temperature=0.3)
    claims = data.get("claims", []) if isinstance(data, dict) else data
    prefix = "B" if side == "bull" else "R"
    return [{
        "id": f"{prefix}{i}", "side": side, "company": c.get("company", ""), "topic": "",
        "text": c.get("text", "").strip(), "quote": c.get("quote", "").strip(), "evidence_id": c.get("evidence_id", "").strip(" []"),
        "status": "pending", "by": "llm",
    } for i, c in enumerate(claims[:n], 1) if c.get("text")]


def _make_claims(state: dict, side: str) -> tuple[list[dict], str]:
    n = config.CLAIMS_PER_SIDE
    if _use_llm(state, "debaters"):
        try:
            claims = _llm_claims(state, side, n)
            if claims:
                return claims, "llm"
        except Exception as exc:
            return _pick_offline(state, side, n), f"offline (LLM failed: {type(exc).__name__})"
    return _pick_offline(state, side, n), "offline"


def _faulty_claim(state: dict) -> dict:
    company = _companies(state)[0]
    ev = next((e for e in state.get("evidence", []) if e["company"] == company), state["evidence"][0])
    return {"id": "B0", "side": "bull", "company": company, "topic": "stress test", "text": _FAULTY_TEXT,
            "quote": "revenue grew 250% in 2021", "evidence_id": ev["id"], "status": "pending", "by": "stress test"}


def bull(state: dict) -> dict:
    t0 = time.perf_counter()
    claims, how = _make_claims(state, "bull")
    if state.get("inject_faulty"):
        claims = [_faulty_claim(state)] + claims
    return {"bull_claims": claims, **_trace("bull", f"{len(claims)} claims for investing [{how}]", t0)}


def bear(state: dict) -> dict:
    t0 = time.perf_counter()
    claims, how = _make_claims(state, "bear")
    return {"bear_claims": claims, **_trace("bear", f"{len(claims)} claims against investing [{how}]", t0)}


# ---------------------------------------------------------------- rebuttal
def rebuttal(state: dict) -> dict:
    t0 = time.perf_counter()
    bulls, bears = state.get("bull_claims", []), state.get("bear_claims", [])
    how = "offline"
    result = None
    if _use_llm(state, "rebuttal") and bulls and bears:
        try:
            from .llm import chat_json

            ids = {c["evidence_id"] for c in bulls + bears}
            ev = [e for e in state["evidence"] if e["id"] in ids]
            user = ("Bull claims:\n" + json.dumps(bulls, indent=1) + "\n\nBear claims:\n" + json.dumps(bears, indent=1)
                    + "\n\nEvidence:\n" + _format_evidence(ev, 600))
            data = chat_json(prompts.REBUTTAL_SYSTEM, user, temperature=0.4)
            result = {"bear_rebuttal": data["bear_rebuttal"], "bull_response": data["bull_response"]}
            how = "llm"
        except Exception as exc:
            how = f"offline (LLM failed: {type(exc).__name__})"
    if result is None:
        real_bulls = [b for b in bulls if b["by"] != "stress test"] or bulls
        if not (real_bulls and bears):
            result = {"bear_rebuttal": "", "bull_response": ""}
        else:
            b1 = real_bulls[0]
            r1 = next((r for r in bears if r["company"] == b1["company"]), bears[0])
            b2 = next((b for b in real_bulls[1:] if b["company"] == r1["company"]), real_bulls[-1])
            result = {
                "bear_rebuttal": (f"The Bull leans on \"{_short(b1['quote'])}\" [{b1['evidence_id']}], but the same filing "
                                  f"warns: \"{_short(r1['quote'])}\" [{r1['evidence_id']}]."),
                "bull_response": (f"Those risks are disclosed, yet the filing also shows: \"{_short(b2['quote'])}\" "
                                  f"[{b2['evidence_id']}]."),
            }
    return {"rebuttal": result, **_trace("rebuttal", f"one rebuttal round [{how}]", t0)}


# ---------------------------------------------------------------- verifier
def verify_claim(claim: dict, evidence: dict[str, dict]) -> tuple[bool, str]:
    ev = evidence.get(claim.get("evidence_id", ""))
    if not ev:
        return False, f"cites unknown evidence '{claim.get('evidence_id')}'"
    if claim.get("company") and claim["company"] != ev["company"]:
        return False, f"claim is about {claim['company']} but the source is {ev['company']}'s filing"
    source = _norm(ev["text"])
    quote = _norm(claim.get("quote", ""))
    if quote and quote not in source:
        return False, "quoted words do not appear on the cited page"
    digits_src = source.replace(",", "")
    for num in _NUMBER.findall(claim.get("text", "")):
        n = num.replace(",", "").rstrip(".")
        if len(n) >= 2 and n not in digits_src:
            return False, f"number {num} is not in the cited source"
    return True, f"supported by {ev['company']} 10-K p.{ev['page']}"


def verifier(state: dict) -> dict:
    t0 = time.perf_counter()
    ev = _evidence_map(state)
    bulls = [dict(c) for c in state.get("bull_claims", [])]
    bears = [dict(c) for c in state.get("bear_claims", [])]
    pending = [c for c in bulls + bears if c["status"] == "pending"]
    for c in pending:
        ok, reason = verify_claim(c, ev)
        c["status"], c["reason"] = ("supported" if ok else "unsupported"), reason
    how = "rules"
    llm_checked = [c for c in pending if c["status"] == "supported" and c["by"] == "llm"]
    if llm_checked and _use_llm(state, "verifier"):
        try:
            from .llm import chat_json

            payload = [{"id": c["id"], "claim": c["text"], "evidence": ev[c["evidence_id"]]["text"][:900]} for c in llm_checked]
            data = chat_json(prompts.VERIFIER_SYSTEM, json.dumps(payload, indent=1), temperature=0.0)
            verdicts = {r["id"]: r for r in data.get("results", [])}
            for c in llm_checked:
                v = verdicts.get(c["id"])
                if v and not v.get("supported", True):
                    c["status"], c["reason"] = "unsupported", f"LLM judge: {v.get('reason', 'not supported')}"
            how = "rules + LLM judge"
        except Exception as exc:
            how = f"rules (LLM judge failed: {type(exc).__name__})"
    failed = [c for c in bulls + bears if c["status"] == "unsupported"]
    ok = sum(c["status"] == "supported" for c in bulls + bears)
    summary = f"{ok} supported, {len(failed)} unsupported [{how}]"
    if failed:
        summary += " · " + "; ".join(f"{c['id']}: {c['reason']}" for c in failed[:3])
    return {"bull_claims": bulls, "bear_claims": bears, **_trace("verifier", summary, t0, failed=len(failed))}


def after_verifier(state: dict) -> str:
    failed = any(c["status"] == "unsupported" for c in state.get("bull_claims", []) + state.get("bear_claims", []))
    if failed and state.get("attempts", 0) < config.MAX_VERIFY_RETRIES:
        return "revise"
    return "judge"


def revise(state: dict) -> dict:
    """Send rejected claims back to their author (Bull or Bear) for a supported replacement."""
    t0 = time.perf_counter()
    attempt = state.get("attempts", 0) + 1
    out: dict[str, Any] = {"attempts": attempt}
    replaced = 0
    for side, key in (("bull", "bull_claims"), ("bear", "bear_claims")):
        claims = [dict(c) for c in state.get(key, [])]
        failed = [c for c in claims if c["status"] == "unsupported"]
        if not failed:
            continue
        keep = [c for c in claims if c["status"] != "unsupported"]
        new: list[dict] = []
        if _use_llm(state, "debaters") and any(c["by"] == "llm" for c in failed):
            try:
                from .llm import chat_json

                system = prompts.REVISE_SYSTEM.format(side_title="Bull" if side == "bull" else "Bear")
                user = ("Rejected claims:\n" + json.dumps([{k: c[k] for k in ("company", "text", "evidence_id", "quote", "reason")}
                                                          for c in failed], indent=1)
                        + "\n\nEvidence:\n" + _format_evidence(state["evidence"]))
                data = chat_json(system, user, temperature=0.2)
                new = [{"side": side, "company": c.get("company", ""), "topic": "", "text": c.get("text", ""),
                        "quote": c.get("quote", ""), "evidence_id": c.get("evidence_id", "").strip(" []"),
                        "status": "pending", "by": "llm"} for c in data.get("claims", [])[: len(failed)]]
            except Exception:
                new = []
        if not new:
            exclude = {_norm(c["quote"]) for c in claims}
            new = _pick_offline(state, side, len(failed), exclude=exclude)
            for c in new:
                c["by"] = "offline (revised)"
        prefix = "B" if side == "bull" else "R"
        start = max([int(re.sub(r"\D", "", c["id"]) or 0) for c in claims] + [0]) + 1
        for i, c in enumerate(new):
            c["id"] = f"{prefix}{start + i}"
            c["revision_of"] = failed[min(i, len(failed) - 1)]["id"]
        replaced += len(new)
        dropped = [{**c, "status": "dropped"} for c in failed]
        out[key] = keep + new + dropped
    return {**out, **_trace("revise", f"retry {attempt}/{config.MAX_VERIFY_RETRIES}: {replaced} rejected claims rewritten", t0)}


# ---------------------------------------------------------------- judge
_MANDATE_WEIGHTS = {
    "growth": {"bear_weight": 1.0, "revenue": 2.0, "gross_bookings": 2.0, "users": 1.5, "trips": 1.0, "rev_per_rider_q4": 1.5},
    "value": {"bear_weight": 1.15, "adj_ebitda": 2.0, "net_loss": 1.5, "op_cash_flow": 1.5},
    "conservative": {"bear_weight": 1.3, "op_cash_flow": 2.0, "adj_ebitda": 1.5, "net_loss": 2.0},
}


_PROFIT_KEYS = ("net_loss", "adj_ebitda", "op_cash_flow")


def score_company(company: str, state: dict) -> dict:
    """Conviction 1-5 = 3 + debate balance + reported metrics.

    Metrics count twice: once for direction (improved vs FY2020) and, for the profit and
    cash metrics, once more against the company if the FY2021 figure is still negative.
    The mandate (from memory) sets the weights.
    """
    mandate = state.get("profile", {}).get("mandate", "growth")
    w = _MANDATE_WEIGHTS.get(mandate, _MANDATE_WEIGHTS["growth"])
    sup = lambda cs: [c for c in cs if c["status"] == "supported" and c["company"] == company]  # noqa: E731
    b, r = len(sup(state.get("bull_claims", []))), len(sup(state.get("bear_claims", [])))
    debate = 0.35 * (b - w["bear_weight"] * r)
    mets = [m for m in state.get("metrics", []) if m["company"] == company]
    raw = sum((1 if m["improved"] else -1) * w.get(m["key"], 1.0) for m in mets)
    still_negative = [m for m in mets if m["key"] in _PROFIT_KEYS and m["fy2021"] < 0]
    raw -= sum(w.get(m["key"], 1.0) for m in still_negative)
    total_w = sum(w.get(m["key"], 1.0) for m in mets) + sum(w.get(m["key"], 1.0) for m in mets if m["key"] in _PROFIT_KEYS)
    metric_part = 1.5 * raw / (total_w or 1)  # between -1.5 and +1.5
    score = max(1.0, min(5.0, 3.0 + debate + metric_part))
    return {"company": company, "conviction": round(score * 2) / 2, "supported_bull": b, "supported_bear": r,
            "metrics_improved": sum(m["improved"] for m in mets), "metrics_total": len(mets),
            "still_loss_making": [m["label"] for m in still_negative], "mandate": mandate}


def judge(state: dict) -> dict:
    t0 = time.perf_counter()
    scores = [score_company(c, state) for c in _companies(state)]
    if len(scores) > 1:
        ranked = sorted(scores, key=lambda s: -s["conviction"])
        if ranked[0]["conviction"] == ranked[1]["conviction"]:
            verdict = f"Evenly matched at {ranked[0]['conviction']}/5 for a {scores[0]['mandate']} mandate."
        else:
            verdict = (f"{ranked[0]['company']} screens stronger for a {scores[0]['mandate']} mandate "
                       f"({ranked[0]['conviction']}/5 vs {ranked[1]['conviction']}/5).")
    else:
        verdict = f"{scores[0]['company']}: conviction {scores[0]['conviction']}/5 for a {scores[0]['mandate']} mandate."
    return {"judge": {"scores": scores, "verdict": verdict}, **_trace("judge", verdict, t0)}


# ---------------------------------------------------------------- writer
def _metric_lines(state: dict) -> list[str]:
    prefs = state.get("profile", {}).get("preferred_metrics", [])
    mets = sorted(state.get("metrics", []), key=lambda m: (m["key"] not in prefs, m["company"]))
    lines = []
    for m in mets:
        pct = "" if m["yoy_pct"] is None else f" ({m['yoy_pct']:+.0f}% YoY)"
        lines.append(f"| {m['company']} | {m['label']} | {fmt_value(m['fy2020'], m['unit'])} | "
                     f"{fmt_value(m['fy2021'], m['unit'])}{pct} | p.{m['page']} |")
    return lines


def _offline_memo(state: dict) -> str:
    j = state["judge"]
    bulls = [c for c in state.get("bull_claims", []) if c["status"] == "supported"]
    bears = [c for c in state.get("bear_claims", []) if c["status"] == "supported"]
    reb = state.get("rebuttal", {})
    profile = state.get("profile", {})
    lines = [f"## Due-diligence memo", f"**Request:** {state['question']}", "",
             "### Summary",
             f"{j['verdict']} The committee reviewed {len(state.get('evidence', []))} filing passages, "
             f"kept {len(bulls) + len(bears)} verified claims and read {len(state.get('metrics', []))} reported metrics. "
             f"Weighting reflects your **{profile.get('mandate', 'growth')}** mandate.", ""]
    lines += ["### Conviction", "| Company | Conviction (1-5) | Verified bull points | Verified bear points | Metrics improved |",
              "|---|---|---|---|---|"]
    for s in j["scores"]:
        lines.append(f"| {s['company']} | **{s['conviction']}** | {s['supported_bull']} | {s['supported_bear']} | "
                     f"{s['metrics_improved']}/{s['metrics_total']} |")
    lines.append("")
    for sc in j["scores"]:
        if sc.get("still_loss_making"):
            lines.append(f"*{sc['company']} improved on most metrics but is still negative on: {', '.join(sc['still_loss_making'])}.*")
    lines += ["", "### Key metrics (FY2020 → FY2021, from the filings' tables)",
              "| Company | Metric | FY2020 | FY2021 | Source |", "|---|---|---|---|---|", *_metric_lines(state), ""]
    lines += ["### Bull case"] + [f"- **{c['company']}:** {c['text']} [{c['evidence_id']}]" for c in bulls] + [""]
    lines += ["### Bear case"] + [f"- **{c['company']}:** {c['text']} [{c['evidence_id']}]" for c in bears] + [""]
    if reb.get("bear_rebuttal"):
        lines += ["### Debate", f"- **Bear rebuttal:** {reb['bear_rebuttal']}", f"- **Bull response:** {reb['bull_response']}", ""]
    lines += ["### Open questions for the next round",
              "- How durable is the FY2021 recovery once pandemic effects fade?",
              "- What would a change in driver classification rules cost each company?",
              "- When does operating cash flow turn sustainably positive?"]
    notes = state.get("review", {}).get("notes")
    if notes:
        lines += ["", "### Reviewer notes addressed", f"- {notes}"]
    past = state.get("past_memos") or []
    if past:
        last = past[-1]
        lines += ["", f"*Memory: your previous memo ({last['date']}) asked \"{_short(last['question'], 90)}\".*"]
    return "\n".join(lines)


def _sources_section(memo: str, state: dict) -> str:
    ev = _evidence_map(state)
    cited = []
    for eid in re.findall(r"\[(E\d+)\]", memo):
        if eid in ev and eid not in cited:
            cited.append(eid)
    if not cited:
        return memo
    rows = [f"- **{e}**: {ev[e]['company']} 10-K FY2021, Item {ev[e]['item']} {ev[e]['item_title']}, p.{ev[e]['page']}" for e in cited]
    return memo.rstrip() + "\n\n### Sources\n" + "\n".join(rows) + "\n"


def writer(state: dict) -> dict:
    t0 = time.perf_counter()
    how = "offline"
    memo = None
    if _use_llm(state, "writer"):
        try:
            from .llm import chat

            verified = [c for c in state.get("bull_claims", []) + state.get("bear_claims", []) if c["status"] == "supported"]
            ids = sorted({c["evidence_id"] for c in verified}, key=lambda x: int(x[1:]))
            user = json.dumps({
                "request": state["question"], "judge": state["judge"], "verified_claims": verified,
                "rebuttal": state.get("rebuttal"), "metrics_table": _metric_lines(state),
                "reviewer_profile": state.get("profile"), "past_memos": state.get("past_memos"),
                "reviewer_notes": state.get("review", {}).get("notes"), "allowed_evidence_ids": ids,
            }, indent=1)
            memo = chat(prompts.WRITER_SYSTEM, user, temperature=0.3)
            allowed = set(ids)
            memo = re.sub(r"\[(E\d+)\]", lambda m: m.group(0) if m.group(1) in allowed else "", memo)
            how = "llm"
        except Exception as exc:
            memo, how = None, f"offline (LLM failed: {type(exc).__name__})"
    if not memo:
        memo = _offline_memo(state)
    memo = _sources_section(memo, state)
    memo, flags = check_output(memo)
    summary = f"memo drafted ({len(memo.split())} words) [{how}]" + (" · " + " ".join(flags) if flags else "")
    return {"memo": memo, "output_flags": flags, **_trace("writer", summary, t0)}


# ---------------------------------------------------------------- human review + finalize
def human_review(state: dict) -> dict:
    from langgraph.types import interrupt

    t0 = time.perf_counter()
    decision = interrupt({"memo": state.get("memo", ""), "verdict": state.get("judge", {}).get("verdict", "")})
    if not isinstance(decision, dict):
        decision = {"action": str(decision)}
    action = decision.get("action", "approve")
    from .observability import log_feedback

    log_feedback(state, decision)
    update: dict[str, Any] = {"review": decision}
    if action == "follow_up" and decision.get("question"):
        update.update({"question": decision["question"], "attempts": 0, "bull_claims": [], "bear_claims": []})
    return {**update, **_trace("human_review", f"reviewer chose: {action}", t0)}


def after_review(state: dict) -> str:
    action = state.get("review", {}).get("action", "approve")
    return {"revise": "writer", "follow_up": "guard"}.get(action, "finalize")


def finalize(state: dict) -> dict:
    t0 = time.perf_counter()
    j = state.get("judge", {})
    MemoryStore().add_memo(state.get("user_id", "default"), state["question"], j.get("verdict", ""),
                           {s["company"]: s["conviction"] for s in j.get("scores", [])})
    out = {"final": True, **_trace("finalize", "memo approved and saved to long-term memory", t0)}
    from .observability import log_run

    log_run({**state, "trace": state.get("trace", []) + out["trace"]})
    return out


def refuse(state: dict) -> dict:
    t0 = time.perf_counter()
    return {"memo": f"**Request not processed.** {state.get('refusal_reason', '')}", "final": True,
            **_trace("refuse", "guardrail stopped the run", t0)}
