"""Visual layer for the Streamlit app: theme CSS and small HTML components.

Design rules follow elayadesign/ai-design-skills (landing-page-design, Part B): one typeface (Geist, with Geist Mono
for figures and citations), Tailwind type scale, a fixed spacing scale, flat light surfaces, Phosphor icons and a single
weighted easing curve.
"""
from __future__ import annotations

from html import escape

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap');
@import url('https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css');
@import url('https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css');
:root{
  /* Core colours (figma-designer two-layer tokens) */
  --grayscale-50:#F7F8FC; --grayscale-100:#EEF0F7; --grayscale-200:#E3E6F0; --grayscale-400:#9AA0BD;
  --grayscale-600:#5A6082; --grayscale-900:#151833;
  --primary-500:#4F46E5; --primary-600:#4338CA; --primary-50:#EEF0FF;
  --amber-500:#E8A317; --amber-600:#B7791F; --amber-50:#FFF7E6;
  /* Colour system (aliases) */
  --bg:var(--grayscale-50); --side:rgba(255,255,255,.86); --panel:rgba(255,255,255,.92); --panel2:var(--grayscale-50);
  --raise:var(--grayscale-100); --line:var(--grayscale-200);
  --text:var(--grayscale-900); --muted:var(--grayscale-600); --dim:var(--grayscale-400);
  --accent:var(--primary-500); --accent2:var(--primary-600); --gold:var(--amber-500); --gold2:var(--amber-600);
  --bull:#059669; --bear:#DC2626; --blue:#2563EB; --violet:#7C3AED; --cyan:#0891B2;
  --shadow:0 1px 2px rgba(21,24,51,.04), 0 8px 24px rgba(21,24,51,.06);
  --shadow-lg:0 2px 4px rgba(21,24,51,.05), 0 18px 40px rgba(79,70,229,.12);
  /* spacing tokens */
  --s25:2px; --s50:4px; --s75:8px; --s100:12px; --s200:16px; --s300:24px; --s400:32px; --s500:40px; --s600:48px; --s700:64px;
  --ease:cubic-bezier(0.22,1,0.36,1);
  --mono:'Geist Mono',ui-monospace,monospace;
}
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select, label,
h1, h2, h3, h4, h5, h6, p, li, td, th { font-family:'Geist',system-ui,sans-serif !important; font-style:normal !important; }
[class^="ph"], [class*=" ph"]{ font-family:'Phosphor','Phosphor-Fill' !important; }
.ph-fill{ font-family:'Phosphor-Fill' !important; }
em, i:not([class]){ font-style:normal !important; }
h1, h2, h3, h4, h5, h6{ font-weight:600 !important; letter-spacing:-0.01em; text-wrap:balance; color:var(--text); }
p, li{ text-wrap:pretty; }
code, pre, kbd{ font-family:var(--mono) !important; }

/* page: flat light colour with a dotted SVG texture (B4: no gradient fills on surfaces) */
.stApp{ background-color:var(--bg);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24'%3E%3Ccircle cx='2' cy='2' r='1' fill='%23D5D9E8'/%3E%3C/svg%3E"); }
[data-testid="stHeader"]{ background:transparent; }
.stAppDeployButton, [data-testid="stAppDeployButton"]{ display:none; }
.block-container{ padding-top:var(--s400); max-width:1280px; }
[data-testid="stMain"] .block-container{ position:relative; z-index:1; }
[data-testid="stSidebar"]{ background:var(--side); border-right:1px solid var(--line); z-index:2;
  -webkit-backdrop-filter:blur(16px); backdrop-filter:blur(16px); }
[data-testid="stSidebar"] > div{ background:transparent; }
[data-testid="stSidebar"] .stMarkdown p{ color:var(--muted); }
[data-testid="stSidebar"] h2{ font-size:20px; line-height:28px; }
[data-testid="stSidebar"] h4{ font-size:12px; line-height:16px; font-weight:500 !important; letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); margin-top:var(--s300); }
.brand{ display:flex; align-items:center; gap:var(--s100); margin-bottom:var(--s50); }
.brand .mark{ width:40px; height:40px; border-radius:12px; display:grid; place-items:center; background:var(--accent);
  color:#fff; font-size:24px; box-shadow:0 6px 16px rgba(79,70,229,.3); }
.brand .name{ font-size:20px; line-height:28px; font-weight:600; color:var(--text); }
.brand .sub{ font-size:12px; line-height:16px; color:var(--muted); }

/* buttons */
.stButton>button, .stDownloadButton>button{ border-radius:12px; border:1px solid var(--line); background:#fff;
  color:var(--text); font-weight:600; font-size:14px; line-height:20px; padding:var(--s75) var(--s100); box-shadow:var(--shadow);
  transition:background-color 300ms var(--ease), border-color 300ms var(--ease), color 300ms var(--ease), transform 500ms var(--ease), box-shadow 300ms var(--ease); }
.stButton>button:hover, .stDownloadButton>button:hover{ border-color:var(--accent); color:var(--accent); transform:translateY(-1px); box-shadow:var(--shadow-lg); }
.stButton>button:active, .stDownloadButton>button:active{ transform:scale(0.98); }
.stButton>button:focus-visible, .stDownloadButton>button:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }
.stButton>button[kind="primary"]{ background:var(--accent); color:#fff; border:1px solid var(--accent); font-size:16px; line-height:24px;
  box-shadow:0 8px 20px rgba(79,70,229,.28); }
.stButton>button[kind="primary"]:hover{ background:var(--accent2); border-color:var(--accent2); color:#fff; }
.stButton>button[kind="primary"] p{ color:#fff !important; }
.stButton>button:disabled{ opacity:.45; transform:none; }
textarea, input{ border-radius:12px !important; }
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"]>div{ border-radius:12px !important; background:#fff !important;
  border-color:var(--line) !important; transition:border-color 300ms var(--ease); }
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within{ border-color:var(--accent) !important; box-shadow:0 0 0 3px var(--primary-50); }
textarea{ font-size:16px !important; line-height:24px !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"], [data-testid="stTabs"] [role="tablist"]{ gap:var(--s50); background:#fff; padding:var(--s50);
  border-radius:16px; border:1px solid var(--line); width:fit-content; max-width:100%; box-shadow:var(--shadow); }
.stTabs [data-baseweb="tab"], [data-testid="stTabs"] [role="tab"]{ border-radius:12px; padding:var(--s75) var(--s200); color:var(--muted);
  font-weight:500; font-size:14px; line-height:20px; height:auto; transition:background-color 300ms var(--ease), color 300ms var(--ease); }
.stTabs [data-baseweb="tab"]:hover{ color:var(--text); }
.stTabs [aria-selected="true"], [data-testid="stTabs"] [role="tab"][aria-selected="true"]{ background:var(--accent) !important; color:#fff !important; }
.stTabs [aria-selected="true"] p{ color:#fff !important; }
.stTabs [role="tab"]{ flex-shrink:0; } .stTabs [role="tab"] p{ white-space:nowrap; }
[data-testid="stTabs"] [role="tablist"]{ overflow-x:auto; scrollbar-width:none; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none; }
[data-testid="stExpander"] details{ border:1px solid var(--line); border-radius:16px; background:var(--panel); box-shadow:var(--shadow); }
[data-testid="stExpander"] summary{ font-size:14px; line-height:20px; }
[data-testid="stExpander"] pre, [data-testid="stText"]{ font-family:var(--mono) !important; font-size:12px; line-height:16px; }
[data-testid="stStatusWidget"], [data-testid="stStatus"]{ border-radius:16px; }
[data-testid="stAlert"]{ border-radius:16px; }
div[data-testid="stVerticalBlockBorderWrapper"]{ border-radius:16px; }
[data-testid="stDataFrame"], [data-testid="stTable"]{ background:#fff; border-radius:16px; }

/* entrance: rise 32px and fade on the base curve */
@keyframes rise{ from{ opacity:0; transform:translateY(32px); } to{ opacity:1; transform:none; } }
.hero, .card, .claim, .metric, .pipe{ animation:rise 700ms var(--ease) both; }
.claim:nth-child(2){ animation-delay:60ms; } .claim:nth-child(3){ animation-delay:120ms; }
.claim:nth-child(4){ animation-delay:180ms; } .claim:nth-child(n+5){ animation-delay:240ms; }

/* shared surface: white cards, full borders, soft shadow */
.hero, .card, .claim, .metric, .pipe, .gauge, .usage .u{ background:var(--panel); border:1px solid var(--line); box-shadow:var(--shadow); }

/* hero */
.hero{ border-radius:24px; padding:var(--s600) var(--s500); margin-bottom:var(--s300); position:relative; overflow:hidden;
  display:grid; grid-template-columns:minmax(0,1fr) 260px; gap:var(--s400); align-items:center; }
.hero::before{ content:""; position:absolute; inset:0 0 auto 0; height:4px;
  background:linear-gradient(90deg,var(--accent),var(--violet),var(--gold)); }
.hero .eyebrow{ display:inline-flex; align-items:center; gap:var(--s75); color:var(--accent); font-weight:500; font-size:12px; line-height:16px;
  letter-spacing:.08em; text-transform:uppercase; padding:var(--s50) var(--s100); border-radius:9999px; background:var(--primary-50);
  border:1px solid rgba(79,70,229,.2); }
.hero h1{ font-size:48px; line-height:48px; font-weight:600; margin:var(--s300) 0 var(--s200); padding:0; max-width:680px;
  background:linear-gradient(90deg,#000000,#666666); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p{ color:var(--muted); font-size:18px; line-height:28px; max-width:680px; margin:0; }
.chips{ display:flex; flex-wrap:wrap; gap:var(--s75); margin-top:var(--s400); }
.chip{ display:inline-flex; align-items:center; gap:var(--s75); background:#fff; border:1px solid var(--line); border-radius:9999px;
  padding:var(--s75) var(--s100); font-size:14px; line-height:20px; color:var(--muted);
  transition:border-color 300ms var(--ease), transform 500ms var(--ease); }
.chip:hover{ border-color:var(--accent); transform:translateY(-2px); }
.chip i{ color:var(--accent); font-size:16px; }
.chip:nth-child(2) i{ color:var(--violet); } .chip:nth-child(3) i{ color:var(--cyan); }
.chip:nth-child(4) i{ color:var(--bull); } .chip:nth-child(5) i{ color:var(--gold2); }
.chip b{ color:var(--text); font-weight:500; }

/* hero visual: a slowly turning glass cube of icons */
.scene{ width:260px; height:260px; perspective:900px; display:grid; place-items:center; }
.cube{ position:relative; width:140px; height:140px; transform-style:preserve-3d; animation:cube 18s linear infinite; }
.cube .f{ position:absolute; inset:0; display:grid; place-items:center; border-radius:16px; font-size:48px; color:var(--accent);
  border:1px solid rgba(79,70,229,.25); background:rgba(238,240,255,.85); box-shadow:inset 0 0 30px rgba(79,70,229,.10); }
.cube .f.g{ background:rgba(255,247,230,.92); color:var(--gold2); border-color:rgba(232,163,23,.35); }
.cube .f3, .cube .f4{ color:var(--violet); }
.cube .f1{ transform:translateZ(70px); } .cube .f2{ transform:rotateY(180deg) translateZ(70px); }
.cube .f3{ transform:rotateY(90deg) translateZ(70px); } .cube .f4{ transform:rotateY(-90deg) translateZ(70px); }
.cube .f5{ transform:rotateX(90deg) translateZ(70px); } .cube .f6{ transform:rotateX(-90deg) translateZ(70px); }
.scene .shadow{ position:absolute; width:150px; height:24px; margin-top:220px; border-radius:50%;
  background:radial-gradient(ellipse, rgba(79,70,229,.25), transparent 70%); filter:blur(4px); }
@keyframes cube{ from{ transform:rotateX(-22deg) rotateY(0deg); } to{ transform:rotateX(-22deg) rotateY(360deg); } }

/* section label */
.sec{ display:flex; align-items:center; gap:var(--s75); font-size:14px; line-height:20px; font-weight:500; color:var(--muted); margin:var(--s200) 0 var(--s75); }
.sec i{ color:var(--accent); font-size:16px; width:24px; height:24px; border-radius:8px; display:grid; place-items:center; background:var(--primary-50); }

/* pipeline */
.pipe{ display:flex; flex-wrap:wrap; align-items:center; gap:var(--s75); margin:var(--s75) 0 var(--s300); padding:var(--s100); border-radius:16px; }
.node{ display:flex; align-items:center; gap:var(--s50); padding:var(--s50) var(--s100); border-radius:8px; background:var(--panel2);
  border:1px solid var(--line); font-size:12px; line-height:16px; font-weight:500; color:var(--dim); }
.node i{ font-size:16px; }
.node.done{ color:var(--text); border-color:rgba(5,150,105,.3); background:#ECFDF5; }
.node.done i{ color:var(--bull); }
.node.retry{ border-color:rgba(220,38,38,.35); background:#FEF2F2; color:var(--text); }
.node.retry i{ color:var(--bear); }
.node small{ color:var(--muted); font-size:12px; font-family:var(--mono); }
.arrow{ color:var(--dim); font-size:12px; }

/* cards */
.card{ border-radius:16px; padding:var(--s300); margin-bottom:var(--s200); }
.verdict{ border-color:rgba(79,70,229,.25); position:relative; overflow:hidden; }
.verdict::before{ content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--accent); }
.verdict .label{ display:flex; align-items:center; gap:var(--s75); color:var(--accent); font-weight:500; font-size:12px; line-height:16px;
  letter-spacing:.08em; text-transform:uppercase; }
.verdict h2{ margin:var(--s75) 0 0; padding:0; font-size:24px; line-height:32px; color:var(--text); max-width:880px; }
.gauges{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:var(--s200); margin-top:var(--s300); }
.gauge{ background:var(--panel2); border-radius:12px; padding:var(--s200); box-shadow:none; }
.gauge .co{ font-weight:500; font-size:16px; line-height:24px; color:var(--text); display:flex; justify-content:space-between; align-items:center; }
.gauge .score{ font-family:var(--mono); font-size:36px; line-height:40px; font-weight:600; color:var(--accent); margin-top:var(--s75); }
.gauge .score span{ font-size:16px; color:var(--muted); }
.bar{ height:8px; border-radius:9999px; background:var(--grayscale-200); overflow:hidden; margin:var(--s75) 0 var(--s100); }
.bar i{ display:block; height:100%; border-radius:9999px; background:linear-gradient(90deg,var(--accent),var(--violet));
  transform-origin:left; animation:grow 800ms var(--ease) both; }
@keyframes grow{ from{ transform:scaleX(0); } to{ transform:scaleX(1); } }
.gauge .meta{ display:flex; flex-wrap:wrap; gap:var(--s100); color:var(--muted); font-size:12px; line-height:16px; }
.gauge .meta span{ display:inline-flex; align-items:center; gap:var(--s50); }

.side-h{ display:flex; align-items:center; gap:var(--s100); font-size:20px; line-height:28px; font-weight:600; color:var(--text); margin:var(--s50) 0 var(--s200); }
.side-h .ico{ width:32px; height:32px; border-radius:8px; display:grid; place-items:center; font-size:20px; }
.side-h .ico.bull{ background:#D1FAE5; color:var(--bull); } .side-h .ico.bear{ background:#FEE2E2; color:var(--bear); }
.side-h .ico.reb{ background:#EDE9FE; color:var(--violet); }
.side-h .count{ font-size:12px; line-height:16px; font-weight:500; padding:var(--s50) var(--s75); border-radius:9999px; background:var(--panel2);
  border:1px solid var(--line); color:var(--muted); }
.claim{ border-radius:16px; padding:var(--s200); margin-bottom:var(--s100);
  transition:border-color 300ms var(--ease), transform 500ms var(--ease), box-shadow 300ms var(--ease); }
.claim.bull{ box-shadow:inset 3px 0 0 var(--bull), var(--shadow); } .claim.bear{ box-shadow:inset 3px 0 0 var(--bear), var(--shadow); }
.claim:hover{ transform:translateY(-3px); }
.claim.bull:hover{ border-color:rgba(5,150,105,.4); } .claim.bear:hover{ border-color:rgba(220,38,38,.4); }
.claim .top{ display:flex; gap:var(--s75); align-items:center; flex-wrap:wrap; margin-bottom:var(--s100); font-size:12px; line-height:16px; }
.claim .dot{ width:8px; height:8px; border-radius:9999px; }
.claim.bull .dot{ background:var(--bull); } .claim.bear .dot{ background:var(--bear); }
.claim .id{ font-weight:600; color:var(--text); font-family:var(--mono); }
.claim .by{ color:var(--dim); }
.claim .text{ color:var(--text); font-size:14px; line-height:20px; }
.pill{ display:inline-flex; align-items:center; gap:var(--s50); white-space:nowrap; flex-shrink:0; border-radius:9999px; padding:var(--s25) var(--s75);
  font-weight:500; font-size:12px; line-height:16px; border:1px solid var(--line); color:var(--muted); background:#fff; }
.pill.ok{ color:#047857; background:#ECFDF5; border-color:#A7F3D0; }
.pill.bad{ color:#B91C1C; background:#FEF2F2; border-color:#FECACA; }
.pill.co{ color:#1D4ED8; background:#EFF6FF; border-color:#BFDBFE; }
.pill.cite{ color:var(--gold2); background:var(--amber-50); border-color:#FCE3A7; font-family:var(--mono); }
.reason{ margin-top:var(--s75); }
.caught{ border-color:#FECACA; }
.caught .t{ display:flex; align-items:center; gap:var(--s75); color:#B91C1C; font-weight:600; font-size:16px; line-height:24px; margin-bottom:var(--s100); }
.caught .row{ padding:var(--s100); border-radius:12px; background:#FEF2F2; border:1px solid #FEE2E2; margin-top:var(--s75); }
.caught s{ color:var(--text); opacity:.7; font-size:14px; line-height:20px; }
.caught .meta{ color:var(--muted); font-size:12px; line-height:16px; margin-top:var(--s50); }
.caught .meta b{ color:#047857; font-family:var(--mono); }
.reb{ border-color:#DDD6FE; }
.reb p{ font-size:14px; line-height:20px; color:var(--text); }
.reb p b{ color:var(--violet); font-weight:600; }

.mgrid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(232px,1fr)); gap:var(--s200); margin-bottom:var(--s300); }
.metric{ border-radius:16px; padding:var(--s200); transition:border-color 300ms var(--ease), transform 500ms var(--ease), box-shadow 300ms var(--ease); }
.metric:hover{ border-color:rgba(79,70,229,.35); transform:translateY(-3px); box-shadow:var(--shadow-lg); }
.metric .lbl{ color:var(--muted); font-size:14px; line-height:20px; display:flex; justify-content:space-between; align-items:center; gap:var(--s75); }
.metric .val{ font-family:var(--mono); font-size:30px; line-height:36px; font-weight:600; color:var(--text); margin:var(--s75) 0; }
.metric .prev{ color:var(--muted); font-size:12px; line-height:16px; display:flex; align-items:center; gap:var(--s75); }
.delta{ display:inline-flex; align-items:center; gap:var(--s25); font-weight:600; font-size:12px; line-height:16px; padding:var(--s25) var(--s75);
  border-radius:9999px; font-family:var(--mono); }
.delta.up{ color:#047857; background:#D1FAE5; } .delta.down{ color:#B91C1C; background:#FEE2E2; }
.co-h{ display:flex; align-items:center; gap:var(--s75); font-weight:600; font-size:20px; line-height:28px; margin:var(--s200) 0 var(--s100); color:var(--text); }
.co-h i{ color:var(--accent); width:32px; height:32px; border-radius:8px; display:grid; place-items:center; background:var(--primary-50); }

.usage{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:var(--s100); margin:var(--s75) 0 var(--s300); }
.usage .u{ display:flex; align-items:center; gap:var(--s75); padding:var(--s100) var(--s200); border-radius:12px; font-size:12px; line-height:16px; color:var(--muted); }
.usage .u i{ color:var(--accent); font-size:16px; }
.usage .u b{ font-family:var(--mono); font-size:16px; line-height:24px; font-weight:600; color:var(--text); }
.review{ display:flex; gap:var(--s200); align-items:flex-start; border-color:rgba(232,163,23,.4); background:#FFFBF0; margin-top:var(--s400); }
.review .ico{ width:40px; height:40px; border-radius:12px; display:grid; place-items:center; background:var(--gold); color:#fff; font-size:24px; flex-shrink:0; }
.review h3{ margin:0 0 var(--s50); padding:0; font-size:20px; line-height:28px; }
.review p{ color:var(--muted); margin:0; font-size:14px; line-height:20px; }
.foot{ display:flex; justify-content:center; flex-wrap:wrap; gap:var(--s75); color:var(--muted); font-size:12px; line-height:16px;
  text-align:center; margin-top:var(--s700); padding-top:var(--s300); border-top:1px solid var(--line); }

/* ---------- decorative background: soft colour blobs and floating finance symbols ---------- */
.bg-deco{ position:fixed; inset:0; z-index:-1; pointer-events:none; overflow:hidden; }
.bg-deco .blob{ position:absolute; width:46vmax; height:46vmax; border-radius:50%; filter:blur(80px); opacity:.35; }
.bg-deco .b1{ left:-16vmax; top:-18vmax; background:#C7D2FE; }
.bg-deco .b2{ right:-18vmax; top:20vh; background:#E9D5FF; opacity:.3; }
.bg-deco .b3{ left:30vw; bottom:-30vmax; background:#FDE68A; opacity:.25; }
.bg-deco .s{ position:absolute; color:var(--accent); opacity:.16; animation:drift 12s var(--ease) infinite alternate; }
.bg-deco .s:nth-child(3n){ color:var(--violet); opacity:.11; }
.bg-deco .s:nth-child(4n){ color:var(--gold2); opacity:.14; }
.bg-deco .s:nth-child(5n){ color:var(--bull); opacity:.11; }
@keyframes drift{ from{ transform:translateY(0) rotate(0deg); } to{ transform:translateY(-24px) rotate(8deg); } }

@media (max-width: 900px){ .hero{ grid-template-columns:1fr; padding:var(--s400) var(--s300); } .scene{ display:none; }
  .hero h1{ font-size:36px; line-height:40px; } }
@media (prefers-reduced-motion: reduce){
  .hero, .card, .claim, .metric, .pipe{ animation:fade 300ms linear both; }
  @keyframes fade{ from{ opacity:0; } to{ opacity:1; } }
  .stButton>button:hover, .claim:hover, .metric:hover, .chip:hover{ transform:none; }
  .bg-deco .s, .cube, .bar i{ animation:none !important; }
}
</style>
"""

# Decorative finance symbols behind the content: (Phosphor icon, left %, top %, size px). aria-hidden, no pointer events.
_SYMBOLS = [("chart-line-up", 6, 14, 56), ("currency-dollar", 88, 10, 48), ("file-text", 18, 62, 44), ("percent", 74, 44, 40),
            ("bank", 93, 72, 52), ("coins", 4, 86, 44), ("receipt", 52, 90, 40), ("trend-up", 40, 6, 36),
            ("chart-pie-slice", 64, 22, 44), ("calculator", 30, 38, 36), ("presentation-chart", 84, 92, 48),
            ("briefcase", 12, 40, 36), ("handshake", 58, 64, 40), ("scales", 96, 34, 40), ("car-simple", 26, 78, 40),
            ("magnifying-glass", 46, 30, 36), ("gavel", 78, 58, 40), ("book-open", 36, 96, 44), ("target", 70, 4, 36),
            ("database", 2, 52, 40), ("trend-down", 48, 50, 32), ("chart-bar", 98, 54, 36), ("seal-check", 20, 20, 32),
            ("piggy-bank", 66, 80, 44), ("money", 14, 4, 36)]
BACKGROUND = ('<div class="bg-deco" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>'
              + "".join(f'<i class="ph ph-{n} s" style="left:{x}%;top:{y}%;font-size:{size}px;animation-delay:-{i * 0.8:.1f}s"></i>'
                        for i, (n, x, y, size) in enumerate(_SYMBOLS)) + "</div>")

ICONS = {"guard": "🛡️", "planner": "🗺️", "researcher": "🔎", "quant": "🧮", "bull": "🐂", "bear": "🐻",
         "rebuttal": "⚔️", "verifier": "✅", "revise": "🔁", "judge": "⚖️", "writer": "✍️",
         "human_review": "🙋", "finalize": "💾", "refuse": "⛔"}
PH = {"guard": "shield-check", "planner": "map-trifold", "researcher": "magnifying-glass", "quant": "calculator",
      "bull": "trend-up", "bear": "trend-down", "rebuttal": "swap", "verifier": "seal-check", "revise": "arrow-counter-clockwise",
      "judge": "scales", "writer": "pen-nib", "human_review": "user-check", "finalize": "floppy-disk", "refuse": "prohibit"}
PIPELINE = ["guard", "planner", "researcher", "quant", "bull", "bear", "rebuttal", "verifier", "judge", "writer", "human_review"]
LABELS = {"guard": "Guardrail", "planner": "Planner", "researcher": "Researcher", "quant": "Quant", "bull": "Bull",
          "bear": "Bear", "rebuttal": "Rebuttal", "verifier": "Verifier", "revise": "Revise", "judge": "Judge",
          "writer": "Writer", "human_review": "You", "finalize": "Saved", "refuse": "Refused"}


def icon(name: str, fill: bool = False) -> str:
    return f'<i class="{"ph-fill" if fill else "ph"} ph-{name}" aria-hidden="true"></i>'


def brand() -> str:
    return (f'<div class="brand"><div class="mark">{icon("bank", True)}</div><div><div class="name">DealRoom</div>'
            '<div class="sub">AI investment committee · Team 24</div></div></div>')


def section(ico: str, text: str) -> str:
    return f'<div class="sec">{icon(ico)} {escape(text)}</div>'


def hero() -> str:
    chips = [("files", "Uber and Lyft", "FY2021 10‑K"), ("graph", "7 agents", "on LangGraph"),
             ("plugs-connected", "MCP", "tool server"), ("seal-check", "Verified", "citations"),
             ("user-check", "Human", "approval")]
    chip_html = "".join(f'<div class="chip">{icon(i)} <b>{b}</b> {t}</div>' for i, b, t in chips)
    faces = [("f1 g", "bank"), ("f2", "scales"), ("f3", "trend-up"), ("f4", "trend-down"), ("f5", "seal-check"),
             ("f6", "magnifying-glass")]
    cube = "".join(f'<div class="f {cls}">{icon(name, True)}</div>' for cls, name in faces)
    return f"""
<div class="hero">
  <div>
    <div class="eyebrow">{icon("sparkle", True)} Team 24 · Mastering Agentic AI · Demo Day</div>
    <h1>Your AI investment committee<br>for SEC filings</h1>
    <p>Seven agents plan, research, debate and fact check 10‑K filings, then hand you a cited memo to approve.
    Every claim links to the filing page it came from.</p>
    <div class="chips">{chip_html}</div>
  </div>
  <div class="scene" aria-hidden="true"><div class="cube">{cube}</div><div class="shadow"></div></div>
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
        parts.append(f'<div class="{cls}">{icon(PH[n])} {LABELS[n]}{extra} {ms}</div>')
        if i < len(PIPELINE) - 1:
            parts.append(f'<span class="arrow">{icon("caret-right")}</span>')
    return f'<div class="pipe">{"".join(parts)}</div>'


def verdict(judge: dict) -> str:
    gauges = []
    for s in judge.get("scores", []):
        pct = s["conviction"] / 5 * 100
        gauges.append(f"""<div class="gauge"><div class="co">{escape(s['company'])}<span class="pill">{escape(s['mandate'])}</span></div>
<div class="score">{s['conviction']}<span> / 5</span></div>
<div class="bar"><i style="width:{pct:.0f}%"></i></div>
<div class="meta"><span>{icon("trend-up")} {s['supported_bull']} bull verified</span><span>{icon("trend-down")} {s['supported_bear']} bear verified</span>
<span>{icon("chart-line-up")} {s['metrics_improved']}/{s['metrics_total']} metrics up</span></div></div>""")
    return f"""<div class="card verdict"><div><div class="label">{icon("scales")} Committee verdict</div>
<h2>{escape(judge.get('verdict', ''))}</h2></div><div class="gauges">{''.join(gauges)}</div></div>"""


def claim(c: dict) -> str:
    status = {"supported": f'<span class="pill ok">{icon("check")} verified</span>',
              "unsupported": f'<span class="pill bad">{icon("x")} rejected</span>',
              "pending": '<span class="pill">pending</span>'}.get(c["status"], "")
    reason = ""
    if c["status"] != "supported" and c.get("reason"):
        reason = f'<div class="reason"><span class="pill bad">{escape(c["reason"])}</span></div>'
    return f"""<div class="claim {c['side']}"><div class="top"><span class="dot"></span><span class="id">{escape(c['id'])}</span>
<span class="pill co">{escape(c['company'])}</span>{status}<span class="pill cite">{escape(c['evidence_id'])}</span>
<span class="by">{escape(c.get('by', ''))}</span></div><div class="text">{escape(c['text'])}</div>{reason}</div>"""


def side_header(side: str, title: str, n: int) -> str:
    ico = {"bull": "trend-up", "bear": "trend-down"}[side]
    return f'<div class="side-h"><span class="ico {side}">{icon(ico)}</span>{title} <span class="count">{n} claims</span></div>'


def caught(claims: list[dict], replaced_by: dict) -> str:
    rows = "".join(
        f'<div class="row"><s>{escape(c["text"])}</s><div class="meta">'
        f'{escape(c["id"])} · {escape(c["company"])} · {escape(c.get("reason", ""))} → replaced by '
        f'<b>{escape(replaced_by.get(c["id"], "none"))}</b></div></div>' for c in claims)
    return (f'<div class="card caught"><div class="t">{icon("warning-octagon", True)} Verifier caught {len(claims)} unsupported '
            f'claim(s) and sent them back</div>{rows}</div>')


def rebuttal(reb: dict) -> str:
    return (f'<div class="card reb"><div class="side-h"><span class="ico reb">{icon("swap")}</span>Rebuttal round</div>'
            f'<p><b>Bear:</b> {escape(reb["bear_rebuttal"])}</p><p style="margin:0"><b>Bull:</b> {escape(reb["bull_response"])}</p></div>')


def metric_grid(metrics: list[dict], fmt) -> str:
    out = []
    for company in sorted({m["company"] for m in metrics}):
        cards = []
        for m in [x for x in metrics if x["company"] == company]:
            up = m["improved"]
            pct = "" if m["yoy_pct"] is None else f"{m['yoy_pct']:+.0f}%"
            cards.append(f"""<div class="metric"><div class="lbl"><span>{escape(m['label'])}</span><span class="pill cite">p.{m['page']}</span></div>
<div class="val">{escape(fmt(m['fy2021'], m['unit']))}</div>
<div class="prev"><span class="delta {'up' if up else 'down'}">{icon('arrow-up-right' if up else 'arrow-down-right')} {pct}</span>vs {escape(fmt(m['fy2020'], m['unit']))} in FY2020</div></div>""")
        out.append(f'<div class="co-h">{icon("buildings")} {escape(company)}</div><div class="mgrid">{"".join(cards)}</div>')
    return "".join(out)


def usage_strip(t: dict) -> str:
    """Run totals for the Agent log: time, LLM calls, tokens and estimated cost."""
    cells = [("timer", f"{t['ms'] / 1000:.1f}s", "agent time"), ("cpu", str(t["llm_calls"]), "LLM calls"),
             ("coins", f"{t['tokens_in'] + t['tokens_out']:,}", "tokens"), ("currency-dollar", f"${t['cost_usd']:.4f}", "est. cost")]
    return '<div class="usage">' + "".join(
        f'<div class="u">{icon(i)}<b>{v}</b><span>{label}</span></div>' for i, v, label in cells) + "</div>"


def review_header() -> str:
    return (f'<div class="card review"><div class="ico">{icon("user-check", True)}</div><div><h3>Your call</h3>'
            '<p>The committee is paused. Nothing is saved until you approve, ask the Writer for changes, '
            'or send a follow up question.</p></div></div>')


def footer() -> str:
    return ('<div class="foot"><span>DealRoom · Team 24</span><span>·</span><span>LangGraph, LangChain, MCP, Chroma, BM25 and Streamlit</span>'
            '<span>·</span><span>Educational research assistant, not investment advice</span></div>')

MEMO_CSS = """
<style>
.st-key-memo_paper{ background:#FFFFFF; border:1px solid var(--line); box-shadow:var(--shadow); border-radius:16px; padding:var(--s400) var(--s500); }
.st-key-memo_paper, .st-key-memo_paper p, .st-key-memo_paper li, .st-key-memo_paper td, .st-key-memo_paper th,
.st-key-memo_paper h1, .st-key-memo_paper h2, .st-key-memo_paper h3, .st-key-memo_paper h4, .st-key-memo_paper strong,
.st-key-memo_paper em, .st-key-memo_paper span{ color:#131209 !important; }
.st-key-memo_paper p, .st-key-memo_paper li{ font-size:16px; line-height:24px; }
.st-key-memo_paper h2{ font-size:24px; line-height:32px; padding-bottom:var(--s75); box-shadow:0 2px 0 var(--gold); margin-bottom:var(--s200); }
.st-key-memo_paper table{ border-collapse:collapse; }
.st-key-memo_paper th{ background:#EDE7D8 !important; }
.st-key-memo_paper td, .st-key-memo_paper th{ border:1px solid #DDD5C2 !important; font-size:14px; line-height:20px; }
.st-key-memo_paper hr{ border-color:#DDD5C2; }
</style>
"""
