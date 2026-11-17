import base64
import os
import time

import streamlit as st
import joblib
from preprocess import clean_text

st.set_page_config(page_title="IMDB Sentiment", layout="centered")


def render(html: str):
    """Strip indentation + newlines so Markdown never turns the HTML into a code block."""
    flat = " ".join(line.strip() for line in html.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


# ---------- Optional real cinema photo ----------
# Put an image named hero.jpg (or hero.png) next to this file and it becomes the hero background.
HERO_BG = "radial-gradient(circle at 80% 20%, rgba(34,211,238,.20), transparent 55%), linear-gradient(135deg,#151515,#0B0B0B)"
for fname, mime in (("hero.jpg", "jpeg"), ("hero.png", "png")):
    if os.path.exists(fname):
        with open(fname, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        HERO_BG = (
            "linear-gradient(90deg, rgba(11,11,11,.96) 25%, rgba(11,11,11,.55)), "
            f"url('data:image/{mime};base64,{b64}') center/cover"
        )
        break

render("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg:#0A0B0D; --surface:#13151A; --surface2:#1A1D24; --line:#262A33;
    --accent:#22D3EE; --accent-d:#0EA5C6; --accent2:#3B82F6;
    --neg:#F43F5E;
    --text:#F4F6F8; --muted:#8B93A1;
}

/* ===== Base ===== */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li, .stApp div {
    font-family:'Inter',system-ui,sans-serif; color:var(--text);
}
.stApp { background:var(--bg); }
header[data-testid="stHeader"] { background:transparent; }
footer, #MainMenu { visibility:hidden; }
.block-container { max-width:860px; padding:1.5rem 1.25rem 2rem !important; position:relative; z-index:2; }

/* ===== Spotlight beams ===== */
.beam {
    position:fixed; top:-10%; width:340px; height:125vh; z-index:0; pointer-events:none;
    background:linear-gradient(180deg, rgba(34,211,238,.18), transparent 75%);
    clip-path:polygon(46% 0, 54% 0, 100% 100%, 0 100%);
    transform-origin:top center; filter:blur(5px);
    animation:sway 9s ease-in-out infinite alternate;
}
.beam.b1 { left:2%; }
.beam.b2 { right:2%; animation-delay:-4s; animation-direction:alternate-reverse; }
@keyframes sway { from { transform:rotate(-14deg); } to { transform:rotate(14deg); } }

/* ===== Floating shapes ===== */
.float { position:fixed; bottom:-70px; color:var(--accent); opacity:.16; z-index:1; pointer-events:none; animation:rise linear infinite; }
.float svg { display:block; }
@keyframes rise { to { transform:translateY(-120vh) rotate(360deg); } }

/* ===== Header ===== */
.top { display:flex; justify-content:space-between; align-items:center; padding-bottom:18px; border-bottom:1px solid var(--line); margin-bottom:28px; }
.brand { display:flex; align-items:center; gap:10px; font-weight:700; font-size:16px; }
.brand-icon {
    width:34px; height:34px; border-radius:9px; background:linear-gradient(135deg,var(--accent),var(--accent2));
    display:flex; align-items:center; justify-content:center; animation:glow 2.8s ease-in-out infinite;
}
.brand-icon svg { width:16px; height:16px; fill:#04141A; }
@keyframes glow { 0%,100% { box-shadow:0 0 0 rgba(34,211,238,0); } 50% { box-shadow:0 0 22px rgba(34,211,238,.6); } }
.top-tag { font-size:11px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted) !important; border:1px solid var(--line); padding:5px 12px; border-radius:999px; }
.live { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--neg); margin-right:8px; animation:blink 1.2s infinite; }
@keyframes blink { 50% { opacity:.15; } }


/* ===== Hero ===== */
.hero {
    position:relative; overflow:hidden; border:1px solid var(--line); border-radius:22px;
    padding:38px 36px; margin-bottom:26px; display:grid; grid-template-columns:1fr 190px; gap:28px; align-items:center;
    animation:fadeup .8s ease both;
}
@keyframes fadeup { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:none; } }
.reel {
    position:absolute; right:-70px; top:-70px; width:260px; height:260px; border-radius:50%; opacity:.12;
    border:14px solid var(--accent);
    background:radial-gradient(circle, transparent 28%, var(--accent) 29% 33%, transparent 34%);
    animation:spin 22s linear infinite;
}
.reel::before, .reel::after { content:""; position:absolute; inset:38px; border-radius:50%; border:14px dotted var(--accent); }
.reel::after { inset:92px; border-width:10px; }
@keyframes spin { to { transform:rotate(360deg); } }

.eyebrow { font-size:12px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:var(--accent) !important; margin-bottom:14px; position:relative; }
.title { font-size:42px; font-weight:800; letter-spacing:-1.5px; line-height:1.08; margin:0 0 14px; padding:0; text-align:left; position:relative; }
.title span { background:linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.sub { font-size:15px; line-height:1.7; color:#B3BAC6 !important; max-width:430px; margin:0; text-align:left; position:relative; }

/* ===== Clapperboard ===== */
.clap { width:170px; position:relative; filter:drop-shadow(0 14px 24px rgba(34,211,238,.22)); animation:bob 4s ease-in-out infinite; }
@keyframes bob { 50% { transform:translateY(-8px); } }
.clap-top {
    height:30px; border-radius:6px 6px 0 0; transform-origin:left bottom; animation:clap 3.4s ease-in-out infinite;
    background:repeating-linear-gradient(-45deg, var(--accent) 0 16px, #0A0B0D 16px 32px); border:2px solid var(--accent);
}
@keyframes clap { 0%,55% { transform:rotate(-24deg); } 63% { transform:rotate(0deg); } 90% { transform:rotate(0deg); } 100% { transform:rotate(-24deg); } }
.clap-bar { height:20px; margin-top:3px; background:repeating-linear-gradient(-45deg, #0A0B0D 0 16px, var(--accent) 16px 32px); border:2px solid var(--accent); border-bottom:none; }
.clap-body { border:2px solid var(--accent); background:var(--surface); border-radius:0 0 8px 8px; padding:12px 14px; font-size:10px; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted) !important; line-height:2; }
.clap-body b { color:var(--accent) !important; }

/* ===== Film strip ===== */
.strip { position:relative; overflow:hidden; background:#050607; border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:20px 0; margin:6px 0 34px; }
.strip::before, .strip::after {
    content:""; position:absolute; left:0; right:0; height:7px;
    background:repeating-linear-gradient(90deg, #23272F 0 12px, transparent 12px 24px);
}
.strip::before { top:5px; } .strip::after { bottom:5px; }
.track { display:flex; width:max-content; animation:scroll 34s linear infinite; }
.strip:hover .track { animation-play-state:paused; }
.frame {
    width:104px; height:66px; margin:0 6px; border:1px solid var(--line); border-radius:4px;
    display:flex; align-items:center; justify-content:center; color:var(--accent);
    background:linear-gradient(135deg,#14171D,#0F2230);
}
.frame:nth-child(even) { background:linear-gradient(135deg,#0F2230,#14171D); }
.frame svg { width:26px; height:26px; opacity:.75; }
@keyframes scroll { to { transform:translateX(-50%); } }

/* ===== Step headings ===== */
.step { display:flex; align-items:center; gap:10px; margin:0 0 12px; }
.step-num { font-size:11px; font-weight:700; color:#04141A !important; background:var(--accent); width:22px; height:22px; border-radius:6px; display:flex; align-items:center; justify-content:center; }
.step-title { font-size:15px; font-weight:600; }


/* ===== Textarea ===== */
.stTextArea textarea {
    background:var(--surface) !important; color:var(--text) !important; border:1px solid var(--line) !important;
    border-radius:12px !important; padding:16px 18px !important; font-size:15px !important; line-height:1.65 !important;
    box-shadow:none !important; caret-color:var(--accent);
}
.stTextArea textarea:focus { border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(34,211,238,.18) !important; }
.stTextArea textarea::placeholder { color:#5A616E !important; }

/* ===== Button ===== */
.stButton > button {
    background:linear-gradient(135deg,var(--accent),var(--accent2)) !important; border:none !important; border-radius:10px !important;
    padding:10px 32px !important; transition:transform .12s, box-shadow .2s, filter .2s;
}
.stButton > button p { color:#04141A !important; font-weight:700; font-size:14px; letter-spacing:.4px; }
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 10px 26px rgba(34,211,238,.35); filter:brightness(1.06); }
.stButton > button:active { transform:scale(.97); }

/* ===== Ticket ===== */
.ticket {
    position:relative; display:flex; background:var(--surface); border:1px solid var(--line); border-radius:16px; overflow:hidden;
    animation:pop .6s cubic-bezier(.2,.9,.3,1.25) both;
}
.ticket::before, .ticket::after { content:""; position:absolute; right:182px; width:22px; height:22px; border-radius:50%; background:var(--bg); border:1px solid var(--line); }
.ticket::before { top:-12px; } .ticket::after { bottom:-12px; }
@keyframes pop { from { opacity:0; transform:scale(.88); } to { opacity:1; transform:scale(1); } }
.t-main { flex:1; display:flex; align-items:center; gap:22px; padding:26px 28px; border-left:5px solid var(--accent); }
.ticket.neg .t-main { border-left-color:var(--neg); }
.t-icon { width:62px; height:62px; flex:none; color:var(--accent); animation:cheer 1.8s ease-in-out infinite; }
.t-icon svg { width:100%; height:100%; }
.ticket.neg .t-icon { color:var(--neg); animation:shake 1.2s ease-in-out infinite; }
@keyframes cheer { 0%,100% { transform:translateY(0) scale(1); } 50% { transform:translateY(-8px) scale(1.06); } }
@keyframes shake { 0%,100% { transform:rotate(0); } 20% { transform:rotate(-10deg); } 40% { transform:rotate(8deg); } 60% { transform:rotate(-6deg); } 80% { transform:rotate(4deg); } }
.t-label { font-size:11px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--muted) !important; }
.t-title { font-size:34px; font-weight:800; letter-spacing:-1px; margin-top:4px; color:var(--accent) !important; line-height:1.1; }
.ticket.neg .t-title { color:var(--neg) !important; }
.t-desc { font-size:13px; color:var(--muted) !important; margin-top:4px; }
.t-side { width:182px; border-left:2px dashed var(--line); padding:20px 14px; display:flex; flex-direction:column; justify-content:center; text-align:center; background:var(--surface2); }
.t-side b { font-size:40px; font-weight:800; letter-spacing:-1.5px; line-height:1; }
.t-side small { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--muted) !important; margin-top:6px; }

.bar { height:8px; background:var(--surface2); border-radius:999px; overflow:hidden; margin-top:24px; }
.fill { height:100%; border-radius:999px; background:linear-gradient(90deg, var(--accent2), var(--accent)); animation:grow 1.2s ease both; }
@keyframes grow { from { width:0 !important; } }
.legend { display:flex; justify-content:space-between; margin-top:10px; font-size:12px; color:var(--muted) !important; }

.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:22px; }
.stat { background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }
.stat b { font-size:22px; font-weight:700; display:block; }
.stat span { font-size:11px; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted) !important; }


/* ===== Confetti (positive only) ===== */
.confetti { position:fixed; top:-30px; width:9px; height:15px; border-radius:2px; z-index:50; pointer-events:none; animation:fall 3.2s ease-in forwards; }
@keyframes fall { to { transform:translateY(108vh) rotate(540deg); opacity:0; } }

/* ===== Expander, alerts, spinner ===== */
div[data-testid="stExpander"] { background:var(--surface); border:1px solid var(--line) !important; border-radius:12px; margin-top:16px; }
div[data-testid="stExpander"] summary p { color:var(--text) !important; font-size:14px; font-weight:500; }
div[data-testid="stAlert"] { background:var(--surface); border:1px solid var(--line); border-radius:12px; }
div[data-testid="stAlert"] * { color:var(--text) !important; }
div[data-testid="stSpinner"] * { color:var(--accent) !important; }

/* ===== Footer ===== */
.foot { margin-top:56px; padding-top:20px; border-top:1px solid var(--line); display:flex; justify-content:space-between; align-items:center; font-size:12px; color:var(--muted) !important; }
.foot b { color:var(--accent) !important; font-weight:600; }

@media (max-width:700px) {
    .hero { grid-template-columns:1fr; padding:28px 22px; }
    .clap { display:none; }
    .title { font-size:32px; }
    .ticket { flex-direction:column; }
    .ticket::before, .ticket::after { display:none; }
    .t-side { width:auto; border-left:none; border-top:2px dashed var(--line); }
    .stats { grid-template-columns:1fr; }
    .top-tag { display:none; }
    .beam { display:none; }
    .foot { flex-direction:column; gap:6px; align-items:flex-start; }
}
</style>
""")

render(f"<style>.hero {{ background:{HERO_BG}; }}</style>")


@st.cache_resource
def load_model():
    return joblib.load("sentiment_modelVersion2.joblib")

model = load_model()


# ---------- SVG icons (no emojis) ----------
def svg(path: str, size: int = 24, fill: bool = False, stroke_w: float = 1.8) -> str:
    attrs = 'fill="currentColor"' if fill else f'fill="none" stroke="currentColor" stroke-width="{stroke_w}" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" {attrs}>{path}</svg>'


PLAY   = '<path d="M7 4.5v15l13-7.5z"/>'
STAR   = '<path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7-6.2-3.7-6.2 3.7 1.6-7L2 9.2l7.1-.6z"/>'
RING   = '<circle cx="12" cy="12" r="8"/>'
DIAMND = '<path d="M12 3l9 9-9 9-9-9z"/>'
BARS   = '<path d="M5 20V10M10 20V4M15 20v-8M20 20V7"/>'
TICKET = '<path d="M3 8a2 2 0 0 0 0 4v0a2 2 0 0 1 0 4v2h18v-2a2 2 0 0 1 0-4v0a2 2 0 0 0 0-4V6H3z"/>'
CHECK  = '<circle cx="12" cy="12" r="10"/><path d="M7.8 12.5l3 3 5.4-6.4"/>'
CROSS  = '<circle cx="12" cy="12" r="10"/><path d="M9 9l6 6M15 9l-6 6"/>'

# floating shapes
floaters = "".join(
    f'<span class="float" style="left:{left}%; animation-duration:{dur}s; animation-delay:-{delay}s;">{svg(path, size, fill=fill)}</span>'
    for left, dur, delay, path, size, fill in [
        (6, 22, 2, PLAY, 26, True), (17, 28, 12, RING, 30, False), (29, 19, 6, STAR, 24, True),
        (41, 25, 16, TICKET, 30, False), (54, 21, 9, DIAMND, 24, False), (66, 27, 3, PLAY, 22, True),
        (78, 23, 14, BARS, 28, False), (90, 26, 7, STAR, 26, True),
    ]
)
render(f'<div class="beam b1"></div><div class="beam b2"></div>{floaters}')

# film strip frames
FRAME_ICONS = [svg(p, 26, f) for p, f in [(PLAY, False), (STAR, False), (RING, False), (BARS, False), (DIAMND, False), (TICKET, False)]]
frames = "".join(f'<div class="frame">{ic}</div>' for ic in FRAME_ICONS * 3)
strip_html = f'<div class="strip"><div class="track">{frames}{frames}</div></div>'


# ---------- Header + Hero ----------
render(f"""
<div class="top">
    <div class="brand"><div class="brand-icon">{svg(PLAY, 16, fill=True)}</div>IMDB Sentiment</div>
    <div class="top-tag"><span class="live"></span>Now screening</div>
</div>
""")

render("""
<div class="hero">
    <div class="reel"></div>
    <div>
        <div class="eyebrow">Sentiment analysis</div>
        <h1 class="title">Is this review <span>positive</span> or negative?</h1>
        <p class="sub">Paste a movie review below. The model reads it and tells you how the author felt.</p>
    </div>
    <div class="clap">
        <div class="clap-top"></div>
        <div class="clap-bar"></div>
        <div class="clap-body">Scene <b>01</b><br>Take <b>01</b><br>Dir. <b>ML Model</b></div>
    </div>
</div>
""")

render(strip_html)


# ---------- Step 1 ----------
render('<div class="step"><div class="step-num">1</div><div class="step-title">Write your review</div></div>')

review = st.text_area(
    "Review",
    height=170,
    placeholder="This movie was absolutely fantastic...",
    label_visibility="collapsed",
)

predict = st.button("Action!")


# ---------- Step 2 ----------
if predict:
    if not review.strip():
        st.warning("Please write a review first.")
    else:
        with st.spinner("Rolling the film..."):
            time.sleep(0.9)
            cleaned = clean_text(review)
            label = model.predict([cleaned])[0]
            proba = model.predict_proba([cleaned])[0]
        pos_p = float(proba[1])

        if label == 1:
            cls, text, conf, icon = "", "Positive", pos_p, svg(CHECK, 62, stroke_w=1.6)
            desc = "A thumbs up. The author enjoyed this one."
            colors = ["#22D3EE", "#3B82F6", "#F4F6F8"]
            confetti = "".join(
                f'<span class="confetti" style="left:{3 + i * 7}%; background:{colors[i % 3]}; animation-delay:{(i % 6) * 0.15:.2f}s;"></span>'
                for i in range(14)
            )
            render(confetti)
        else:
            cls, text, conf, icon = "neg", "Negative", float(proba[0]), svg(CROSS, 62, stroke_w=1.6)
            desc = "Not a fan. The author was not impressed."

        render("""
        <div style="height:34px"></div>
        <div class="step"><div class="step-num">2</div><div class="step-title">Your ticket</div></div>
        """)

        render(f"""
        <div class="ticket {cls}">
            <div class="t-main">
                <div class="t-icon">{icon}</div>
                <div>
                    <div class="t-label">Verdict</div>
                    <div class="t-title">{text}</div>
                    <div class="t-desc">{desc}</div>
                </div>
            </div>
            <div class="t-side"><b>{conf:.0%}</b><small>Confidence</small></div>
        </div>

        <div class="bar"><div class="fill" style="width:{pos_p*100:.1f}%"></div></div>
        <div class="legend"><span>Negative</span><span>Positive · {pos_p:.1%}</span></div>

        <div class="stats">
            <div class="stat"><b>{len(review.split())}</b><span>Words</span></div>
            <div class="stat"><b>{len(review)}</b><span>Characters</span></div>
            <div class="stat"><b>{len(cleaned.split())}</b><span>Kept after cleaning</span></div>
        </div>
        """)

        with st.expander("Show cleaned text"):
            st.write(cleaned)


# ---------- Footer ----------
render("""
<div class="foot">
    <span>© 2026 <b>IMDB Sentiment</b> · Made for the love of cinema</span>
    <span>Built with Streamlit · scikit-learn</span>
</div>
""")