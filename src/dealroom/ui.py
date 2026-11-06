"""Visual layer for the Streamlit app: theme CSS and small HTML components.

Design rules follow elayadesign/ai-design-skills (landing-page-design, Part B): one typeface (Geist, with Geist Mono
for figures and citations), Tailwind type scale, a fixed spacing scale, flat dark surfaces, Phosphor icons and a single
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
  /* midnight indigo base with translucent glass surfaces over a 3D background */
  --bg:#070B24; --side:rgba(10,14,42,.72); --panel:rgba(22,28,72,.52); --panel2:rgba(34,40,96,.55);
  --raise:rgba(60,66,140,.6); --line:rgba(148,163,255,.16);
  --text:#EEF0FF; --muted:#A3A9D6; --dim:#6E74A8; --cyan:#22D3EE; --glass-blur:blur(8px);
  --gold:#F5B83D; --gold2:#FFD27A; --bull:#2FD08A; --bear:#FF6B6B; --blue:#6EA8FE; --violet:#A78BFA;
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
h1, h2, h3, h4, h5, h6{ font-weight:600 !important; letter-spacing:-0.01em; text-wrap:balance; }
p, li{ text-wrap:pretty; }
code, pre, kbd{ font-family:var(--mono) !important; }

.stApp{ background:var(--bg); }
[data-testid="stHeader"]{ background:transparent; }
.stAppDeployButton, [data-testid="stAppDeployButton"]{ display:none; }
.block-container{ padding-top:var(--s400); max-width:1280px; }
[data-testid="stSidebar"]{ background:var(--side); border-right:none; box-shadow:inset -1px 0 0 var(--line); }
[data-testid="stSidebar"] .stMarkdown p{ color:var(--muted); }
[data-testid="stSidebar"] h2{ font-size:20px; line-height:28px; }
[data-testid="stSidebar"] h4{ font-size:12px; line-height:16px; font-weight:500 !important; letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); margin-top:var(--s300); }
.brand{ display:flex; align-items:center; gap:var(--s100); margin-bottom:var(--s50); }
.brand .mark{ width:40px; height:40px; border-radius:12px; display:grid; place-items:center; background:var(--gold);
  color:#131209; font-size:24px; }
.brand .name{ font-size:20px; line-height:28px; font-weight:600; color:#fff; }
.brand .sub{ font-size:12px; line-height:16px; color:var(--muted); }

/* buttons */
.stButton>button, .stDownloadButton>button{ border-radius:12px; border:1px solid var(--line); background:var(--panel2);
  color:var(--text); font-weight:600; font-size:14px; line-height:20px; padding:var(--s75) var(--s100);
  transition:background-color 300ms var(--ease), border-color 300ms var(--ease), color 300ms var(--ease), transform 500ms var(--ease); }
.stButton>button:hover, .stDownloadButton>button:hover{ background:var(--raise); border-color:var(--gold); color:var(--gold2); transform:translateY(-1px); }
.stButton>button:active, .stDownloadButton>button:active{ transform:scale(0.98); }
.stButton>button:focus-visible, .stDownloadButton>button:focus-visible{ outline:2px solid var(--gold); outline-offset:2px; }
.stButton>button[kind="primary"]{ background:var(--gold); color:#131209; border:1px solid var(--gold); font-size:16px; line-height:24px; }
.stButton>button[kind="primary"]:hover{ background:var(--gold2); border-color:var(--gold2); color:#131209; }
.stButton>button:disabled{ opacity:.4; transform:none; }
textarea, input{ border-radius:12px !important; }
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"]>div{ border-radius:12px !important; background:var(--panel) !important;
  border-color:var(--line) !important; transition:border-color 300ms var(--ease); }
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within{ border-color:var(--gold) !important; }
textarea{ font-size:16px !important; line-height:24px !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"], [data-testid="stTabs"] [role="tablist"]{ gap:var(--s50); background:var(--panel); padding:var(--s50);
  border-radius:16px; border:1px solid var(--line); width:fit-content; max-width:100%; }
.stTabs [data-baseweb="tab"], [data-testid="stTabs"] [role="tab"]{ border-radius:12px; padding:var(--s75) var(--s200); color:var(--muted);
  font-weight:500; font-size:14px; line-height:20px; height:auto; transition:background-color 300ms var(--ease), color 300ms var(--ease); }
.stTabs [data-baseweb="tab"]:hover{ color:var(--text); }
.stTabs [aria-selected="true"], [data-testid="stTabs"] [role="tab"][aria-selected="true"]{ background:var(--raise) !important; color:#fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none; }
[data-testid="stExpander"] details{ border:1px solid var(--line); border-radius:16px; background:var(--panel); }
[data-testid="stExpander"] summary{ font-size:14px; line-height:20px; }
[data-testid="stExpander"] pre, [data-testid="stText"]{ font-family:var(--mono) !important; font-size:12px; line-height:16px; }
[data-testid="stStatusWidget"], [data-testid="stStatus"]{ border-radius:16px; }
[data-testid="stAlert"]{ border-radius:16px; }
div[data-testid="stVerticalBlockBorderWrapper"]{ border-radius:16px; }

/* entrance: rise 32px and fade on the base curve */
@keyframes rise{ from{ opacity:0; transform:translateY(32px); } to{ opacity:1; transform:none; } }
.hero, .card, .claim, .metric, .pipe{ animation:rise 700ms var(--ease) both; }
.claim:nth-child(2){ animation-delay:60ms; } .claim:nth-child(3){ animation-delay:120ms; }
.claim:nth-child(4){ animation-delay:180ms; } .claim:nth-child(n+5){ animation-delay:240ms; }
@media (prefers-reduced-motion: reduce){
  .hero, .card, .claim, .metric, .pipe{ animation:fade 300ms linear both; }
  @keyframes fade{ from{ opacity:0; } to{ opacity:1; } }
  .stButton>button:hover{ transform:none; }
}

/* hero */
.hero{ border-radius:24px; padding:var(--s600) var(--s500); margin-bottom:var(--s300); background:var(--panel); border:1px solid var(--line); }
.hero .eyebrow{ display:inline-flex; align-items:center; gap:var(--s75); color:var(--gold2); font-weight:500; font-size:12px; line-height:16px;
  letter-spacing:.08em; text-transform:uppercase; padding:var(--s50) var(--s100); border-radius:9999px; background:var(--side);
  border:1px solid rgba(245,184,61,.3); }
.hero h1{ font-size:48px; line-height:48px; font-weight:600; margin:var(--s300) 0 var(--s200); padding:0; max-width:680px;
  background:linear-gradient(90deg,#FFFFFF,#9B9B9B); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p{ color:var(--muted); font-size:18px; line-height:28px; max-width:680px; margin:0; }
.chips{ display:flex; flex-wrap:wrap; gap:var(--s75); margin-top:var(--s400); }
.chip{ display:inline-flex; align-items:center; gap:var(--s75); background:var(--panel2); border:1px solid var(--line); border-radius:9999px;
  padding:var(--s75) var(--s100); font-size:14px; line-height:20px; color:var(--muted); }
.chip i{ color:var(--gold); font-size:16px; }
.chip b{ color:var(--text); font-weight:500; }

/* section label */
.sec{ display:flex; align-items:center; gap:var(--s75); font-size:14px; line-height:20px; font-weight:500; color:var(--muted); margin:var(--s200) 0 var(--s75); }
.sec i{ color:var(--gold); font-size:16px; }

/* pipeline */
.pipe{ display:flex; flex-wrap:wrap; align-items:center; gap:var(--s75); margin:var(--s75) 0 var(--s300); padding:var(--s100);
  border-radius:16px; background:var(--panel); border:1px solid var(--line); }
.node{ display:flex; align-items:center; gap:var(--s50); padding:var(--s50) var(--s100); border-radius:8px; background:var(--panel2);
  border:1px solid var(--line); font-size:12px; line-height:16px; font-weight:500; color:var(--dim); }
.node i{ font-size:16px; }
.node.done{ color:var(--text); border-color:rgba(47,208,138,.35); background:rgba(47,208,138,.08); }
.node.done i{ color:var(--bull); }
.node.retry{ border-color:rgba(255,107,107,.45); background:rgba(255,107,107,.08); color:var(--text); }
.node.retry i{ color:var(--bear); }
.node small{ color:var(--muted); font-size:12px; font-family:var(--mono); }
.arrow{ color:var(--line); font-size:12px; }

/* cards */
.card{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:var(--s300); margin-bottom:var(--s200); }
.verdict{ border-color:rgba(245,184,61,.35); }
.verdict .label{ display:flex; align-items:center; gap:var(--s75); color:var(--gold2); font-weight:500; font-size:12px; line-height:16px;
  letter-spacing:.08em; text-transform:uppercase; }
.verdict h2{ margin:var(--s75) 0 0; padding:0; font-size:24px; line-height:32px; color:#fff; max-width:880px; }
.gauges{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:var(--s200); margin-top:var(--s300); }
.gauge{ background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:var(--s200); }
.gauge .co{ font-weight:500; font-size:16px; line-height:24px; color:#fff; display:flex; justify-content:space-between; align-items:center; }
.gauge .score{ font-family:var(--mono); font-size:36px; line-height:40px; font-weight:600; color:var(--gold2); margin-top:var(--s75); }
.gauge .score span{ font-size:16px; color:var(--muted); }
.bar{ height:8px; border-radius:9999px; background:var(--raise); overflow:hidden; margin:var(--s75) 0 var(--s100); }
.bar i{ display:block; height:100%; border-radius:9999px; background:var(--gold); transform-origin:left; animation:grow 800ms var(--ease) both; }
@keyframes grow{ from{ transform:scaleX(0); } to{ transform:scaleX(1); } }
.gauge .meta{ display:flex; flex-wrap:wrap; gap:var(--s100); color:var(--muted); font-size:12px; line-height:16px; }
.gauge .meta span{ display:inline-flex; align-items:center; gap:var(--s50); }

.side-h{ display:flex; align-items:center; gap:var(--s100); font-size:20px; line-height:28px; font-weight:600; color:#fff; margin:var(--s50) 0 var(--s200); }
.side-h .ico{ width:32px; height:32px; border-radius:8px; display:grid; place-items:center; font-size:20px; }
.side-h .ico.bull{ background:rgba(47,208,138,.12); color:var(--bull); } .side-h .ico.bear{ background:rgba(255,107,107,.12); color:var(--bear); }
.side-h .ico.reb{ background:rgba(167,139,250,.14); color:var(--violet); }
.side-h .count{ font-size:12px; line-height:16px; font-weight:500; padding:var(--s50) var(--s75); border-radius:9999px; background:var(--panel2);
  border:1px solid var(--line); color:var(--muted); }
.claim{ border-radius:16px; padding:var(--s200); margin-bottom:var(--s100); background:var(--panel); border:1px solid var(--line);
  transition:border-color 300ms var(--ease), transform 500ms var(--ease); }
.claim:hover{ transform:translateY(-2px); }
.claim.bull:hover{ border-color:rgba(47,208,138,.45); } .claim.bear:hover{ border-color:rgba(255,107,107,.45); }
.claim .top{ display:flex; gap:var(--s75); align-items:center; flex-wrap:wrap; margin-bottom:var(--s100); font-size:12px; line-height:16px; }
.claim .dot{ width:8px; height:8px; border-radius:9999px; }
.claim.bull .dot{ background:var(--bull); } .claim.bear .dot{ background:var(--bear); }
.claim .id{ font-weight:600; color:#fff; font-family:var(--mono); }
.claim .by{ color:var(--dim); }
.claim .text{ color:var(--text); font-size:14px; line-height:20px; }
.pill{ display:inline-flex; align-items:center; gap:var(--s50); white-space:nowrap; flex-shrink:0; border-radius:9999px; padding:var(--s25) var(--s75);
  font-weight:500; font-size:12px; line-height:16px; border:1px solid var(--line); color:var(--muted); }
.pill.ok{ color:#7CF0B9; background:rgba(47,208,138,.12); border-color:rgba(47,208,138,.3); }
.pill.bad{ color:#FFB1B1; background:rgba(255,107,107,.12); border-color:rgba(255,107,107,.35); }
.pill.co{ color:#BFD6FF; background:rgba(110,168,254,.12); border-color:rgba(110,168,254,.3); }
.pill.cite{ color:var(--gold2); background:rgba(245,184,61,.1); border-color:rgba(245,184,61,.3); font-family:var(--mono); }
.reason{ margin-top:var(--s75); }
.caught{ border-color:rgba(255,107,107,.4); }
.caught .t{ display:flex; align-items:center; gap:var(--s75); color:#FFB1B1; font-weight:600; font-size:16px; line-height:24px; margin-bottom:var(--s100); }
.caught .row{ padding:var(--s100); border-radius:12px; background:var(--panel2); border:1px solid var(--line); margin-top:var(--s75); }
.caught s{ color:var(--text); opacity:.75; font-size:14px; line-height:20px; }
.caught .meta{ color:var(--muted); font-size:12px; line-height:16px; margin-top:var(--s50); }
.caught .meta b{ color:#7CF0B9; font-family:var(--mono); }
.reb{ border-color:rgba(167,139,250,.35); }
.reb p{ font-size:14px; line-height:20px; color:var(--text); }
.reb p b{ color:#C9B8FF; font-weight:600; }

.mgrid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(232px,1fr)); gap:var(--s200); margin-bottom:var(--s300); }
.metric{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:var(--s200);
  transition:border-color 300ms var(--ease), transform 500ms var(--ease); }
.metric:hover{ border-color:var(--raise); transform:translateY(-2px); }
.metric .lbl{ color:var(--muted); font-size:14px; line-height:20px; display:flex; justify-content:space-between; align-items:center; gap:var(--s75); }
.metric .val{ font-family:var(--mono); font-size:30px; line-height:36px; font-weight:600; color:#fff; margin:var(--s75) 0; }
.metric .prev{ color:var(--muted); font-size:12px; line-height:16px; display:flex; align-items:center; gap:var(--s75); }
.delta{ display:inline-flex; align-items:center; gap:var(--s25); font-weight:600; font-size:12px; line-height:16px; padding:var(--s25) var(--s75);
  border-radius:9999px; font-family:var(--mono); }
.delta.up{ color:#7CF0B9; background:rgba(47,208,138,.12); } .delta.down{ color:#FFB1B1; background:rgba(255,107,107,.12); }
.co-h{ display:flex; align-items:center; gap:var(--s75); font-weight:600; font-size:20px; line-height:28px; margin:var(--s200) 0 var(--s100); color:#fff; }
.co-h i{ color:var(--gold); }

.usage{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:var(--s100); margin:var(--s75) 0 var(--s300); }
.usage .u{ display:flex; align-items:center; gap:var(--s75); padding:var(--s100) var(--s200); border-radius:12px; background:var(--panel);
  border:1px solid var(--line); font-size:12px; line-height:16px; color:var(--muted); }
.usage .u i{ color:var(--gold); font-size:16px; }
.usage .u b{ font-family:var(--mono); font-size:16px; line-height:24px; font-weight:600; color:#fff; }
.review{ display:flex; gap:var(--s200); align-items:flex-start; border-color:rgba(245,184,61,.35); margin-top:var(--s400); }
.review .ico{ width:40px; height:40px; border-radius:12px; display:grid; place-items:center; background:var(--gold); color:#131209; font-size:24px; flex-shrink:0; }
.review h3{ margin:0 0 var(--s50); padding:0; font-size:20px; line-height:28px; }
.review p{ color:var(--muted); margin:0; font-size:14px; line-height:20px; }
.foot{ display:flex; justify-content:center; flex-wrap:wrap; gap:var(--s75); color:var(--dim); font-size:12px; line-height:16px;
  text-align:center; margin-top:var(--s700); padding-top:var(--s300); border-top:1px solid var(--line); }

/* ---------- 3D background: aurora light, perspective grid floor, floating shaded spheres ---------- */
.stApp{ background:radial-gradient(1200px 700px at 15% -10%, #1B1F5E 0%, transparent 60%),
  radial-gradient(900px 600px at 100% 10%, #2A1660 0%, transparent 55%), var(--bg); }
[data-testid="stMain"], [data-testid="stSidebar"], [data-testid="stHeader"]{ position:relative; z-index:1; }
.bg3d{ position:fixed; inset:0; z-index:-1; pointer-events:none; overflow:hidden; }  /* behind every block inside stMain */
.bg3d .aurora{ position:absolute; width:70vmax; height:70vmax; border-radius:50%; filter:blur(90px); opacity:.45;
  will-change:auto; }
.bg3d .a1{ left:-20vmax; top:-25vmax; background:radial-gradient(circle,#6D5BFF 0%,transparent 65%); }
.bg3d .a2{ right:-25vmax; top:10vh; background:radial-gradient(circle,#0EA5E9 0%,transparent 65%); animation-delay:-9s; opacity:.32; }
.bg3d .a3{ left:30vw; bottom:-40vmax; background:radial-gradient(circle,#F5B83D 0%,transparent 60%); animation-delay:-16s; opacity:.18; }
@keyframes drift{ from{ transform:translate3d(0,0,0) scale(1); } to{ transform:translate3d(6vw,4vh,0) scale(1.12); } }
.bg3d .floor{ position:absolute; left:-50%; right:-50%; bottom:-8vh; height:58vh; transform-origin:50% 100%;
  transform:perspective(520px) rotateX(64deg);
  background-image:linear-gradient(rgba(124,140,255,.30) 1px, transparent 1px), linear-gradient(90deg, rgba(124,140,255,.30) 1px, transparent 1px);
  background-size:64px 64px; -webkit-mask-image:linear-gradient(to top, #000 10%, transparent 90%); mask-image:linear-gradient(to top, #000 10%, transparent 90%);
  }
@keyframes floor{ to{ background-position:0 64px, 0 0; } }
.bg3d .orb{ position:absolute; border-radius:50%; animation:float 14s ease-in-out infinite;
  box-shadow:0 30px 60px rgba(0,0,0,.45), inset -14px -18px 40px rgba(0,0,0,.45); }
.bg3d .o1{ width:180px; height:180px; right:6vw; top:16vh; background:radial-gradient(circle at 32% 28%, #FFFFFF 0%, #C4B5FD 12%, #7C3AED 48%, #2E1065 100%); }
.bg3d .o2{ width:96px; height:96px; right:2vw; top:82vh; background:radial-gradient(circle at 32% 28%, #FFFFFF 0%, #A5F3FC 12%, #0891B2 50%, #083344 100%); animation-delay:-5s; }
.bg3d .o3{ width:56px; height:56px; right:3vw; top:6vh; background:radial-gradient(circle at 32% 28%, #FFFFFF 0%, #FDE68A 14%, #F59E0B 52%, #78350F 100%); animation-delay:-9s; }
.bg3d .ring{ position:absolute; right:10vw; top:58vh; width:220px; height:220px; border-radius:50%; border:10px solid rgba(124,140,255,.22);
  box-shadow:0 0 40px rgba(124,140,255,.25), inset 0 0 30px rgba(124,140,255,.2); transform:rotateX(70deg) rotateZ(20deg);
  animation:spin 30s linear infinite; }
@keyframes float{ 0%,100%{ transform:translate3d(0,0,0); } 50%{ transform:translate3d(0,-26px,0); } }
@keyframes spin{ to{ transform:rotateX(70deg) rotateZ(380deg); } }

/* ---------- glass surfaces ---------- */
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"]>div{ background:rgba(12,16,48,.88) !important; }
.stButton>button:not([kind="primary"]), .stDownloadButton>button{ background:rgba(22,28,72,.82); }
.hero, .card, .claim, .metric, .pipe, .gauge, .usage .u, [data-testid="stExpander"] details,
.stTabs [data-baseweb="tab-list"], [data-testid="stTabs"] [role="tablist"]{ -webkit-backdrop-filter:var(--glass-blur); backdrop-filter:var(--glass-blur);
  box-shadow:0 10px 40px rgba(3,6,30,.45), inset 0 1px 0 rgba(255,255,255,.06); }
[data-testid="stSidebar"]{ -webkit-backdrop-filter:var(--glass-blur); backdrop-filter:var(--glass-blur); }
[data-testid="stSidebar"] > div{ background:transparent; }
.claim:hover, .metric:hover{ transform:translateY(-4px) rotateX(2deg); box-shadow:0 18px 50px rgba(3,6,30,.6), inset 0 1px 0 rgba(255,255,255,.08); }
.metric, .claim{ transform-style:preserve-3d; }

/* ---------- hero with a 3D cube ---------- */
.hero{ display:grid; grid-template-columns:minmax(0,1fr) 260px; gap:var(--s400); align-items:center; position:relative; overflow:hidden; }
.hero h1{ background:linear-gradient(90deg,#FFFFFF 0%,#C7D2FE 55%,#A5B4FC 100%); -webkit-background-clip:text; background-clip:text; }
.scene{ width:260px; height:260px; perspective:900px; display:grid; place-items:center; }
.cube{ position:relative; width:140px; height:140px; transform-style:preserve-3d; animation:cube 18s linear infinite; }
.cube .f{ position:absolute; inset:0; display:grid; place-items:center; border-radius:16px; font-size:48px; color:#fff;
  border:1px solid rgba(199,210,254,.35); background:linear-gradient(135deg, rgba(124,58,237,.55), rgba(14,165,233,.35));
  box-shadow:inset 0 0 30px rgba(255,255,255,.12); -webkit-backdrop-filter:blur(6px); backdrop-filter:blur(6px); }
.cube .f.g{ background:linear-gradient(135deg, rgba(245,184,61,.65), rgba(234,88,12,.35)); color:#131209; }
.cube .f1{ transform:translateZ(70px); } .cube .f2{ transform:rotateY(180deg) translateZ(70px); }
.cube .f3{ transform:rotateY(90deg) translateZ(70px); } .cube .f4{ transform:rotateY(-90deg) translateZ(70px); }
.cube .f5{ transform:rotateX(90deg) translateZ(70px); } .cube .f6{ transform:rotateX(-90deg) translateZ(70px); }
.scene .shadow{ position:absolute; width:150px; height:24px; margin-top:220px; border-radius:50%;
  background:radial-gradient(ellipse, rgba(124,140,255,.45), transparent 70%); filter:blur(4px); }
@keyframes cube{ from{ transform:rotateX(-22deg) rotateY(0deg); } to{ transform:rotateX(-22deg) rotateY(360deg); } }
@media (max-width: 900px){ .hero{ grid-template-columns:1fr; } .scene{ display:none; } .bg3d .orb, .bg3d .ring{ display:none; } }
@media (prefers-reduced-motion: reduce){
  .bg3d .aurora, .bg3d .floor, .bg3d .orb, .bg3d .ring, .cube{ animation:none !important; }
}
</style>
"""

BACKGROUND = """<div class="bg3d" aria-hidden="true"><div class="aurora a1"></div><div class="aurora a2"></div>
<div class="aurora a3"></div><div class="ring"></div><div class="orb o1"></div><div class="orb o2"></div>
<div class="orb o3"></div><div class="floor"></div></div>"""

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
.st-key-memo_paper{ background:#F7F5EF; border-radius:16px; padding:var(--s400) var(--s500); }
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
