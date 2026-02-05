
"""
CoMentor - Executive Communication Intelligence
================================================
AI-powered communication analysis for high-stakes conversations
Record or upload meetings to get actionable insights
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import tempfile
import os
import json
from openai import OpenAI
from datetime import datetime
import base64


# ──────────────────────────────────────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoMentor | Communication Intelligence",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("### ✅ CoMentor UI VERSION: 2026-02-05  (if you don't see this, Streamlit isn't running your latest code)")


# ──────────────────────────────────────────────────────────────────────────────
# Grammarly-like landing CSS (clean, airy, green accent)
# IMPORTANT: This also overrides many default Streamlit widget styles.
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
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
  --accent: #22c55e;      /* clean green */
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

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Make the app feel like a marketing site */
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

/* Text inputs / selects / uploader */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
div[data-testid="stFileUploader"] section {
  border-radius: 12px !important;
}

/* Tabs: simple pills */
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

/* Buttons: green CTA */
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
  grid-template-columns: 1.2fr 0.8fr;
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

.cm-section {
  margin-top: 1.5rem;
  border: 1px solid var(--border);
  background: white;
  border-radius: var(--radius);
  padding: 1.35rem 1.35rem;
  box-shadow: var(--shadow-sm);
}

/* Light info strip inside tabs */
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

/* Soften native report components (your older CSS classes still referenced by report) */
.ces-container { border-radius: 22px !important; box-shadow: var(--shadow) !important; }
.subscore-card, .insight-card, .cog-meter {
  border: 1px solid var(--border) !important;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06) !important;
}
.executive-summary { border-left: 4px solid var(--accent) !important; }

/* Existing classes from your original report UI (kept so report still renders) */
.section-header { display:flex; align-items:center; gap:0.75rem; margin: 2rem 0 1.25rem 0; }
.section-icon { width:32px; height:32px; background:#f3f4f6; border-radius:8px; display:flex; align-items:center; justify-content:center; }
.section-title { font-size:1.25rem; font-weight:800; color:#111827; margin:0; }

.insight-card { background:white; border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:0.75rem; display:flex; align-items:flex-start; gap:1rem; }
.insight-icon { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0; }
.insight-icon-strength { background:#d1fae5; color:#059669; }
.insight-icon-improve { background:#fef3c7; color:#d97706; }
.insight-icon-moment { background:#dbeafe; color:#2563eb; }
.insight-title { font-weight:800; color:#1f2937; margin-bottom:0.25rem; }
.insight-text { font-size:0.925rem; color:#4b5563; line-height:1.5; }

.executive-summary { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem 2rem; border-radius: 0 12px 12px 0; font-size: 1.05rem; line-height: 1.7; color: #334155; }

.cog-meter { background:white; border-radius:12px; padding:1.5rem; }
.cog-meter-row { display:flex; justify-content:space-between; align-items:center; padding:0.75rem 0; border-bottom:1px solid #f3f4f6; }
.cog-meter-row:last-child { border-bottom:none; }
.cog-meter-label { font-size:0.925rem; color:#4b5563; }
.cog-meter-value { font-weight:800; padding:0.25rem 0.75rem; border-radius:20px; font-size:0.875rem; }
.cog-low { background:#d1fae5; color:#059669; }
.cog-medium { background:#fef3c7; color:#d97706; }
.cog-high { background:#fee2e2; color:#dc2626; }

.transcript-box {
  background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px; padding:1.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size:0.875rem; line-height:1.7; color:#374151; max-height:400px; overflow-y:auto;
}

.report-footer { margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border); text-align:center; color:#94a3b8; font-size:0.875rem; }

/* A small "version stamp" style */
.cm-version {
  color: #94a3b8;
  font-size: 0.82rem;
  margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI client init (FIXED: your previous code referenced init_openai_client()
# but didn't define it)
# ──────────────────────────────────────────────────────────────────────────────
def init_openai_client():
    api_key = (
        os.environ.get("OPENAI_API_KEY")
        or st.secrets.get("OPENAI_API_KEY", None)
        or st.session_state.get("openai_api_key")
    )
    if api_key:
        return OpenAI(api_key=api_key)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Core AI functions
# ──────────────────────────────────────────────────────────────────────────────
def transcribe_audio(client, audio_file_path):
    """Transcribe audio using OpenAI Whisper."""
    with open(audio_file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json"
        )
    return transcript


def analyze_communication(client, transcript_text, meeting_context):
    """Analyze communication using GPT-4o (JSON output)."""

    analysis_prompt = f"""You are an elite executive communication analyst with 20 years of experience coaching Fortune 500 CEOs, world leaders, and elite performers.

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
    "executive_summary": "<2-3 sentence high-level assessment written in a direct, executive tone>",
    "strengths": [
        {{
            "title": "<short strength name>",
            "detail": "<specific evidence and why it matters>"
        }},
        {{
            "title": "<short strength name>",
            "detail": "<specific evidence and why it matters>"
        }},
        {{
            "title": "<short strength name>",
            "detail": "<specific evidence and why it matters>"
        }}
    ],
    "improvements": [
        {{
            "title": "<short issue name>",
            "detail": "<what happened and specific fix>"
        }},
        {{
            "title": "<short issue name>",
            "detail": "<what happened and specific fix>"
        }}
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
    "one_thing": "<The single most impactful change - be specific and actionable>"
}}

Be direct. No fluff. Every insight must be actionable."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an elite executive communication analyst. Respond only with valid JSON, no markdown."},
            {"role": "user", "content": analysis_prompt}
        ],
        temperature=0.5,
        max_tokens=2500
    )

    response_text = response.choices[0].message.content.strip()

    # Defensive cleanup (in case of fenced output)
    if response_text.startswith("```"):
        parts = response_text.split("```")
        response_text = parts[1] if len(parts) > 1 else response_text
        if response_text.lstrip().startswith("json"):
            response_text = response_text.lstrip()[4:]

    response_text = response_text.strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Surface the raw text to help debug prompt compliance
        raise ValueError(f"Model did not return valid JSON. Raw output:\n{response_text}")


# ──────────────────────────────────────────────────────────────────────────────
# UI helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_score_color(score):
    if score >= 80:
        return "#059669"
    elif score >= 60:
        return "#16a34a"
    elif score >= 40:
        return "#d97706"
    return "#dc2626"


def render_header():
    """Marketing-style landing hero."""
    st.markdown("""
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
          <div class="cm-version">UI refresh • Grammarly-inspired landing</div>
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
          <p class="cm-card-text">Flags vague sections and gives concrete, reusable fixes.</p>
        </div>
        <div class="cm-card">
          <p class="cm-card-title">Authority & persuasion</p>
          <p class="cm-card-text">Shows where leverage drops—and what to say instead.</p>
        </div>
        <div class="cm-card">
          <p class="cm-card-title">Cognitive load control</p>
          <p class="cm-card-text">Detects jargon/complexity spikes that make audiences tune out.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_subscore(score, label):
    color = get_score_color(score)
    st.markdown(f"""
    <div class="subscore-card" style="text-align:center; border-radius:16px; padding:1.25rem;">
        <div class="subscore-value" style="color: {color}; font-size:2.1rem; font-weight:900; margin-bottom:0.25rem;">{score}</div>
        <div class="subscore-label" style="color:#6b7280; font-weight:700; font-size:0.9rem;">{label}</div>
        <div style="height:6px;background:#e5e7eb;border-radius:999px;margin-top:1rem;overflow:hidden;">
            <div style="height:100%;width:{score}%;background:{color};border-radius:999px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_report(analysis, transcript):
    ces = analysis['communication_effectiveness_score']
    verdict = analysis.get('score_verdict', 'Competent')

    # Top score (keep your original structure but it will be softened by CSS above)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="ces-container" style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color:white; padding:2.25rem; text-align:center;">
            <div style="font-size:0.85rem; font-weight:900; letter-spacing:0.12em; text-transform:uppercase; opacity:0.95;">Communication Effectiveness</div>
            <div style="font-size:4.6rem; font-weight:900; line-height:1; margin:0.35rem 0;">{ces}</div>
            <div style="opacity:0.85; font-weight:700;">out of 100</div>
            <div style="margin-top:1rem; display:inline-block; padding:0.45rem 1.1rem; border-radius:999px; background:rgba(255,255,255,0.18); font-weight:800;">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Summary
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📋</div>
        <h3 class="section-title">Executive Summary</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="executive-summary">
        {analysis['executive_summary']}
    </div>
    """, unsafe_allow_html=True)

    # Sub-scores
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📊</div>
        <h3 class="section-title">Performance Breakdown</h3>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    sub_scores = analysis['sub_scores']
    labels = [
        ("clarity", "Clarity"),
        ("authority", "Authority"),
        ("audience_adaptation", "Audience Fit"),
        ("persuasion", "Persuasion"),
        ("emotional_regulation", "Composure")
    ]
    for col, (key, label) in zip(cols, labels):
        with col:
            render_subscore(sub_scores[key], label)

    st.markdown("<br>", unsafe_allow_html=True)

    # Strengths & Improvements
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="section-header">
            <div class="section-icon">💪</div>
            <h3 class="section-title">Strengths</h3>
        </div>
        """, unsafe_allow_html=True)

        for strength in analysis['strengths']:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-icon insight-icon-strength">✓</div>
                <div style="flex:1;">
                    <div class="insight-title">{strength['title']}</div>
                    <div class="insight-text">{strength['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-header">
            <div class="section-icon">🎯</div>
            <h3 class="section-title">Areas to Improve</h3>
        </div>
        """, unsafe_allow_html=True)

        for improvement in analysis['improvements']:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-icon insight-icon-improve">↑</div>
                <div style="flex:1;">
                    <div class="insight-title">{improvement['title']}</div>
                    <div class="insight-text">{improvement['detail']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Key Moments
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">⚡</div>
        <h3 class="section-title">Key Moments</h3>
    </div>
    """, unsafe_allow_html=True)

    for moment in analysis['key_moments']:
        impact_class = {
            "positive": "insight-icon-strength",
            "negative": "insight-icon-improve",
            "neutral": "insight-icon-moment"
        }.get(moment['impact'], "insight-icon-moment")

        impact_icon = {"positive": "↑", "negative": "↓", "neutral": "→"}.get(moment['impact'], "•")

        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-icon {impact_class}">{impact_icon}</div>
            <div style="flex:1;">
                <div class="insight-title">{moment['timestamp'].title()}: {moment['title']}</div>
                <div class="insight-text">{moment['insight']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Cognitive Load
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🧠</div>
        <h3 class="section-title">Cognitive Load Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

    cog = analysis['cognitive_load']

    def get_cog_class(level):
        return {"low": "cog-low", "medium": "cog-medium", "high": "cog-high"}.get(level.lower(), "cog-medium")

    st.markdown(f"""
    <div class="cog-meter">
        <div class="cog-meter-row">
            <span class="cog-meter-label">Overall Cognitive Load</span>
            <span class="cog-meter-value {get_cog_class(cog['overall'])}">{cog['overall'].title()}</span>
        </div>
        <div class="cog-meter-row">
            <span class="cog-meter-label">Jargon Density</span>
            <span class="cog-meter-value {get_cog_class(cog['jargon'])}">{cog['jargon'].title()}</span>
        </div>
        <div class="cog-meter-row">
            <span class="cog-meter-label">Sentence Complexity</span>
            <span class="cog-meter-value {get_cog_class(cog['complexity'])}">{cog['complexity'].title()}</span>
        </div>
        <div class="cog-meter-row">
            <span class="cog-meter-label">Topic Switching</span>
            <span class="cog-meter-value {get_cog_class(cog['topic_switches'])}">{cog['topic_switches'].title()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # The ONE Thing
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🎯</div>
        <h3 class="section-title">The ONE Thing to Change</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cm-section" style="border-color: rgba(34,197,94,0.28); background: rgba(34,197,94,0.07);">
        <div style="font-size:0.78rem; font-weight:900; letter-spacing:0.14em; text-transform:uppercase; color: var(--accent-dark); margin-bottom:0.6rem;">
            Your highest-impact action
        </div>
        <div style="font-size:1.2rem; font-weight:900; color: var(--text); line-height:1.5;">
            {analysis['one_thing']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Transcript
    with st.expander("📝 View Full Transcript"):
        st.markdown(f"""<div class="transcript-box">{transcript}</div>""", unsafe_allow_html=True)

    # Footer + download
    st.markdown(f"""
    <div class="report-footer">
        Analysis generated by CoMentor • {datetime.now().strftime('%B %d, %Y at %H:%M')}
    </div>
    """, unsafe_allow_html=True)

    report_data = {
        "analysis": analysis,
        "transcript": transcript,
        "generated_at": datetime.now().isoformat()
    }

    st.download_button(
        "📥 Download Full Report (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name=f"comentor_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )


def process_audio(client, audio_data, meeting_context, is_base64=False):
    """Process audio data and run analysis."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        if is_base64:
            tmp.write(base64.b64decode(audio_data))
        else:
            tmp.write(audio_data)
        tmp_path = tmp.name

    try:
        transcript = transcribe_audio(client, tmp_path)
        transcript_text = transcript.text
        analysis = analyze_communication(client, transcript_text, meeting_context)
        return analysis, transcript_text
    finally:
        os.unlink(tmp_path)


# ──────────────────────────────────────────────────────────────────────────────
# Main app
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 0.25rem 0;">
            <div style="font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 0.9rem;">
                Configuration
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Only show API key input if not set in environment or secrets
        env_has_key = bool(os.environ.get("OPENAI_API_KEY")) or ("OPENAI_API_KEY" in st.secrets)
        if not env_has_key:
            st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key (not saved). Prefer Streamlit Secrets for deployment.",
                key="openai_api_key"
            )

        st.markdown("""
        <div style="padding: 1rem 0 0.25rem 0;">
            <div style="font-size: 0.75rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 0.9rem;">
                Meeting context
            </div>
        </div>
        """, unsafe_allow_html=True)

        meeting_type = st.selectbox(
            "Meeting Type",
            ["Board Presentation", "Investor Pitch", "Sales Call", "Team Update",
             "Negotiation", "Client Meeting", "Media Interview", "Other"]
        )

        objective = st.selectbox(
            "Primary Objective",
            ["Persuade / Influence", "Inform / Update", "Decide / Align",
             "Build Relationship", "Negotiate Terms", "Defend Position"]
        )

        audience = st.selectbox(
            "Audience",
            ["C-Suite / Board", "Investors", "Senior Leadership", "Clients",
             "Direct Reports", "External Stakeholders", "Media / Public"]
        )

        speaker_role = st.text_input(
            "Your Role",
            placeholder="e.g., CEO, Founder, Managing Director"
        )

    # Landing header
    render_header()

    # Client
    client = init_openai_client()

    if not client:
        st.markdown("""
        <div class="cm-section" style="text-align:center;">
          <div style="font-size:2.25rem; margin-bottom:0.5rem;">🔐</div>
          <h3 style="margin:0; font-weight:900; letter-spacing:-0.02em;">Add your OpenAI API key to start</h3>
          <p style="color: var(--muted); margin-top:0.6rem; line-height:1.6;">
            Use the sidebar for local testing, or Streamlit Secrets for deployment.
          </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Show results if available
    if 'analysis' in st.session_state and st.session_state.get('show_results'):
        render_report(st.session_state['analysis'], st.session_state['transcript'])

        if st.button("← Analyze Another Recording"):
            st.session_state['show_results'] = False
            st.rerun()
        return

    # Input tabs inside a “marketing” section card
    st.markdown('<div class="cm-section">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🎙️ Record Audio", "📁 Upload File"])

    meeting_context = {
        "meeting_type": meeting_type,
        "objective": objective,
        "audience": audience,
        "speaker_role": speaker_role or "Executive"
    }

    with tab1:
        st.markdown("""
        <div class="cm-strip">
          <h3>Record your communication</h3>
          <p>Record a short segment, then analyze. Add context on the left for sharper coaching.</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            audio_value = st.audio_input("Record your audio", key="audio_recorder")

            if audio_value:
                st.audio(audio_value)

                if st.button("Analyze Recording", key="analyze_recorded", use_container_width=True):
                    with st.status("Analyzing your communication...", expanded=True) as status:
                        st.write("🎙️ Processing audio...")

                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                            tmp.write(audio_value.getvalue())
                            tmp_path = tmp.name

                        try:
                            st.write("📝 Transcribing with Whisper...")
                            transcript = transcribe_audio(client, tmp_path)
                            transcript_text = transcript.text

                            st.write("🧠 Running communication analysis...")
                            analysis = analyze_communication(client, transcript_text, meeting_context)

                            st.session_state['analysis'] = analysis
                            st.session_state['transcript'] = transcript_text
                            st.session_state['show_results'] = True

                            status.update(label="Analysis complete!", state="complete")
                            st.rerun()
                        finally:
                            os.unlink(tmp_path)

        except Exception:
            st.info("Audio recording requires Streamlit 1.33+. Use the **Upload File** tab instead, or update Streamlit.")

    with tab2:
        st.markdown("""
        <div class="cm-strip">
          <h3>Upload a recording</h3>
          <p>Upload audio/video and analyze. Shorter clips run faster and cost less.</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drag and drop your meeting recording",
            type=['mp3', 'mp4', 'wav', 'm4a', 'webm', 'mpeg4', 'ogg'],
            help="Supported: MP3, MP4, WAV, M4A, WebM, OGG"
        )

        if uploaded_file:
            size_mb = uploaded_file.size / 1024 / 1024
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.5rem 0.9rem;border-radius:999px;border:1px solid var(--border);background:var(--soft);font-weight:800;color:var(--text);">
                ✓ {uploaded_file.name} ({size_mb:.1f} MB)
            </div>
            """, unsafe_allow_html=True)

            st.audio(uploaded_file)

            if st.button("Analyze Upload", key="analyze_uploaded", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    with st.status("Analyzing your communication...", expanded=True) as status:
                        st.write("📝 Transcribing with Whisper...")
                        transcript = transcribe_audio(client, tmp_path)
                        transcript_text = transcript.text
                        st.write(f"✓ Transcribed {len(transcript_text.split())} words")

                        st.write("🧠 Running communication analysis...")
                        analysis = analyze_communication(client, transcript_text, meeting_context)

                        st.session_state['analysis'] = analysis
                        st.session_state['transcript'] = transcript_text
                        st.session_state['show_results'] = True

                        status.update(label="Analysis complete!", state="complete")
                        st.rerun()

                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                finally:
                    os.unlink(tmp_path)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1.5rem; color: var(--muted);">
                <p style="margin:0;">Upload an audio or video recording of a meeting, presentation, or conversation.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

