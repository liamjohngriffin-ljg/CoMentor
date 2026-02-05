from dotenv import load_dotenv
load_dotenv()

import os
import json
import base64
import tempfile
from datetime import datetime

import streamlit as st
from openai import OpenAI


# ──────────────────────────────────────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoMentor | Executive Communication Intelligence",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Version stamp at top to confirm code is current
st.markdown(
    "### ✅ CoMentor UI VERSION: 2026-02-05 — Communication Analysis Landing Page"
)


# ──────────────────────────────────────────────────────────────────────────────
# Global CSS – clean “Grammarly‑style” marketing page
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg: #ffffff;
  --text: #0f172a;
  --muted: #475569;
  --muted2: #64748b;
  --border: #e2e8f0;
  --card: #ffffff;
  --soft: #f8fafc;
  --accent: #22c55e;
  --accent-dark: #16a34a;
  --shadow: 0 14px 40px rgba(15, 23, 42, 0.10);
  --shadow-sm: 0 8px 22px rgba(15, 23, 42, 0.08);
  --radius: 18px;
}

/* Base */
.stApp {
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: var(--text);
}

/* Hide Streamlit chrome to feel like a landing page */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container{
  max-width: 1120px;
  padding-top: 2.0rem;
  padding-bottom: 4rem;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: #fbfdff;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stMarkdown{
  color: var(--text);
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
  color: var(--muted) !important;
}

/* Inputs / uploader */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
div[data-testid="stFileUploader"] section {
  border-radius: 12px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 10px;
  background: transparent;
  padding: 0;
  border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 999px !important;
  padding: 10px 16px;
  font-weight: 700;
  color: var(--muted);
  background: transparent;
}
.stTabs [aria-selected="true"] {
  background: rgba(34, 197, 94, 0.10) !important;
  color: var(--text) !important;
}

/* Buttons – primary CTA */
.stButton > button {
  background: var(--accent) !important;
  color: white !important;
  border: none !important;
  padding: 0.85rem 1.25rem !important;
  font-size: 1rem !important;
  font-weight: 800 !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  background: var(--accent-dark) !important;
  box-shadow: var(--shadow) !important;
}

/* Hero */
.cm-hero {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2.5rem 2.5rem;
  box-shadow: var(--shadow-sm);
}
.cm-nav {
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom: 1.75rem;
}
.cm-brand {
  display:flex;
  align-items:center;
  gap: 0.75rem;
}
.cm-logo {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(34,197,94,0.14);
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight: 900;
  color: var(--accent-dark);
}
.cm-brandname {
  font-size: 1.25rem;
  font-weight: 900;
  letter-spacing: -0.02em;
}
.cm-mini{
  font-size: 0.90rem;
  color: var(--muted2);
}
.cm-badge {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--accent-dark);
  background: rgba(34,197,94,0.10);
  border: 1px solid rgba(34,197,94,0.18);
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
}

/* Hero grid */
.cm-hero-grid {
  display:grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: 1.75rem;
}
@media (max-width: 900px){
  .cm-hero-grid { grid-template-columns: 1fr; }
}
.cm-h1 {
  font-size: 2.75rem;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -0.04em;
  margin: 0 0 0.75rem 0;
}
.cm-sub {
  font-size: 1.1rem;
  color: var(--muted);
  line-height: 1.7;
  margin: 0 0 1.25rem 0;
}
.cm-proof {
  margin-top: 1.0rem;
  color: var(--muted2);
  font-size: 0.98rem;
}
.cm-proof strong { color: var(--text); }

.cm-cards {
  margin-top: 1.75rem;
  display:grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 900px){
  .cm-cards { grid-template-columns: 1fr; }
}
.cm-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.15rem 1.15rem;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
}
.cm-card-title{
  font-weight: 900;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.01em;
}
.cm-card-text{
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Section wrapper */
.cm-section {
  margin-top: 1.5rem;
  border: 1px solid var(--border);
  background: white;
  border-radius: var(--radius);
  padding: 1.35rem 1.35rem;
  box-shadow: var(--shadow-sm);
}

/* Info strip */
.cm-strip {
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--border);
  background: var(--soft);
  border-radius: 16px;
  margin: 0.5rem 0 1rem 0;
}
.cm-strip h3{
  margin: 0;
  font-weight: 900;
  letter-spacing: -0.02em;
}
.cm-strip p{
  margin: 0.5rem 0 0 0;
  color: var(--muted);
}

/* Report UI (kept, but simplified) */
.section-header {
  display:flex;
  align-items:center;
  gap:0.75rem;
  margin: 2rem 0 1.25rem 0;
}
.section-icon {
  width:32px;
  height:32px;
  background:#f3f4f6;
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
}
.section-title {
  font-size:1.25rem;
  font-weight:800;
  color:#111827;
  margin:0;
}

.insight-card {
  background:white;
  border-radius:12px;
  padding:1.25rem 1.5rem;
  margin-bottom:0.75rem;
  display:flex;
  align-items:flex-start;
  gap:1rem;
  border: 1px solid var(--border);
  box-shadow: 0 6px 18px rgba(15,23,42,0.06);
}
.insight-icon {
  width:36px;
  height:36px;
  border-radius:10px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:1.1rem;
  flex-shrink:0;
}
.insight-icon-strength { background:#d1fae5; color:#059669; }
.insight-icon-improve { background:#fef3c7; color:#d97706; }
.insight-icon-moment { background:#dbeafe; color:#2563eb; }

.insight-title { font-weight:800; color:#1f2937; margin-bottom:0.25rem; }
.insight-text { font-size:0.925rem; color:#4b5563; line-height:1.5; }

.executive-summary {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 1.5rem 2rem;
  border-radius: 0 12px 12px 0;
  font-size: 1.05rem;
  line-height: 1.7;
  color: #334155;
  border-left: 4px solid var(--accent);
}

.subscore-card {}
.cog-meter {
  background:white;
  border-radius:12px;
  padding:1.5rem;
  border:1px solid var(--border);
  box-shadow:0 6px 18px rgba(15,23,42,0.06);
}
.cog-meter-row {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:0.75rem 0;
  border-bottom:1px solid #f3f4f6;
}
.cog-meter-row:last-child { border-bottom:none; }
.cog-meter-label { font-size:0.925rem; color:#4b5563; }
.cog-meter-value {
  font-weight:800;
  padding:0.25rem 0.75rem;
  border-radius:20px;
  font-size:0.875rem;
}
.cog-low { background:#d1fae5; color:#059669; }
.cog-medium { background:#fef3c7; color:#d97706; }
.cog-high { background:#fee2e2; color:#dc2626; }

.transcript-box {
  background:#f9fafb;
  border:1px solid #e5e7eb;
  border-radius:12px;
  padding:1.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size:0.875rem;
  line-height:1.7;
  color:#374151;
  max-height:400px;
  overflow-y:auto;
}

.report-footer {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  text-align:center;
  color:#94a3b8;
  font-size:0.875rem;
}

.cm-version {
  color: #94a3b8;
  font-size: 0.82rem;
  margin-top: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI client
# ──────────────────────────────────────────────────────────────────────────────
def init_openai_client() -> OpenAI | None:
    api_key = os.environ.get("OPENAI_API_KEY")

    # Try Streamlit secrets if available
    if not api_key:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass

    # Try session state (from sidebar input)
    if not api_key:
        api_key = st.session_state.get("openai_api_key")

    if not api_key or not isinstance(api_key, str) or len(api_key.strip()) < 10:
        return None

    return OpenAI(api_key=api_key.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Core AI functions
# ──────────────────────────────────────────────────────────────────────────────
def transcribe_audio(client: OpenAI, audio_file_path: str):
    with open(audio_file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
        )
    return transcript


def analyze_communication(client: OpenAI, transcript_text: str, meeting_context: dict):
    prompt = f"""
You are an elite executive communication analyst with 20 years of experience coaching Fortune 500 CEOs, world leaders, and elite performers.

Analyze this communication with surgical precision. Be specific, evidence-based, and actionable.

MEETING CONTEXT:
- Meeting Type: {meeting_context.get('meeting_type', 'Not specified')}
- Objective: {meeting_context.get('objective', 'Not specified')}
- Audience: {meeting_context.get('audience', 'Not specified')}
- Speaker Role: {meeting_context.get('speaker_role', 'Executive')}

TRANSCRIPT:
{transcript_text}

Provide your analysis as a JSON object with this exact structure:
{{
  "communication_effectiveness_score": <0-100>,
  "score_verdict": "<one of: 'Exceptional', 'Strong', 'Competent', 'Developing', 'Needs Work'>",
  "sub_scores": {{
    "clarity": <0-100>,
    "authority": <0-100>,
    "audience_adaptation": <0-100>,
    "persuasion": <0-100>,
    "emotional_regulation": <0-100>
  }},
  "executive_summary": "<2-3 sentence high-level assessment in a direct, executive tone>",
  "strengths": [
    {{"title": "<short>", "detail": "<specific evidence and why it matters>"}},
    {{"title": "<short>", "detail": "<specific evidence and why it matters>"}},
    {{"title": "<short>", "detail": "<specific evidence and why it matters>"}}
  ],
  "improvements": [
    {{"title": "<short>", "detail": "<what happened and specific fix>"}},
    {{"title": "<short>", "detail": "<what happened and specific fix>"}}
  ],
  "key_moments": [
    {{
      "timestamp": "<early/mid/late>",
      "title": "<what happened>",
      "impact": "<positive/negative/neutral>",
      "insight": "<coaching insight>"
    }},
    {{
      "timestamp": "<early/mid/late>",
      "title": "<what happened>",
      "impact": "<positive/negative/neutral>",
      "insight": "<coaching insight>"
    }}
  ],
  "cognitive_load": {{
    "overall": "<low/medium/high>",
    "jargon": "<low/medium/high>",
    "complexity": "<low/medium/high>",
    "topic_switches": "<low/medium/high>"
  }},
  "one_thing": "<single most impactful change, specific and actionable>"
}}

Only return valid JSON. No markdown, no commentary.
"""
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an elite executive communication analyst. Respond only with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2500,
    )

    text = resp.choices[0].message.content.strip()

    # Strip accidental code fences
    if text.startswith("```"):
        parts = text.split("```")
        # take first non-empty part that looks like JSON
        for p in parts:
            p = p.strip()
            if p and not p.lower().startswith("json"):
                text = p
                break

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Model did not return valid JSON. Raw output:\n{text}")

    return data


# ──────────────────────────────────────────────────────────────────────────────
# UI helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_score_color(score: int) -> str:
    if score >= 80:
        return "#059669"
    if score >= 60:
        return "#16a34a"
    if score >= 40:
        return "#d97706"
    return "#dc2626"


def render_hero():
    st.markdown(
        """
<div class="cm-hero">
  <div class="cm-nav">
    <div class="cm-brand">
      <div class="cm-logo">◐</div>
      <div>
        <div class="cm-brandname">CoMentor</div>
        <div class="cm-mini">Executive Communication Intelligence</div>
      </div>
    </div>
    <div class="cm-badge">Private • Evidence-based • Actionable</div>
  </div>

  <div class="cm-hero-grid">
    <div>
      <h1 class="cm-h1">Say it with clarity, authority, and impact.</h1>
      <p class="cm-sub">
        Record or upload a high-stakes conversation and get coaching-grade feedback:
        what worked, what didn’t, and the single highest-leverage change for next time.
      </p>
      <div class="cm-proof">
        <strong>Outputs:</strong> Effectiveness score, strengths, fixes, key moments, cognitive load, and a “ONE thing” action.
      </div>
      <div class="cm-version">Landing experience • Comms analysis focused</div>
    </div>

    <div>
      <div class="cm-card">
        <p class="cm-card-title">What you’ll get</p>
        <p class="cm-card-text">A structured report you can act on immediately—no fluff.</p>
        <div style="height:1px;background:var(--border);margin:1.1rem 0;"></div>
        <p class="cm-card-text"><strong>Best for:</strong> board updates, investor pitches, negotiations, client meetings.</p>
      </div>
    </div>
  </div>

  <div class="cm-cards">
    <div class="cm-card">
      <p class="cm-card-title">Executive-grade clarity</p>
      <p class="cm-card-text">Flags vague sections and suggests concrete, reusable fixes.</p>
    </div>
    <div class="cm-card">
      <p class="cm-card-title">Authority & persuasion</p>
      <p class="cm-card-text">Shows where leverage drops—and what to say instead.</p>
    </div>
    <div class="cm-card">
      <p class="cm-card-title">Cognitive load control</p>
      <p class="cm-card-text">Detects jargon and complexity spikes that make audiences tune out.</p>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_subscore(score: int, label: str):
    color = get_score_color(score)
    st.markdown(
        f"""
<div class="subscore-card" style="text-align:center; border-radius:16px; padding:1.25rem;">
  <div style="color:{color}; font-size:2.1rem; font-weight:900; margin-bottom:0.25rem;">{score}</div>
  <div style="color:#6b7280; font-weight:700; font-size:0.9rem;">{label}</div>
  <div style="height:6px;background:#e5e7eb;border-radius:999px;margin-top:1rem;overflow:hidden;">
    <div style="height:100%;width:{score}%;background:{color};border-radius:999px;"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_report(analysis: dict, transcript_text: str):
    score = analysis["communication_effectiveness_score"]
    verdict = analysis.get("score_verdict", "Competent")

    # Overall score banner
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
<div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color:white; padding:2.25rem; text-align:center; border-radius:20px; box-shadow:var(--shadow);">
  <div style="font-size:0.85rem; font-weight:900; letter-spacing:0.12em; text-transform:uppercase; opacity:0.95;">
    Communication Effectiveness
  </div>
  <div style="font-size:4.6rem; font-weight:900; line-height:1; margin:0.35rem 0;">
    {score}
  </div>
  <div style="opacity:0.85; font-weight:700;">out of 100</div>
  <div style="margin-top:1rem; display:inline-block; padding:0.45rem 1.1rem; border-radius:999px; background:rgba(255,255,255,0.18); font-weight:800;">
    {verdict}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive summary
    st.markdown(
        """
<div class="section-header">
  <div class="section-icon">📋</div>
  <h3 class="section-title">Executive summary</h3>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="executive-summary">
  {analysis["executive_summary"]}
</div>
""",
        unsafe_allow_html=True,
    )

    # Sub-scores
    st.markdown(
        """
<div class="section-header">
  <div class="section-icon">📊</div>
  <h3 class="section-title">Performance breakdown</h3>
</div>
""",
        unsafe_allow_html=True,
    )
    cols = st.columns(5)
    sub = analysis["sub_scores"]
    labels = [
        ("clarity", "Clarity"),
        ("authority", "Authority"),
        ("audience_adaptation", "Audience fit"),
        ("persuasion", "Persuasion"),
        ("emotional_regulation", "Composure"),
    ]
    for c, (k, label) in zip(cols, labels):
        with c:
            render_subscore(sub[k], label)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strengths / improvements
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
<div class="section-header">
  <div class="section-icon">💪</div>
  <h3 class="section-title">Strengths</h3>
</div>
""",
            unsafe_allow_html=True,
        )
        for s_ in analysis["strengths"]:
            st.markdown(
                f"""
<div class="insight-card">
  <div class="insight-icon insight-icon-strength">✓</div>
  <div style="flex:1;">
    <div class="insight-title">{s_["title"]}</div>
    <div class="insight-text">{s_["detail"]}</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
<div class="section-header">
  <div class="section-icon">🎯</div>
  <h3 class="section-title">Areas to improve</h3>
</div>
""",
            unsafe_allow_html=True,
        )
        for imp in analysis["improvements"]:
            st.markdown(
                f"""
<div class="insight-card">
  <div class="insight-icon insight-icon-improve">↑</div>
  <div style="flex:1;">
    <div class="insight-title">{imp["title"]}</div>
    <div class="insight-text">{imp["detail"]}</div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    # Key moments
    st.markdown(
        """
<div class="section-header">
  <div class="section-icon">⚡</div>
  <h3 class="section-title">Key moments</h3>
</div>
""",
        unsafe_allow_html=True,
    )
    for moment in analysis["key_moments"]:
        cls = {
            "positive": "insight-icon-strength",
            "negative": "insight-icon-improve",
            "neutral": "insight-icon-moment",
        }.get(moment["impact"], "insight-icon-moment")
        icon = {"positive": "↑", "negative": "↓", "neutral": "→"}.get(
            moment["impact"], "•"
        )
        st.markdown(
            f"""
<div class="insight-card">
  <div class="insight-icon {cls}">{icon}</div>
  <div style="flex:1;">
    <div class="insight-title">{moment["timestamp"].title()}: {moment["title"]}</div>
    <div class="insight-text">{moment["insight"]}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Cognitive load
    st.markdown(
        """
<div class="section-header">
  <div class="section-icon">🧠</div>
  <h3 class="section-title">Cognitive load</h3>
</div>
""",
        unsafe_allow_html=True,
    )

    def cog_class(level: str) -> str:
        return {"low": "cog-low", "medium": "cog-medium", "high": "cog-high"}.get(
            level.lower(), "cog-medium"
        )

    cog = analysis["cognitive_load"]
    st.markdown(
        f"""
<div class="cog-meter">
  <div class="cog-meter-row">
    <span class="cog-meter-label">Overall cognitive load</span>
    <span class="cog-meter-value {cog_class(cog["overall"])}">{cog["overall"].title()}</span>
  </div>
  <div class="cog-meter-row">
    <span class="cog-meter-label">Jargon density</span>
    <span class="cog-meter-value {cog_class(cog["jargon"])}">{cog["jargon"].title()}</span>
  </div>
  <div class="cog-meter-row">
    <span class="cog-meter-label">Sentence complexity</span>
    <span class="cog-meter-value {cog_class(cog["complexity"])}">{cog["complexity"].title()}</span>
  </div>
  <div class="cog-meter-row">
    <span class="cog-meter-label">Topic switching</span>
    <span class="cog-meter-value {cog_class(cog["topic_switches"])}">{cog["topic_switches"].title()}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # One thing
    st.markdown(
        """
<div class="section-header">
  <div class="section-icon">🎯</div>
  <h3 class="section-title">One thing to change</h3>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="cm-section" style="border-color: rgba(34,197,94,0.28); background: rgba(34,197,94,0.07);">
  <div style="font-size:0.78rem; font-weight:900; letter-spacing:0.14em; text-transform:uppercase; color: var(--accent-dark); margin-bottom:0.6rem;">
    Highest-impact action
  </div>
  <div style="font-size:1.2rem; font-weight:900; color: var(--text); line-height:1.5;">
    {analysis["one_thing"]}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Transcript + download
    with st.expander("📝 View full transcript"):
        st.markdown(
            f"""<div class="transcript-box">{transcript_text}</div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
<div class="report-footer">
  Analysis generated by CoMentor • {datetime.now().strftime('%B %d, %Y at %H:%M')}
</div>
""",
        unsafe_allow_html=True,
    )

    report_data = {
        "analysis": analysis,
        "transcript": transcript_text,
        "generated_at": datetime.now().isoformat(),
    }

    st.download_button(
        "📥 Download full report (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name=f"comentor_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Main app – landing‑style flow
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Sidebar: API key + meeting context
    with st.sidebar:
        st.markdown(
            """
<div style="padding: 0.5rem 0 0.25rem 0;">
  <div style="font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 0.9rem;">
    Configuration
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        env_has_key = bool(os.environ.get("OPENAI_API_KEY"))
        try:
            env_has_key = env_has_key or ("OPENAI_API_KEY" in st.secrets)
        except Exception:
            pass

        if not env_has_key:
            st.text_input(
                "OpenAI API Key",
                type="password",
                help="Not stored. For production, use Streamlit Secrets or environment variables.",
                key="openai_api_key",
            )

        st.markdown(
            """
<div style="padding: 1rem 0 0.25rem 0;">
  <div style="font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 0.9rem;">
    Meeting context
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        meeting_type = st.selectbox(
            "Meeting type",
            [
                "Board presentation",
                "Investor pitch",
                "Sales call",
                "Team update",
                "Negotiation",
                "Client meeting",
                "Media interview",
                "Other",
            ],
        )
        objective = st.selectbox(
            "Primary objective",
            [
                "Persuade / influence",
                "Inform / update",
                "Decide / align",
                "Build relationship",
                "Negotiate terms",
                "Defend position",
            ],
        )
        audience = st.selectbox(
            "Audience",
            [
                "C-suite / board",
                "Investors",
                "Senior leadership",
                "Clients",
                "Direct reports",
                "External stakeholders",
                "Media / public",
            ],
        )
        speaker_role = st.text_input(
            "Your role",
            placeholder="e.g., CEO, Founder, Managing Director",
        )

    # Hero – always visible as landing top section
    render_hero()

    client = init_openai_client()
    if not client:
        st.markdown(
            """
<div class="cm-section" style="text-align:center;">
  <div style="font-size:2.25rem; margin-bottom:0.5rem;">🔐</div>
  <h3 style="margin:0; font-weight:900; letter-spacing:-0.02em;">
    Add your OpenAI API key to start
  </h3>
  <p style="color: var(--muted); margin-top:0.6rem; line-height:1.6;">
    Use the sidebar for local testing, or configure environment variables / Streamlit Secrets for deployment.
  </p>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    # If we already have a completed analysis, show report-first (post-landing)
    if st.session_state.get("show_results") and "analysis" in st.session_state:
        render_report(
            st.session_state["analysis"],
            st.session_state.get("transcript", ""),
        )
        if st.button("← Analyze another conversation", use_container_width=True):
            st.session_state["show_results"] = False
            st.session_state.pop("analysis", None)
            st.session_state.pop("transcript", None)
            st.rerun()
        return

    # Landing “Get started” section: record/upload tabs
    st.markdown('<div class="cm-section">', unsafe_allow_html=True)
    tab_record, tab_upload = st.tabs(["🎙️ Record now", "📁 Upload recording"])

    meeting_context = {
        "meeting_type": meeting_type,
        "objective": objective,
        "audience": audience,
        "speaker_role": speaker_role or "Executive",
    }

    # RECORD TAB
    with tab_record:
        st.markdown(
            """
<div class="cm-strip">
  <h3>Record a short segment</h3>
  <p>Capture 2–5 minutes of a live pitch, update, or practice run. Add context in the sidebar for sharper coaching.</p>
</div>
""",
            unsafe_allow_html=True,
        )

        try:
            audio_value = st.audio_input("Record your audio", key="audio_recorder")

            if audio_value:
                st.audio(audio_value)

                if st.button(
                    "Analyze recording", key="analyze_recorded", use_container_width=True
                ):
                    with st.status(
                        "Analyzing your communication...", expanded=True
                    ) as status:
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".wav"
                        ) as tmp:
                            tmp.write(audio_value.getvalue())
                            tmp_path = tmp.name

                        try:
                            status.write("🎙️ Transcribing with Whisper…")
                            transcript = transcribe_audio(client, tmp_path)
                            transcript_text = transcript.text

                            status.write("🧠 Running communication analysis…")
                            analysis = analyze_communication(
                                client, transcript_text, meeting_context
                            )

                            st.session_state["analysis"] = analysis
                            st.session_state["transcript"] = transcript_text
                            st.session_state["show_results"] = True

                            status.update(
                                label="Analysis complete – scroll up for your report.",
                                state="complete",
                            )
                            st.rerun()
                        finally:
                            os.unlink(tmp_path)

        except Exception:
            st.info(
                "Recording requires a recent Streamlit version (1.33+). If this does not appear, use the Upload tab instead."
            )

    # UPLOAD TAB
    with tab_upload:
        st.markdown(
            """
<div class="cm-strip">
  <h3>Upload a recording</h3>
  <p>Upload audio or video of a meeting, pitch, or conversation. Shorter clips run faster and cost less.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Drag and drop your recording",
            type=["mp3", "mp4", "wav", "m4a", "webm", "mpeg4", "ogg"],
            help="Supported formats: MP3, MP4, WAV, M4A, WebM, OGG",
        )

        if uploaded:
            size_mb = uploaded.size / 1024 / 1024
            st.markdown(
                f"""
<div style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.5rem 0.9rem;border-radius:999px;border:1px solid var(--border);background:var(--soft);font-weight:800;color:var(--text);">
  ✓ {uploaded.name} ({size_mb:.1f} MB)
</div>
""",
                unsafe_allow_html=True,
            )
            st.audio(uploaded)

            if st.button(
                "Analyze upload", key="analyze_uploaded", use_container_width=True
            ):
                with st.status(
                    "Analyzing your communication...", expanded=True
                ) as status:
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=os.path.splitext(uploaded.name)[1]
                    ) as tmp:
                        tmp.write(uploaded.getvalue())
                        tmp_path = tmp.name

                    try:
                        status.write("📝 Transcribing with Whisper…")
                        transcript = transcribe_audio(client, tmp_path)
                        transcript_text = transcript.text
                        status.write(
                            f"✓ Transcribed {len(transcript_text.split())} words."
                        )

                        status.write("🧠 Running communication analysis…")
                        analysis = analyze_communication(
                            client, transcript_text, meeting_context
                        )

                        st.session_state["analysis"] = analysis
                        st.session_state["transcript"] = transcript_text
                        st.session_state["show_results"] = True

                        status.update(
                            label="Analysis complete – scroll up for your report.",
                            state="complete",
                        )
                        st.rerun()

                    except Exception as e:
                        status.update(label="Analysis failed", state="error")
                        st.error(f"Analysis failed: {e}")
                    finally:
                        os.unlink(tmp_path)
        else:
            st.markdown(
                """
<div style="text-align: center; padding: 1.5rem; color: var(--muted);">
  <p style="margin:0;">Upload a recording of a meeting, board update, investor pitch, or practice run to generate an executive-grade communication report.</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
