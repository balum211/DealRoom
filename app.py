"""DealRoom Streamlit app: watch an AI investment committee debate SEC filings, then approve the memo."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dealroom import config, ui  # noqa: E402
from dealroom.graph import NODE_LABELS, DealRoom  # noqa: E402
from dealroom.memory import MemoryStore  # noqa: E402
from dealroom.metrics import fmt_value  # noqa: E402

st.set_page_config(page_title="DealRoom · AI investment committee", page_icon="🏛️", layout="wide")
st.markdown(ui.CSS + ui.MEMO_CSS, unsafe_allow_html=True)

EXAMPLES = [
    ("⚖️ Uber vs Lyft", "Should a growth fund prefer Uber or Lyft based on their FY2021 10-Ks?"),
    ("📉 Uber profitability", "Is Uber's path to profitability credible?"),
    ("⚠️ Lyft risks", "What are Lyft's biggest risks, and do its 2021 results offset them?"),
    ("💵 Cash burn", "Compare Uber and Lyft on cash burn and liquidity."),
]


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
ss.setdefault("question", EXAMPLES[0][1])

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🏛️ DealRoom")
    st.caption("AI investment committee · Team 24")
    st.markdown("#### 👤 Reviewer profile")
    user_id = st.text_input("Reviewer name", value="demo").strip() or "demo"
    user = store.get_user(user_id)
    mandates = ["growth", "value", "conservative"]
    mandate = st.selectbox("Investment mandate", mandates, index=mandates.index(user["profile"]["mandate"]),
                           help="The Judge weights metrics and bear points differently for each mandate.")
    metric_opts = ["revenue", "gross_bookings", "adj_ebitda", "net_loss", "op_cash_flow", "users", "trips", "rev_per_rider_q4"]
    prefs = st.multiselect("Metrics to lead with", metric_opts,
                           default=[m for m in user["profile"]["preferred_metrics"] if m in metric_opts])
    if st.button("💾 Save profile to memory", width="stretch"):
        store.save_profile(user_id, {"mandate": mandate, "preferred_metrics": prefs})
        st.toast("Profile saved. The Judge and Writer will use it.", icon="🧠")

    st.markdown("#### ⚙️ Run options")
    llm_ok = config.llm_enabled("auto")
    mode = st.segmented_control("Agents", ["auto", "offline"], default="auto",
                                help="auto = LLM agents when an API key is set, otherwise offline agents.") or "auto"
    st.caption(f"Engine: **{config.llm_label() if llm_ok and mode == 'auto' else 'offline agents (no key needed)'}**")
    inject = st.toggle("🧪 Stress test: plant a false claim", value=False,
                       help="Adds a made-up Bull claim ('revenue grew 250%') to show the Verifier catching it.")
    via_mcp = st.toggle("🔌 Researcher uses the MCP server", value=False,
                        help="Runs the knowledge base as an MCP server (stdio) and has the Researcher call it.")

    st.markdown("#### 🧠 Memory")
    if user["memos"]:
        for m in reversed(user["memos"][-3:]):
            with st.container(border=True):
                st.caption(f"{m['date']}")
                st.markdown(f"**{m['question'][:70]}**")
                st.caption(m["summary"])
        if st.button("Clear my memory", width="stretch"):
            store.clear(user_id)
            st.rerun()
    else:
        st.caption("No approved memos yet. Approve one and it is remembered here.")


def run_stream(gen, box) -> None:
    for node, update in gen:
        if node == "__interrupt__":
            continue
        for t in (update or {}).get("trace", []):
            ss.trace.append(t)
            icon = ui.ICONS.get(t["node"], "•")
            box.markdown(f"{icon} **{NODE_LABELS.get(t['node'], t['node'])}** · {t['summary']}")
            box.update(label=f"{icon} {NODE_LABELS.get(t['node'], t['node'])} done")


# ---------------------------------------------------------------- main
st.markdown(ui.hero(), unsafe_allow_html=True)
tab_room, tab_eval, tab_how = st.tabs(["🏛️  Committee", "📊  Evaluation", "🧩  How it works"])

with tab_room:
    st.markdown("##### Pick a scenario or write your own")
    cols = st.columns(len(EXAMPLES))
    for col, (label, ex) in zip(cols, EXAMPLES):
        if col.button(label, width="stretch", help=ex):
            ss.question = ex
    q_col, b_col = st.columns([5, 1], vertical_alignment="bottom")
    with q_col:
        question = st.text_area("Your due-diligence request", key="question", height=80, label_visibility="collapsed")
    with b_col:
        go = st.button("🚀 Convene", type="primary", width="stretch")

    if go:
        ss.thread = room.new_thread()
        ss.trace = []
        with st.status("The committee is in session…", expanded=True) as box:
            t0 = time.perf_counter()
            run_stream(room.start(question, ss.thread, user_id=user_id, mode=mode, inject_faulty=inject,
                                  via_mcp=via_mcp, profile={"mandate": mandate, "preferred_metrics": prefs}), box)
            box.update(label=f"✅ Committee finished in {time.perf_counter() - t0:.1f}s", state="complete", expanded=False)

    if ss.thread:
        state = room.state(ss.thread)
        st.markdown(ui.pipeline(ss.trace), unsafe_allow_html=True)

        if state.get("refused"):
            st.error(state.get("memo", "Request blocked."), icon="⛔")
        elif state.get("memo"):
            for note in state.get("guard", {}).get("notes", []):
                st.info(note, icon="🛡️")
            st.markdown(ui.verdict(state.get("judge", {})), unsafe_allow_html=True)

            t_debate, t_metrics, t_memo, t_evidence, t_trace = st.tabs(
                ["⚔️  Debate", "🧮  Metrics", "📝  Memo", "📚  Evidence", "🕒  Agent log"])
            all_claims = state.get("bull_claims", []) + state.get("bear_claims", [])
            with t_debate:
                dropped = [c for c in all_claims if c["status"] == "dropped"]
                if dropped:
                    replaced_by = {c.get("revision_of"): c["id"] for c in all_claims if c.get("revision_of")}
                    st.markdown(ui.caught(dropped, replaced_by), unsafe_allow_html=True)
                left, right = st.columns(2, gap="large")
                bulls = [c for c in state.get("bull_claims", []) if c["status"] != "dropped"]
                bears = [c for c in state.get("bear_claims", []) if c["status"] != "dropped"]
                with left:
                    st.markdown(ui.side_header("🐂", "Bull case", len(bulls)) + "".join(ui.claim(c) for c in bulls),
                                unsafe_allow_html=True)
                with right:
                    st.markdown(ui.side_header("🐻", "Bear case", len(bears)) + "".join(ui.claim(c) for c in bears),
                                unsafe_allow_html=True)
                reb = state.get("rebuttal") or {}
                if reb.get("bear_rebuttal"):
                    st.markdown(ui.rebuttal(reb), unsafe_allow_html=True)
            with t_metrics:
                st.markdown(ui.metric_grid(state.get("metrics", []), fmt_value), unsafe_allow_html=True)
                st.caption("Read by the Quant agent straight from the filings' tables. The page chip is the source page.")
            with t_memo:
                with st.container(key="memo_paper"):
                    st.markdown(state["memo"])
                st.download_button("⬇️ Download memo (.md)", state["memo"], file_name="dealroom_memo.md")
            with t_evidence:
                ev = {e["id"]: e for e in state.get("evidence", [])}
                cited = []
                for c in all_claims:
                    if c["evidence_id"] in ev and c["evidence_id"] not in cited:
                        cited.append(c["evidence_id"])
                st.caption(f"{len(cited)} passages cited out of {len(ev)} retrieved. Expand one to read the exact filing text.")
                for eid in cited + [e for e in ev if e not in cited]:
                    e = ev[eid]
                    star = "⭐ " if eid in cited else ""
                    with st.expander(f"{star}{eid} · {e['company']} 10-K FY2021 · Item {e['item']} {e['item_title']} · p.{e['page']}"):
                        st.text(e["text"])
            with t_trace:
                for t in ss.trace:
                    st.markdown(f"{ui.ICONS.get(t['node'], '•')} **{NODE_LABELS.get(t['node'], t['node'])}** · "
                                f"{t['summary']} <span style='color:#6B7493'>({t['ms']} ms)</span>", unsafe_allow_html=True)

            if room.waiting_for_review(ss.thread):
                st.markdown(ui.review_header(), unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3, gap="medium")
                with c1:
                    st.markdown("**Ship it**")
                    if st.button("✅ Approve memo", type="primary", width="stretch"):
                        with st.status("Saving to memory…") as box:
                            run_stream(room.resume({"action": "approve"}, ss.thread), box)
                        st.rerun()
                with c2:
                    notes = st.text_input("Ask the Writer for changes", placeholder="e.g. lead with cash burn")
                    if st.button("✍️ Revise memo", width="stretch", disabled=not notes):
                        with st.status("Writer revising…") as box:
                            run_stream(room.resume({"action": "revise", "notes": notes}, ss.thread), box)
                        st.rerun()
                with c3:
                    follow = st.text_input("Follow-up question", placeholder="e.g. How exposed is Lyft to reclassification?")
                    if st.button("🔁 Ask follow-up", width="stretch", disabled=not follow):
                        with st.status("Committee reconvening…", expanded=True) as box:
                            run_stream(room.resume({"action": "follow_up", "question": follow}, ss.thread), box)
                        st.rerun()
            elif state.get("final"):
                st.success("Memo approved and saved to your long-term memory.", icon="💾")

with tab_eval:
    summary = config.RESULTS_DIR / "summary.md"
    if summary.exists():
        st.markdown(summary.read_text(encoding="utf-8"))
    else:
        st.info("Run `python eval/run_eval.py` to generate the evaluation report.")

with tab_how:
    arch = ROOT / "docs" / "ARCHITECTURE.md"
    if arch.exists():
        st.markdown(arch.read_text(encoding="utf-8"))

st.markdown(ui.footer(), unsafe_allow_html=True)
