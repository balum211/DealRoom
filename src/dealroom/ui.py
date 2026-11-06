"""Visual layer for the Streamlit app: theme CSS and small HTML components."""
from __future__ import annotations

from html import escape

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{
  --bg:#0B1020; --panel:#131A2E; --panel2:#182241; --line:rgba(255,255,255,.08);
  --text:#E7EAF3; --muted:#9AA3BC; --gold:#F5B83D; --gold2:#FFD27A;
  --bull:#2FD08A; --bear:#FF6B6B; --blue:#6EA8FE; --violet:#A78BFA;
}
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea { font-family:'Inter',sans-serif !important; }
.stApp{ background:
   radial-gradient(1200px 500px at 10% -10%, rgba(110,168,254,.18), transparent 60%),
   radial-gradient(900px 400px at 100% 0%, rgba(245,184,61,.12), transparent 60%), var(--bg); }
[data-testid="stHeader"]{ background:transparent; }
.stAppDeployButton, [data-testid="stAppDeployButton"]{ display:none; }
.block-container{ padding-top:1.6rem; max-width:1280px; }
h1,h2,h3,h4{ font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.01em; }
[data-testid="stSidebar"]{ background:linear-gradient(180deg,#10172B 0%,#0B1020 100%); border-right:1px solid var(--line); }
[data-testid="stSidebar"] .stMarkdown p{ color:var(--muted); }

/* buttons */
.stButton>button, .stDownloadButton>button{ border-radius:12px; border:1px solid var(--line); background:var(--panel2);
  color:var(--text); font-weight:600; transition:all .15s ease; }
.stButton>button:hover{ border-color:var(--gold); color:var(--gold2); transform:translateY(-1px); }
.stButton>button[kind="primary"]{ background:linear-gradient(135deg,#F5B83D 0%,#F08A3E 100%); color:#1A1305; border:none;
  box-shadow:0 8px 24px rgba(245,184,61,.25); padding:.6rem 1.4rem; }
.stButton>button[kind="primary"]:hover{ color:#1A1305; box-shadow:0 10px 30px rgba(245,184,61,.4); }
textarea, input{ border-radius:12px !important; }
[data-baseweb="textarea"], [data-baseweb="input"]{ border-radius:12px !important; background:var(--panel) !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"], [data-testid="stTabs"] [role="tablist"]{ gap:6px; background:rgba(255,255,255,.03); padding:6px; border-radius:14px; border:1px solid var(--line); }
.stTabs [data-baseweb="tab"], [data-testid="stTabs"] [role="tab"]{ border-radius:10px; padding:8px 16px; color:var(--muted); font-weight:600; }
.stTabs [aria-selected="true"], [data-testid="stTabs"] [role="tab"][aria-selected="true"]{ background:var(--panel2) !important; color:var(--text) !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none; }
[data-testid="stExpander"]{ border:1px solid var(--line); border-radius:14px; background:rgba(255,255,255,.02); }
[data-testid="stStatusWidget"], [data-testid="stStatus"]{ border-radius:14px; }

/* hero */
.hero{ position:relative; overflow:hidden; border-radius:24px; padding:34px 36px; margin-bottom:22px;
  background:linear-gradient(135deg,rgba(24,34,65,.95) 0%,rgba(19,26,46,.95) 55%,rgba(60,42,12,.85) 100%);
  border:1px solid rgba(245,184,61,.25); box-shadow:0 20px 60px rgba(0,0,0,.35); }
.hero:after{ content:""; position:absolute; right:-80px; top:-80px; width:320px; height:320px; border-radius:50%;
  background:radial-gradient(circle,rgba(245,184,61,.35),transparent 65%); }
.hero .eyebrow{ color:var(--gold2); font-weight:700; font-size:.78rem; letter-spacing:.16em; text-transform:uppercase; }
.hero h1{ font-size:2.6rem; margin:.35rem 0 .5rem; line-height:1.1; color:#fff; }
.hero h1 span{ background:linear-gradient(90deg,#FFD27A,#F08A3E); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p{ color:var(--muted); font-size:1.05rem; max-width:760px; margin:0; }
.chips{ display:flex; flex-wrap:wrap; gap:10px; margin-top:18px; position:relative; z-index:1; }
.chip{ background:rgba(255,255,255,.06); border:1px solid var(--line); border-radius:999px; padding:6px 14px; font-size:.85rem; color:var(--text); }
.chip b{ color:var(--gold2); }

/* pipeline */
.pipe{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:6px 0 18px; }
.node{ display:flex; align-items:center; gap:6px; padding:6px 10px; border-radius:12px; background:var(--panel);
  border:1px solid var(--line); font-size:.85rem; color:var(--muted); }
.node.done{ color:var(--text); border-color:rgba(47,208,138,.35); background:rgba(47,208,138,.08); }
.node.retry{ border-color:rgba(255,107,107,.45); background:rgba(255,107,107,.08); color:var(--text); }
.node small{ color:var(--muted); font-size:.72rem; }
.arrow{ color:#3A4566; }

/* cards */
.card{ background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.015)); border:1px solid var(--line);
  border-radius:18px; padding:18px 20px; margin-bottom:14px; }
.verdict{ display:block; border-color:rgba(245,184,61,.3);
  background:linear-gradient(135deg,rgba(245,184,61,.10),rgba(110,168,254,.06)); }
.verdict .label{ color:var(--gold2); font-weight:700; font-size:.75rem; letter-spacing:.14em; text-transform:uppercase; }
.verdict h2{ margin:.2rem 0 0; font-size:1.55rem; color:#fff; }
.gauges{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin-top:16px; }
.gauge{ min-width:210px; background:rgba(11,16,32,.55); border:1px solid var(--line); border-radius:16px; padding:14px 16px; }
.gauge .co{ font-weight:700; color:#fff; display:flex; justify-content:space-between; }
.gauge .score{ font-family:'Space Grotesk'; font-size:2rem; font-weight:700; color:var(--gold2); }
.bar{ height:8px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden; margin:6px 0 8px; }
.bar i{ display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,#F08A3E,#FFD27A); }
.gauge .meta{ color:var(--muted); font-size:.78rem; }

.side-h{ display:flex; align-items:center; gap:10px; font-family:'Space Grotesk'; font-size:1.3rem; font-weight:700; margin:4px 0 12px; }
.side-h .count{ font-size:.75rem; font-family:'Inter'; padding:3px 10px; border-radius:99px; background:rgba(255,255,255,.06); color:var(--muted); }
.claim{ position:relative; border-radius:16px; padding:14px 16px 14px 18px; margin-bottom:12px; background:var(--panel);
  border:1px solid var(--line); }
.claim:before{ content:""; position:absolute; left:0; top:12px; bottom:12px; width:4px; border-radius:4px; }
.claim.bull:before{ background:var(--bull); } .claim.bear:before{ background:var(--bear); }
.claim .top{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:8px; font-size:.78rem; }
.claim .id{ font-weight:800; color:#fff; }
.claim .text{ color:var(--text); line-height:1.55; font-size:.95rem; }
.pill{ white-space:nowrap; flex-shrink:0; border-radius:99px; padding:2px 10px; font-weight:600; font-size:.72rem; border:1px solid var(--line); color:var(--muted); }
.pill.ok{ color:#7CF0B9; background:rgba(47,208,138,.12); border-color:rgba(47,208,138,.3); }
.pill.bad{ color:#FFB1B1; background:rgba(255,107,107,.12); border-color:rgba(255,107,107,.35); }
.pill.co{ color:#BFD6FF; background:rgba(110,168,254,.12); border-color:rgba(110,168,254,.3); }
.pill.cite{ color:var(--gold2); background:rgba(245,184,61,.1); border-color:rgba(245,184,61,.3); font-family:monospace; }
.caught{ border-color:rgba(255,107,107,.4); background:linear-gradient(135deg,rgba(255,107,107,.12),rgba(255,107,107,.03)); }
.caught .t{ color:#FFB1B1; font-weight:700; margin-bottom:8px; }
.caught s{ color:#E7EAF3; opacity:.8; }
.reb{ border-left:3px solid var(--violet); }
.reb b{ color:#C9B8FF; }

.mgrid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:14px; }
.metric{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:14px 16px; }
.metric .lbl{ color:var(--muted); font-size:.8rem; display:flex; justify-content:space-between; gap:8px; }
.metric .val{ font-family:'Space Grotesk'; font-size:1.6rem; font-weight:700; color:#fff; margin:4px 0; }
.metric .prev{ color:var(--muted); font-size:.8rem; }
.delta{ font-weight:700; font-size:.78rem; padding:2px 8px; border-radius:99px; }
.delta.up{ color:#7CF0B9; background:rgba(47,208,138,.12); } .delta.down{ color:#FFB1B1; background:rgba(255,107,107,.12); }
.co-h{ font-family:'Space Grotesk'; font-weight:700; font-size:1.1rem; margin:10px 0 10px; color:#fff; }

.memo{ background:#F7F5EF; color:#1B2033; border-radius:18px; padding:28px 34px; box-shadow:0 20px 50px rgba(0,0,0,.35); }
.review{ border-color:rgba(245,184,61,.35); background:linear-gradient(135deg,rgba(245,184,61,.08),rgba(255,255,255,.02)); }
.review h3{ margin:0 0 4px; } .review p{ color:var(--muted); margin:0; }
.foot{ color:var(--muted); font-size:.8rem; text-align:center; margin-top:28px; }
</style>
"""

ICONS = {"guard": "🛡️", "planner": "🗺️", "researcher": "🔎", "quant": "🧮", "bull": "🐂", "bear": "🐻",
         "rebuttal": "⚔️", "verifier": "✅", "revise": "🔁", "judge": "⚖️", "writer": "✍️",
         "human_review": "🙋", "finalize": "💾", "refuse": "⛔"}
PIPELINE = ["guard", "planner", "researcher", "quant", "bull", "bear", "rebuttal", "verifier", "judge", "writer", "human_review"]
LABELS = {"guard": "Guardrail", "planner": "Planner", "researcher": "Researcher", "quant": "Quant", "bull": "Bull",
          "bear": "Bear", "rebuttal": "Rebuttal", "verifier": "Verifier", "revise": "Revise", "judge": "Judge",
          "writer": "Writer", "human_review": "You", "finalize": "Saved", "refuse": "Refused"}


def hero() -> str:
    return """
<div class="hero">
  <div class="eyebrow">Team 24 · Mastering Agentic AI · Demo Day</div>
  <h1>Deal<span>Room</span>: your AI investment committee</h1>
  <p>Seven agents plan, research, debate and fact-check SEC 10-K filings, then hand you a cited memo to approve.
  Every claim links to the filing page it came from.</p>
  <div class="chips">
    <div class="chip">📚 <b>Uber + Lyft</b> FY2021 10-K</div>
    <div class="chip">🧠 <b>7 agents</b> on LangGraph</div>
    <div class="chip">🔌 <b>MCP</b> tool server</div>
    <div class="chip">✅ <b>Verified</b> citations</div>
    <div class="chip">🙋 <b>Human</b> approval</div>
  </div>
</div>"""


def pipeline(trace: list[dict]) -> str:
    done = {}
    for t in trace:
        done[t["node"]] = done.get(t["node"], 0) + t["ms"]
    retried = "revise" in done
    parts = []
    for i, n in enumerate(PIPELINE):
        cls = "node done" if n in done else "node"
        if n == "verifier" and retried:
            cls = "node retry"
        ms = f"<small>{done[n] / 1000:.1f}s</small>" if n in done and done[n] >= 100 else ""
        extra = " ↺" if n == "verifier" and retried else ""
        parts.append(f'<div class="{cls}">{ICONS[n]} {LABELS[n]}{extra} {ms}</div>')
        if i < len(PIPELINE) - 1:
            parts.append('<span class="arrow">›</span>')
    return f'<div class="pipe">{"".join(parts)}</div>'


def verdict(judge: dict) -> str:
    gauges = []
    for s in judge.get("scores", []):
        pct = s["conviction"] / 5 * 100
        gauges.append(f"""<div class="gauge"><div class="co">{escape(s['company'])}<span class="pill">{escape(s['mandate'])}</span></div>
<div class="score">{s['conviction']}<span style="font-size:1rem;color:#9AA3BC"> / 5</span></div>
<div class="bar"><i style="width:{pct:.0f}%"></i></div>
<div class="meta">🐂 {s['supported_bull']} verified · 🐻 {s['supported_bear']} verified · 📈 {s['metrics_improved']}/{s['metrics_total']} metrics up</div></div>""")
    return f"""<div class="card verdict"><div><div class="label">⚖️ Committee verdict</div>
<h2>{escape(judge.get('verdict', ''))}</h2></div><div class="gauges">{''.join(gauges)}</div></div>"""


def claim(c: dict) -> str:
    status = {"supported": '<span class="pill ok">✓ verified</span>', "unsupported": '<span class="pill bad">✕ rejected</span>',
              "pending": '<span class="pill">pending</span>'}.get(c["status"], "")
    reason = ""
    if c["status"] != "supported" and c.get("reason"):
        reason = f'<div class="pill bad" style="margin-top:8px;display:inline-block">{escape(c["reason"])}</div>'
    return f"""<div class="claim {c['side']}"><div class="top"><span class="id">{escape(c['id'])}</span>
<span class="pill co">{escape(c['company'])}</span>{status}<span class="pill cite">{escape(c['evidence_id'])}</span>
<span style="color:#6B7493">{escape(c.get('by', ''))}</span></div><div class="text">{escape(c['text'])}</div>{reason}</div>"""


def side_header(icon: str, title: str, n: int) -> str:
    return f'<div class="side-h">{icon} {title} <span class="count">{n} claims</span></div>'


def caught(claims: list[dict], replaced_by: dict) -> str:
    rows = "".join(
        f'<div style="margin:6px 0"><s>{escape(c["text"])}</s><br><span style="color:#9AA3BC;font-size:.82rem">'
        f'{escape(c["id"])} · {escape(c["company"])} · {escape(c.get("reason", ""))} → replaced by '
        f'<b style="color:#7CF0B9">{escape(replaced_by.get(c["id"], "-"))}</b></span></div>' for c in claims)
    return f'<div class="card caught"><div class="t">🚨 Verifier caught {len(claims)} unsupported claim(s) and sent them back</div>{rows}</div>'


def rebuttal(reb: dict) -> str:
    return (f'<div class="card reb"><div class="side-h" style="font-size:1.1rem">⚔️ Rebuttal round</div>'
            f'<p><b>🐻 Bear:</b> {escape(reb["bear_rebuttal"])}</p><p style="margin:0"><b>🐂 Bull:</b> {escape(reb["bull_response"])}</p></div>')


def metric_grid(metrics: list[dict], fmt) -> str:
    out = []
    for company in sorted({m["company"] for m in metrics}):
        cards = []
        for m in [x for x in metrics if x["company"] == company]:
            up = m["improved"]
            pct = "" if m["yoy_pct"] is None else f"{m['yoy_pct']:+.0f}%"
            cards.append(f"""<div class="metric"><div class="lbl"><span>{escape(m['label'])}</span><span class="pill cite">p.{m['page']}</span></div>
<div class="val">{escape(fmt(m['fy2021'], m['unit']))}</div>
<div class="prev"><span class="delta {'up' if up else 'down'}">{'▲' if up else '▼'} {pct}</span> &nbsp;vs {escape(fmt(m['fy2020'], m['unit']))} in FY2020</div></div>""")
        out.append(f'<div class="co-h">{escape(company)}</div><div class="mgrid">{"".join(cards)}</div>')
    return "".join(out)


def review_header() -> str:
    return ('<div class="card review"><h3>🙋 Your call</h3><p>The committee is paused. Nothing is saved until you approve, '
            'ask the Writer for changes, or send a follow-up question.</p></div>')


def footer() -> str:
    return ('<div class="foot">DealRoom · Team 24 · Built with LangGraph, LangChain, MCP, Chroma, BM25 and Streamlit · '
            'Educational research assistant, not investment advice.</div>')

MEMO_CSS = """
<style>
.st-key-memo_paper{ background:#F7F5EF; border-radius:18px; padding:26px 32px; box-shadow:0 20px 50px rgba(0,0,0,.35); }
.st-key-memo_paper, .st-key-memo_paper p, .st-key-memo_paper li, .st-key-memo_paper td, .st-key-memo_paper th,
.st-key-memo_paper h1, .st-key-memo_paper h2, .st-key-memo_paper h3, .st-key-memo_paper h4, .st-key-memo_paper strong,
.st-key-memo_paper em, .st-key-memo_paper span{ color:#1B2033 !important; }
.st-key-memo_paper h2{ border-bottom:2px solid #F5B83D; padding-bottom:6px; }
.st-key-memo_paper table{ border-collapse:collapse; }
.st-key-memo_paper th{ background:#EDE7D8 !important; }
.st-key-memo_paper td, .st-key-memo_paper th{ border:1px solid #DDD5C2 !important; }
.st-key-memo_paper hr{ border-color:#DDD5C2; }
</style>
"""
