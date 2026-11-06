# Team 24 Demo Day proposal: DealRoom

**Team 24 · The Gen Academy, Mastering Agentic AI · November 2026**
Repo: https://github.com/balum211/DealRoom

DealRoom is a team of AI agents that does a junior analyst's first pass of due diligence in seconds. It reads a
company's SEC filings, has a Bull agent and a Bear agent argue the case with citations, checks every claim
against its source, and hands a human reviewer a one-page investment memo where every claim links back to the
filing page it came from.

## Problem and users

A single 10-K runs 150 to 300 pages, and a real diligence pass compares two or more companies. Analysts,
founders and retail investors either spend days reading or trust a summary they cannot check. Plain chatbots
fall short in three ways:

- **One-sided answers.** A single model tends to agree with the question's framing.
- **Unverifiable numbers.** Figures without a page reference cannot be trusted in an investment committee.
- **No judgment step.** Nobody signs off before the memo goes out.

| User | Job to be done | What DealRoom gives them |
|---|---|---|
| Junior analyst or associate | First-pass diligence on a target or competitor | A cited memo plus the open questions to chase |
| Startup founder | Understand how a public competitor makes and loses money | Side-by-side metrics and risk factors |
| Retail investor or student | Learn to read a 10-K critically | Both sides of the argument, source page one click away |

## Solution: why it is agentic, not just RAG

1. **Planning.** A Planner splits the request into sub-questions per company (growth, profitability, cash,
   risks, strategy, plus the user's own focus).
2. **Tool use.** Agents call a hybrid filing search, a table-reading metrics tool and a change calculator. The
   same tools are served by an **MCP server** that any MCP client can use.
3. **Multi-agent debate.** Bull and Bear get the same evidence but opposite briefs, run in parallel, then one
   rebuttal round. A Judge weighs them.
4. **Self-correction.** A Verifier rejects claims whose quote is not on the cited page, whose numbers are not in
   the source, or whose company does not match, and sends them back for a rewrite (max 2 loops).
5. **Human in the loop.** The graph pauses with `interrupt()` before anything is saved: approve, ask for
   changes, or ask a follow-up.
6. **Memory.** Short-term thread memory (LangGraph checkpointer) and long-term reviewer memory (mandate,
   preferred metrics, past memos) that changes how the Judge scores and the Writer writes.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the graph and the agent table.

| Layer | Choice |
|---|---|
| Orchestration | LangGraph: parallel fan-out (Researcher + Quant, Bull + Bear), conditional retry loop, interrupt for human review, checkpointer |
| LLM | Any OpenAI-compatible model via LangChain (Nebius Llama-3.3-70B by default); deterministic offline agents when no key is set |
| Retrieval | Reused from our Week 2 project FilingSight: semantic chunks, Chroma (MiniLM ONNX) + BM25, Reciprocal Rank Fusion, local reranker, company filters |
| Data | Uber and Lyft FY2021 Form 10-K (SEC EDGAR), 1,767 chunks with company, page and 10-K Item metadata |
| Tools | MCP server (`dealroom-filings`): `search_filings`, `get_page`, `list_companies`, `key_metrics`, `compute_change` |
| UI | Streamlit: live agent timeline, debate view with verification badges, metrics table, memo with footnotes, evidence viewer, approve / revise / follow-up |
| Quality | pytest suite (27 tests), evaluation script, GitHub Actions CI |

## Guardrails

- **Input:** prompt-injection patterns, empty or oversized requests, off-topic requests and companies outside the
  knowledge base are refused; buy/sell questions are answered with an evidence assessment, not advice.
- **Evidence:** instruction-like lines in retrieved text are stripped before any agent sees them.
- **Grounding:** a claim that fails verification never reaches the memo.
- **Output:** buy/sell language is removed and a disclaimer is always added.
- **Cost and loops:** at most 2 verification retries and 1 rebuttal round.

## Evaluation

`python eval/run_eval.py` measures citation faithfulness, whether an injected false claim is caught, Quant
accuracy against the printed filing values, retrieval hit@5 on 20 labelled questions, debate balance, guardrail
decisions, latency, and a side-by-side with plain RAG (our Week 2 FilingSight). Latest results are in
[eval/results/summary.md](../eval/results/summary.md) and in the app's Evaluation tab.

## Demo script

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (about 2 minutes 30 seconds).

## Team and plan

**Team 24:** Bala Mallampati, Ravindranath Konduru (Ravi), Deepthi Avula and Neha Madhao Pande.

One owner per workstream; everyone reviews and rehearses the demo.

| Team member | Owns |
|---|---|
| **Bala Mallampati** | LangGraph orchestration, agents, human review and memory |
| **Ravindranath Konduru** | Data ingestion, chunking, hybrid retrieval and the MCP filing server |
| **Deepthi Avula** | Streamlit UI, live debate view, README and the demo video |
| **Neha Madhao Pande** | Evaluation set, LLM judge, guardrails and the Demo Day slides |

1. **Nov 6 (done):** full committee graph, MCP server, human approval, memory, Streamlit UI and eval suite with cost and latency tracking. Today: record the demo video and submit the form by 11:59 pm PT.
2. **Nov 7 to 8:** run the eval with the LLM agents and an API key to measure real tokens and cost per memo, tune prompts, rehearse. Shortlist announced Nov 8.
3. **Nov 9 to 10 (if shortlisted):** add FY2022 and FY2023 filings, more companies, live Demo Day rehearsal.

| Risk | Fallback |
|---|---|
| LLM slow or rate limited on stage | Offline agents run the same graph with no key; a recorded run as backup |
| First run slow on a laptop while the search index warms up | Run one question before going on stage; provider and model are configurable, including a local Ollama model |
| Agents loop or overspend | Hard caps on Verifier retries and debate rounds; tokens and cost tracked per agent |
| PDF tables parse badly | Quant reads named table rows and is tested against the printed figures (12 of 12 match) |

**Future work:** live EDGAR fetch for any ticker, earnings-call transcripts, a "compare five companies" mode,
Slack delivery of approved memos.
