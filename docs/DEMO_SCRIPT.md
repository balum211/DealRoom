# Demo video script (about 3 minutes)

**Setup before recording**
1. `run.bat` (or `streamlit run app.py`), wait for the page to load.
2. Run the first example once so the index is warm, then refresh.
3. Sidebar: reviewer name `demo`, mandate **growth**, turn on **Stress test: plant a false claim**.
4. No API key is needed. In `auto` mode the Writer uses the free GPT-OSS 20B model (one reply every 45 seconds,
   so wait about a minute between runs). For every agent on a model, use the Ollama lines in `.env.example`.
5. Record the browser window with Windows `Win + Alt + R` (Xbox Game Bar) or OBS / Loom. Upload the file to
   Google Drive and set sharing to "Anyone with the link can view".

| Time | On screen | Say |
|---|---|---|
| 0:00 to 0:15 | App title | "We're Team 24. This is DealRoom, an AI investment committee that turns SEC filings into a cited, debated memo in seconds." |
| 0:15 to 0:30 | Click the **Uber vs Lyft** scenario, then **Convene committee** | "One question in. A guardrail checks it, and a Planner splits it into growth, profitability, cash, risk and strategy questions for each company." |
| 0:30 to 0:55 | Pipeline: Researcher and Quant finish | "A Researcher searches both 10-Ks in parallel using hybrid search, and the same tools are exposed as an MCP server. If a search comes back weak, the Researcher rewrites the query and searches again. That's agentic RAG. A Quant agent reads twelve figures straight from the filings' tables, no LLM needed." |
| 0:55 to 1:20 | **Debate** tab: Bull and Bear columns, rebuttal | "Now a Bull and a Bear argue opposite cases from the same evidence, and then rebut each other." |
| 1:20 to 1:40 | Scroll to the red "rejected" claim B0 and its replacement | "We planted a false claim: revenue grew 250 percent. The Verifier caught that the quote isn't on the cited page, sent it back, and the Bull replaced it with a supported one." |
| 1:40 to 2:00 | **Metrics** tab, then **Memo** tab, then **Evidence** tab and expand one passage | "The Judge scores conviction from verified claims and metrics, weighted by my mandate from memory. The Writer drafts a memo where every claim has a footnote to the exact filing page." |
| 2:00 to 2:15 | **Agent log** tab: the time, LLM calls, tokens and cost strip, then the per-agent lines | "Every agent is traced: time, LLM calls, tokens and estimated cost per memo. The same trace goes to a run log, or to LangSmith when tracing is on." |
| 2:15 to 2:30 | Human review buttons, click **Approve memo** | "A human approves before anything is saved. Approved memos go into long-term memory, and every review decision is logged so we can replay it as a regression test." |
| 2:30 to 2:45 | **Evaluation** tab | "On our evaluation, 100 percent of final claims are verified, the planted claim is caught every time, retrieval hit at five is 95 percent, and we track latency and cost per memo." |
| 2:45 to 3:00 | **Course map** tab, scroll through the weeks | "And this maps every topic from Weeks 1 to 5 to where it lives in DealRoom, including local models with Ollama. Code is on GitHub. Thanks!" |

Tips
- If time is short, skip the Course map scroll and just say it is there.
- The whole committee takes about 10 to 25 seconds on a laptop.
- The Agent log shows 0 tokens and $0 with offline agents. Say "offline agents need no API key, so this run is free",
  or point out the Writer's one model call and its token count.
- To show a re-search on screen, use the **Cash burn** or **Uber profitability** scenario: the Researcher line in
  the Agent log then says how many weak results were searched again.
