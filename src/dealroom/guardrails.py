"""Input, evidence and output guardrails.

* Input: refuse prompt injection, empty or oversized requests, and companies outside the
  knowledge base; flag requests for buy/sell advice (DealRoom assesses evidence instead).
* Evidence: strip instruction-like lines that a document could smuggle into an agent prompt.
* Output: no buy/sell instructions in the memo, and a disclaimer is always appended.
"""
from __future__ import annotations

import re

from filingsight import config as fs_config

MAX_QUESTION_CHARS = 600

_INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior|above) (instructions|prompts?)|disregard (the )?(system|previous)|"
    r"system prompt|you are now|developer mode|jailbreak|reveal your (prompt|instructions)|act as (an? )?(unfiltered|dan))",
    re.I,
)
_ADVICE = re.compile(r"\b(should i (buy|sell|short|invest)|buy or sell|price target|will (the )?stock (go|rise|fall)|"
                     r"guarantee(d)? return|all in)\b", re.I)
_FINANCE_HINT = re.compile(
    r"\b(revenue|growth|margin|profit|loss|ebitda|cash|risk|invest|fund|valuation|competit|strategy|driver|rider|"
    r"bookings|trips|diligence|memo|bull|bear|compare|business|segment|debt|liquidity|regulat|10-k|filing|outlook|"
    r"customers?|market|delivery|mobility|freight|economics|financial|performance|earnings|buy|sell|stock)\w*",
    re.I,
)
# Common public companies people may ask about that are NOT in the knowledge base.
_OTHER_COMPANIES = re.compile(
    r"\b(tesla|apple|microsoft|google|alphabet|amazon|meta|facebook|nvidia|netflix|doordash|airbnb|grab|didi|"
    r"instacart|walmart|caterpillar|ola|bolt)\b",
    re.I,
)
_EVIDENCE_INJECTION = re.compile(r"(?im)^.*(ignore (all |any )?(previous|prior) instructions|system prompt|you are an ai).*$")
_OUTPUT_ADVICE = re.compile(
    r"\b(you should (buy|sell|short)|we recommend (buying|selling)|strong (buy|sell)|(buy|sell) (the|this) stock|"
    r"guaranteed returns?)\b",
    re.I,
)


def check_input(question: str) -> dict:
    """Return {"allowed": bool, "reason": str, "notes": [str]}."""
    q = (question or "").strip()
    notes: list[str] = []
    if not q:
        return {"allowed": False, "reason": "Please type a due-diligence question.", "notes": notes}
    if len(q) > MAX_QUESTION_CHARS:
        return {"allowed": False, "reason": f"Please keep the request under {MAX_QUESTION_CHARS} characters.", "notes": notes}
    if _INJECTION.search(q):
        return {"allowed": False, "reason": "That request looks like an attempt to override DealRoom's instructions, so it was blocked.", "notes": notes}
    known = [c for c in fs_config.COMPANIES if re.search(rf"\b{c}\b", q, re.I)]
    others = sorted({m.group(0).title() for m in _OTHER_COMPANIES.finditer(q)})
    if others and not known:
        names = ", ".join(others)
        corpus = " and ".join(fs_config.COMPANIES)
        return {"allowed": False,
                "reason": f"{names} is not in DealRoom's knowledge base yet. It currently covers the {corpus} FY2021 10-K filings.",
                "notes": notes}
    if others:
        notes.append(f"{', '.join(others)} is not in the knowledge base; the memo covers {', '.join(known)} only.")
    if not known and not _FINANCE_HINT.search(q):
        return {"allowed": False,
                "reason": "DealRoom answers due-diligence questions about the companies in its filings (Uber, Lyft).",
                "notes": notes}
    if _ADVICE.search(q):
        notes.append("DealRoom does not give buy or sell advice. It will weigh the evidence and give a conviction score instead.")
    return {"allowed": True, "reason": "", "notes": notes}


def sanitize_evidence_text(text: str) -> str:
    return _EVIDENCE_INJECTION.sub("[line removed by guardrail]", text)


def check_output(memo: str) -> tuple[str, list[str]]:
    """Soften advice language and make sure the disclaimer is present."""
    from .config import DISCLAIMER

    flags: list[str] = []
    if _OUTPUT_ADVICE.search(memo):
        flags.append("Removed buy/sell language from the memo.")
        memo = _OUTPUT_ADVICE.sub("[assessment only, not advice]", memo)
    if DISCLAIMER not in memo:
        memo = memo.rstrip() + f"\n\n---\n*{DISCLAIMER}*\n"
    return memo, flags
