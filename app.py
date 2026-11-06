"""DealRoom Streamlit app: watch an AI investment committee debate SEC filings, then approve the memo."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dealroom import config  # noqa: E402
from dealroom.graph import NODE_LABELS, DealRoom  # noqa: E402
from dealroom.memory import MemoryStore  # noqa: E402
from dealroom.metrics import fmt_value  # noqa: E402

st.set_page_config(page_title="DealRoom · Team 24", page_icon="🏛️", layout="wide")

EXAMPLES = [
    "Should a growth fund prefer Uber or Lyft based on their FY2021 10-Ks?",
    "Is Uber's path to profitability credible?",
    "What are Lyft's biggest risks, and do its 2021 results offset them?",
]
ICONS = {"guard": "🛡️", "planner": "🗺️", "researcher": "🔎", "quant": "🧮", "bull": "🐂", "bear": "🐻",
         "rebuttal": "⚔️", "verifier": "✅", "revise": "🔁", "judge": "⚖️", "writer": "✍️",
         "human_review": "🙋", "finalize": "💾", "refuse": "⛔"}
STATUS_BADGE = {"supported": "🟢 verified", "unsupported": "🔴 rejected", "dropped": "⚪ replaced", "pending": "🟡 pending"}


@st.cache_resource(show_spinner="Loading the 10-K knowledge base…")
def get_room() -> DealRoom:
    from dealroom.tools import get_index

    get_index()
    return DealRoom()


room = get_room()
store = MemoryStore()
ss = st.session_state
ss.setdefault("thread", None)
ss.setdefault("trace", [])
ss.setdefault("question", EXAMPLES[0])

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("🏛️ DealRoom")
    st.caption("Team 24 · The Gen Academy, Mastering Agentic AI")
    user_id = st.text_input("Reviewer name", value="demo").strip() or "demo"
    user = store.get_user(user_id)
    mandate = st.selectbox("Investment mandate", ["growth", "value", "conservative"],
                           index=["growth", "value", "conservative"].index(user["profile"]["mandate"]))
    metric_opts = ["revenue", "gross_bookings", "adj_ebitda", "net_loss", "op_cash_flow", "users", "trips", "rev_per_rider_q4"]
    prefs = st.multiselect("Metrics to show first", metric_opts, default=[m for m in user["profile"]["preferred_metrics"] if m in metric_opts])
    if st.button("Save profile to memory"):
        store.save_profile(user_id, {"mandate": mandate, "preferred_metrics": prefs})
        st.success("Saved. The Judge and Writer will use it.")

    st.divider()
    st.subheader("Run options")
    llm_ok = config.llm_enabled("auto")
    mode = st.radio("Agents", ["auto", "offline"], horizontal=True,
                    help="auto = LLM agents when an API key is set, otherwise offline agents. "
                         "offline = deterministic extractive agents (no key, no cost).")
    st.caption(f"LLM: **{config.llm_label() if llm_ok and mode == 'auto' else 'offline agents'}**")
    inject = st.toggle("Stress test: inject a false claim", value=False,
                       help="Adds a made-up Bull claim ('revenue grew 250%') to show the Verifier catching it and the retry loop.")
    via_mcp = st.toggle("Researcher calls tools over MCP", value=False,
                        help="Runs the knowledge base as an MCP server (stdio) and has the Researcher call it.")

    st.divider()
    st.subheader("🧠 Memory")
    if user["memos"]:
        for m in reversed(user["memos"][-3:]):
            st.caption(f"**{m['date']}** · {m['question'][:70]}\n\n{m['summary']}")
        if st.button("Clear my memory"):
            store.clear(user_id)
            st.rerun()
    else:
        st.caption("No approved memos yet. Approve one and it is remembered here.")

# ---------------------------------------------------------------- helpers


def render_timeline(trace: list[dict], container) -> None:
    for t in trace:
        icon = ICONS.get(t["node"], "•")
        container.markdown(f"{icon} **{NODE_LABELS.get(t['node'], t['node'])}** · {t['summary']}  "
                           f"<span style='color:#888'>({t['ms']} ms)</span>", unsafe_allow_html=True)


def run_stream(gen, status_box) -> None:
    for node, update in gen:
        if node == "__interrupt__":
            continue
        for t in (update or {}).get("trace", []):
            ss.trace.append(t)
            icon = ICONS.get(t["node"], "•")
            status_box.markdown(f"{icon} **{NODE_LABELS.get(t['node'], t['node'])}** · {t['summary']}")
            status_box.update(label=f"{icon} {NODE_LABELS.get(t['node'], t['node'])} finished")


def claim_card(c: dict) -> None:
    badge = STATUS_BADGE.get(c["status"], c["status"])
    with st.container(border=True):
        st.markdown(f"**{c['id']} · {c['company']}** &nbsp; {badge} &nbsp; <span style='color:#888'>[{c['evidence_id']}] · {c.get('by', '')}</span>",
                    unsafe_allow_html=True)
        st.markdown(c["text"])
        if c.get("reason") and c["status"] != "supported":
            st.caption(f"Verifier: {c['reason']}")


# ---------------------------------------------------------------- main
st.title("DealRoom: an AI investment committee for SEC filings")
st.caption("Planner → Researcher + Quant → Bull vs Bear debate → Verifier → Judge → Writer → **you approve**. "
           "Every claim links to the 10-K page it came from. Knowledge base: Uber and Lyft FY2021 Form 10-K.")

tab_room, tab_eval, tab_how = st.tabs(["🏛️ Committee", "📊 Evaluation", "🧩 How it works"])

with tab_room:
    cols = st.columns(len(EXAMPLES))
    for col, ex in zip(cols, EXAMPLES):
        if col.button(ex, width="stretch"):
            ss.question = ex
    question = st.text_area("Your due-diligence request", key="question", height=70)
    go = st.button("Convene the committee", type="primary")

    if go:
        ss.thread = room.new_thread()
        ss.trace = []
        with st.status("Committee at work…", expanded=True) as box:
            t0 = time.perf_counter()
            run_stream(room.start(question, ss.thread, user_id=user_id, mode=mode, inject_faulty=inject,
                                  via_mcp=via_mcp, profile={"mandate": mandate, "preferred_metrics": prefs}), box)
            box.update(label=f"Committee finished in {time.perf_counter() - t0:.1f}s", state="complete", expanded=False)

    if ss.thread:
        state = room.state(ss.thread)
        if not go and ss.trace:
            with st.expander("Agent timeline", expanded=False):
                render_timeline(ss.trace, st)

        if state.get("refused"):
            st.error(state.get("memo", "Request blocked."))
        elif state.get("memo"):
            for note in state.get("guard", {}).get("notes", []):
                st.info(note)
            j = state.get("judge", {})
            st.markdown(f"### ⚖️ {j.get('verdict', '')}")
            score_cols = st.columns(max(len(j.get("scores", [])), 1))
            for col, s in zip(score_cols, j.get("scores", [])):
                col.metric(f"{s['company']} conviction", f"{s['conviction']} / 5",
                           help=f"{s['supported_bull']} verified bull points, {s['supported_bear']} verified bear points, "
                                f"{s['metrics_improved']}/{s['metrics_total']} metrics improved, {s['mandate']} mandate")

            t_debate, t_metrics, t_memo, t_evidence = st.tabs(["⚔️ Debate", "🧮 Metrics", "📝 Memo", "📚 Evidence"])
            with t_debate:
                caught = [c for c in state.get("bull_claims", []) + state.get("bear_claims", []) if c["status"] == "dropped"]
                if caught:
                    replaced_by = {c.get("revision_of"): c["id"] for c in state.get("bull_claims", []) + state.get("bear_claims", [])
                                   if c.get("revision_of")}
                    with st.container(border=True):
                        st.markdown(f"**✅ Verifier caught {len(caught)} unsupported claim(s) and sent them back**")
                        for c in caught:
                            st.markdown(f"🔴 ~~{c['text']}~~  \n<span style='color:#888'>{c['id']} · {c['company']} · "
                                        f"{c.get('reason', '')} → replaced by **{replaced_by.get(c['id'], '-')}**</span>",
                                        unsafe_allow_html=True)
                left, right = st.columns(2)
                with left:
                    st.subheader("🐂 Bull")
                    for c in state.get("bull_claims", []):
                        if c["status"] != "dropped":
                            claim_card(c)
                with right:
                    st.subheader("🐻 Bear")
                    for c in state.get("bear_claims", []):
                        if c["status"] != "dropped":
                            claim_card(c)
                reb = state.get("rebuttal") or {}
                if reb.get("bear_rebuttal"):
                    st.subheader("⚔️ Rebuttal round")
                    st.markdown(f"**Bear:** {reb['bear_rebuttal']}")
                    st.markdown(f"**Bull:** {reb['bull_response']}")
                if state.get("attempts"):
                    st.caption(f"Verifier sent claims back {state['attempts']} time(s); rejected claims were replaced.")
            with t_metrics:
                rows = [{"Company": m["company"], "Metric": m["label"], "FY2020": fmt_value(m["fy2020"], m["unit"]),
                         "FY2021": fmt_value(m["fy2021"], m["unit"]),
                         "YoY": "" if m["yoy_pct"] is None else f"{m['yoy_pct']:+.1f}%",
                         "Improved": "✅" if m["improved"] else "❌", "Source": f"p.{m['page']}", "Filing row": m["row_text"]}
                        for m in state.get("metrics", [])]
                st.dataframe(rows, width="stretch", hide_index=True)
                st.caption("Read by the Quant agent straight from the filings' tables; the last column is the exact row it parsed.")
            with t_memo:
                st.markdown(state["memo"])
                st.download_button("Download memo (.md)", state["memo"], file_name="dealroom_memo.md")
            with t_evidence:
                ev = {e["id"]: e for e in state.get("evidence", [])}
                cited = []
                for c in state.get("bull_claims", []) + state.get("bear_claims", []):
                    if c["evidence_id"] in ev and c["evidence_id"] not in cited:
                        cited.append(c["evidence_id"])
                st.caption(f"{len(cited)} passages cited out of {len(ev)} retrieved. Expand one to read the filing text.")
                for eid in cited + [e for e in ev if e not in cited]:
                    e = ev[eid]
                    with st.expander(f"{eid} · {e['company']} 10-K FY2021 · Item {e['item']} {e['item_title']} · p.{e['page']}"
                                     + (" · cited" if eid in cited else "")):
                        st.text(e["text"])

            st.divider()
            if room.waiting_for_review(ss.thread):
                st.subheader("🙋 Human review")
                st.caption("The graph is paused. Nothing is saved until you approve.")
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("✅ Approve memo", type="primary", width="stretch"):
                        with st.status("Finalizing…") as box:
                            run_stream(room.resume({"action": "approve"}, ss.thread), box)
                        st.rerun()
                with c2:
                    notes = st.text_input("Ask the Writer for changes", placeholder="e.g. lead with cash burn")
                    if st.button("✍️ Revise memo", width="stretch", disabled=not notes):
                        with st.status("Writer revising…") as box:
                            run_stream(room.resume({"action": "revise", "notes": notes}, ss.thread), box)
                        st.rerun()
                with c3:
                    follow = st.text_input("Follow-up question", placeholder="e.g. How exposed is Lyft to driver reclassification?")
                    if st.button("🔁 Ask follow-up", width="stretch", disabled=not follow):
                        with st.status("Committee reconvening…", expanded=True) as box:
                            run_stream(room.resume({"action": "follow_up", "question": follow}, ss.thread), box)
                        st.rerun()
            elif state.get("final"):
                st.success("Memo approved and saved to your long-term memory.")

with tab_eval:
    summary = config.RESULTS_DIR / "summary.md"
    if summary.exists():
        st.markdown(summary.read_text(encoding="utf-8"))
    else:
        st.info("Run `python eval/run_eval.py` to generate the evaluation report.")

with tab_how:
    st.markdown((ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8") if (ROOT / "docs" / "ARCHITECTURE.md").exists() else "")
    try:
        st.code(room.graph.get_graph().draw_mermaid(), language="mermaid")
    except Exception:
        pass
