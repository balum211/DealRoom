"""DealRoom settings. Every value can be overridden with an environment variable."""
from __future__ import annotations

import os
from pathlib import Path

from filingsight import config as fs_config  # loads .env as a side effect

ROOT = fs_config.ROOT
DATA_DIR = fs_config.DATA_DIR
MEMORY_PATH = Path(os.getenv("DR_MEMORY_PATH", DATA_DIR / "memory" / "store.json"))
EVAL_DIR = ROOT / "eval"
RESULTS_DIR = EVAL_DIR / "results"

COMPANIES = fs_config.COMPANIES
COVERED_YEARS = fs_config.COVERED_YEARS

# Candidates per retriever before reranking. FilingSight used 20 for single questions;
# the Researcher runs ~10 searches per memo, so 12 keeps the memo fast on a laptop CPU.
fs_config.CANDIDATES_K = int(os.getenv("DR_CANDIDATES_K", 12))

# Agent loop limits (cost and runaway guards)
MAX_VERIFY_RETRIES = int(os.getenv("DR_MAX_VERIFY_RETRIES", 2))
CLAIMS_PER_SIDE = int(os.getenv("DR_CLAIMS_PER_SIDE", 4))
EVIDENCE_PER_TOPIC = int(os.getenv("DR_EVIDENCE_PER_TOPIC", 4))
MAX_TOPICS = int(os.getenv("DR_MAX_TOPICS", 5))

# Researcher calls the knowledge base through the MCP server (stdio) instead of in-process.
RESEARCH_VIA_MCP = os.getenv("DR_RESEARCH_VIA_MCP", "0") == "1"

# "auto" uses the LLM when a key is set and falls back to the offline agents otherwise.
# "offline" forces the deterministic agents (no key, no cost, fully reproducible).
AGENT_MODE = os.getenv("DR_AGENT_MODE", "auto")

# Token prices (USD per 1M tokens) used to estimate cost per memo. Set these to your provider's
# current rates; local models (Ollama) cost 0 per call.
PRICE_IN_PER_M = float(os.getenv("DR_PRICE_IN_PER_M", 0.13))
PRICE_OUT_PER_M = float(os.getenv("DR_PRICE_OUT_PER_M", 0.40))

# Agentic retrieval: re-search a sub-question with a reformulated query when the first pass looks weak.
RESEARCH_RETRY_MIN_HITS = int(os.getenv("DR_RESEARCH_RETRY_MIN_HITS", 3))
RESEARCH_RETRY_MIN_SCORE = float(os.getenv("DR_RESEARCH_RETRY_MIN_SCORE", 0.5))

# Observability: every run's agent trace is appended here as JSON lines; human review decisions go
# to the feedback log, which the eval can replay as regression cases.
TRACE_DIR = Path(os.getenv("DR_TRACE_DIR", DATA_DIR / "traces"))
FEEDBACK_PATH = Path(os.getenv("DR_FEEDBACK_PATH", DATA_DIR / "eval" / "feedback.jsonl"))

DISCLAIMER = (
    "DealRoom is a research assistant for education. It summarises public SEC filings and "
    "is not investment advice. Verify every figure against the cited filing page."
)


def llm_enabled(mode: str | None = None) -> bool:
    mode = mode or AGENT_MODE
    return mode != "offline" and fs_config.llm_available()


def is_local_model() -> bool:
    """True when the OpenAI-compatible endpoint is a local server such as Ollama."""
    return any(h in (fs_config.LLM_BASE_URL or "") for h in ("localhost", "127.0.0.1", ":11434"))


def tracing_enabled() -> bool:
    return os.getenv("LANGSMITH_TRACING", os.getenv("LANGCHAIN_TRACING_V2", "")).lower() == "true" and bool(
        os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"))


def llm_label() -> str:
    if not fs_config.llm_available():
        return "offline agents (no API key)"
    return f"{fs_config.LLM_MODEL}" + (" (local, Ollama)" if is_local_model() else "")
