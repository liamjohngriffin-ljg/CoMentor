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

# Page configuration
st.set_page_config(
    page_title="CoMentor | Communication Intelligence",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean landing-page CSS (Grammarly-inspired: minimal, airy, green accent)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root{
  --bg: #ffffff;
  --text: #0f172a;
  --muted: #475569;
  --border: #e2e8f0;
  --card: #ffffff;
  --soft: #f8fafc;
  --accent: #22c55e;      /* clean green */
  --accent-dark: #16a34a;
  --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  --shadow-sm: 0 6px 18px rgba(15, 23, 42, 0.06);
  --radius: 18px;
}

.stApp {
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Constrain content width like a marketing site */
.block-container{
  max-width: 1120px;
  padding-top: 2.0rem;
  padding-bottom: 4rem;
}

/* Sidebar: lighter, cleaner */
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

/* Inputs */
.stSelectbox, .stTextInput, .stFileUploader {
  border-radius: 12px;
}

/* Tabs: minimal pill style */
.stTabs [data-baseweb="tab-list"] {
  gap: 10px;
  background: transparent;
  padding: 0;
  border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 600;
  color: var(--muted);
  background: transparent;
}
.stTabs [aria-selected="true"] {
  background: rgba(34, 197, 94, 0.10);
  color: var(--text);
}

/* Buttons: green primary like Grammarly CTA */
.stButton > button {
  background: var(--accent);
  color: white;
  border: none;
  padding: 0.85rem 1.25rem;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  background: var(--accent-dark);
  box-shadow: var(--shadow);
}

/* Secondary button look (we’ll use st.button with custom class via markdown) */
.cm-secondary {
  display:inline-block;
  border: 1px solid var(--border);
  background: white;
  color: var(--text);
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  font-weight: 700;
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
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(34,197,94,0.14);
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight: 800;
  color: var(--accent-dark);
}
.cm-brandname {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.cm-badge {
  font-size: 0.8rem;
  font-weight: 700;
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
  font-size: 2.65rem;
  font-weight: 800;
  line-height: 1.06;
  letter-spacing: -0.03em;
  margin: 0 0 0.75rem 0;
}
.cm-sub {
  font-size: 1.1rem;
  color: var(--muted);
  line-height: 1.6;
  margin: 0 0 1.25rem 0;
}
.cm-cta-row {
  display:flex;
  gap: 12px;
  align-items:center;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
.cm-proof {
  margin-top: 1.0rem;
  color: #64748b;
  font-size: 0.95rem;
}
.cm-proof strong { color: var(--text); }

/* Feature cards */
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
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
}
.cm-card-title{
  font-weight: 800;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.01em;
}
.cm-card-text{
  margin: 0;
  color: var(--muted);
  line-height: 1.55;
  font-size: 0.95rem;
}
.cm-mini{
  font-size: 0.85rem;
  color: #64748b;
}

/* Section wrapper */
.cm-section {
  margin-top: 1.75rem;
  border: 1px solid var(--border);
  background: white;
  border-radius: var(--radius);
  padding: 1.5rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

/* Keep your report components working, but soften them */
.ces-container {
  border-radius: 22px !important;
  box-shadow: var(--shadow) !important;
}
.subscore-card, .insight-card, .cog-meter {
  border: 1px solid var(--border) !important;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05) !important;
}
.executive-summary {
  border-left: 4px solid var(--accent) !important;
}

/* Muted divider */
.cm-divider {
  height: 1px;
  background: var(--border);
  margin: 1.25rem 0;
}
</style>
""", unsafe_allow_html=True)


# Audio recorder JavaScript component
AUDIO_RECORDER_HTML = """
<div id="audio-recorder-container" style="text-align: center; padding: 20px;">
    <div id="status" class="recording-status status-ready">
        <span>🎙️</span> Ready to record
    </div>
    
    <div id="timer" style="font-size: 2.5rem; font-weight: 600; font-family: monospace; color: #1f2937; margin: 1.5rem 0;">
        00:00
    </div>
    
    <div style="display: flex; gap: 12px; justify-content: center; margin: 1.5rem 0;">
        <button id="recordBtn" onclick="toggleRecording()" style="
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
            transition: all 0.3s ease;
        ">
            <span id="recordIcon">⏺</span>
            <span id="recordText">Start Recording</span>
        </button>
    </div>
    
    <div id="audioPreview" style="display: none; margin-top: 1.5rem;">
        <audio id="audioPlayback" controls style="width: 100%; max-width: 400px;"></audio>
        <div style="margin-top: 1rem;">
            <button onclick="submitAudio()" style="
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 1rem;
                font-weight: 600;
                border-radius: 10px;
                cursor: pointer;
                margin-right: 8px;
                box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
            ">✓ Use This Recording</button>
            <button onclick="resetRecording()" style="
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                padding: 12px 24px;
                font-size: 1rem;
                font-weight: 500;
                border-radius: 10px;
                cursor: pointer;
            ">↺ Record Again</button>
        </div>
    </div>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let timerInterval;
let seconds = 0;
let audioBlob;

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(audioBlob);
            document.getElementById('audioPlayback').src = audioUrl;
            document.getElementById('audioPreview').style.display = 'block';
            
            // Update status
            document.getElementById('status').className = 'recording-status status-complete';
            document.getElementById('status').innerHTML = '<span>✓</span> Recording complete';
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        document.getElementById('recordBtn').style.background = 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)';
        document.getElementById('recordBtn').style.boxShadow = '0 4px 15px rgba(107, 114, 128, 0.3)';
        document.getElementById('recordIcon').textContent = '⏹';
        document.getElementById('recordText').textContent = 'Stop Recording';
        document.getElementById('status').className = 'recording-status status-recording';
        document.getElementById('status').innerHTML = '<div class="pulse-dot"></div> Recording...';
        document.getElementById('audioPreview').style.display = 'none';
        
        // Start timer
        seconds = 0;
        timerInterval = setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
            const secs = (seconds % 60).toString().padStart(2, '0');
            document.getElementById('timer').textContent = `${mins}:${secs}`;
            document.getElementById('timer').style.color = '#dc2626';
        }, 1000);
        
    } catch (err) {
        alert('Could not access microphone. Please allow microphone access and try again.');
        console.error('Error accessing microphone:', err);
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        
        // Update UI
        document.getElementById('recordBtn').style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)';
        document.getElementById('recordBtn').style.boxShadow = '0 4px 15px rgba(220, 38, 38, 0.3)';
        document.getElementById('recordIcon').textContent = '⏺';
        document.getElementById('recordText').textContent = 'Start Recording';
        document.getElementById('timer').style.color = '#1f2937';
        
        // Stop timer
        clearInterval(timerInterval);
    }
}

function resetRecording() {
    document.getElementById('audioPreview').style.display = 'none';
    document.getElementById('timer').textContent = '00:00';
    document.getElementById('status').className = 'recording-status status-ready';
    document.getElementById('status').innerHTML = '<span>🎙️</span> Ready to record';
    seconds = 0;
    audioBlob = null;
}

function submitAudio() {
    if (audioBlob) {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64data = reader.result.split(',')[1];
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: base64data
            }, '*');
            
            // Also try the Streamlit component method
            if (window.Streamlit) {
                window.Streamlit.setComponentValue(base64data);
            }
        };
        reader.readAsDataURL(audioBlob);
        
        document.getElementById('status').innerHTML = '<span>📤</span> Sending audio...';
    }
}

// Initialize Streamlit component communication
if (window.Streamlit) {
    window.Streamlit.setComponentReady();
}
</script>
"""


api_key = (
    os.environ.get("OPENAI_API_KEY")
    or st.secrets.get("OPENAI_API_KEY", None)
    or st.session_state.get("openai_api_key")
)



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
    """Analyze communication using GPT-4."""
    
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
        temperature=0.7,
        max_tokens=2500
    )
    
    response_text = response.choices[0].message.content.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    response_text = response_text.strip()
    
    return json.loads(response_text)


def get_score_color(score):
    """Return color based on score."""
    if score >= 80:
        return "#059669"
    elif score >= 60:
        return "#3b82f6"
    elif score >= 40:
        return "#d97706"
    else:
        return "#dc2626"


def render_header():
    """Render a clean, landing-page hero (marketing style)."""
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
            Upload or record a high-stakes conversation and get a coaching-grade analysis:
            what worked, what didn’t, and the single highest-leverage change for next time.
          </p>

          <div class="cm-cta-row">
            <!-- Primary CTA is your tab + record button below; this is just visual framing -->
            <span class="cm-mini">Tip: Add context in the left panel for sharper feedback.</span>
          </div>

          <div class="cm-proof">
            <strong>Outputs:</strong> Effectiveness score, strengths, fixes, key moments, cognitive load, and “ONE thing” action.
          </div>
        </div>

        <div>
          <div class="cm-card">
            <p class="cm-card-title">What you’ll get</p>
            <p class="cm-card-text">A structured report you can act on immediately—no fluff.</p>
            <div class="cm-divider"></div>
            <p class="cm-card-text"><strong>Best for:</strong> board updates, investor pitches, negotiations, client meetings.</p>
          </div>
        </div>
      </div>

      <div class="cm-cards">
        <div class="cm-card">
          <p class="cm-card-title">Executive-grade clarity</p>
          <p class="cm-card-text">Flags vague sections and gives a rewrite-level fix you can reuse.</p>
        </div>
        <div class="cm-card">
          <p class="cm-card-title">Authority & persuasion</p>
          <p class="cm-card-text">Identifies where you lose leverage—and what to say instead.</p>
        </div>
        <div class="cm-card">
          <p class="cm-card-title">Cognitive load control</p>
          <p class="cm-card-text">Detects jargon/complexity spikes that make audiences tune out.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)



def render_subscore(score, label):
    """Render a single subscore card."""
    color = get_score_color(score)
    st.markdown(f"""
    <div class="subscore-card">
        <div class="subscore-value" style="color: {color};">{score}</div>
        <div class="subscore-label">{label}</div>
        <div class="subscore-bar">
            <div class="subscore-fill" style="width: {score}%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_report(analysis, transcript):
    """Render the full analysis report."""
    
    ces = analysis['communication_effectiveness_score']
    verdict = analysis.get('score_verdict', 'Competent')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="ces-container">
            <div class="ces-label">Communication Effectiveness Score</div>
            <div class="ces-score">{ces}</div>
            <div class="ces-max">out of 100</div>
            <div class="ces-verdict">{verdict}</div>
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
                <div class="insight-content">
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
                <div class="insight-content">
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
            <div class="insight-content">
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
    <div class="action-hero">
        <div class="action-hero-label">Your Highest-Impact Action</div>
        <div class="action-hero-text">{analysis['one_thing']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Transcript
    with st.expander("📝 View Full Transcript"):
        st.markdown(f"""
        <div class="transcript-box">{transcript}</div>
        """, unsafe_allow_html=True)
    
    # Report footer
    st.markdown(f"""
    <div class="report-footer">
        Analysis generated by CoMentor • {datetime.now().strftime('%B %d, %Y at %H:%M')}
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
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
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        if is_base64:
            tmp.write(base64.b64decode(audio_data))
        else:
            tmp.write(audio_data)
        tmp_path = tmp.name
    
    try:
        # Transcribe
        transcript = transcribe_audio(client, tmp_path)
        transcript_text = transcript.text
        
        # Analyze
        analysis = analyze_communication(client, transcript_text, meeting_context)
        
        return analysis, transcript_text
        
    finally:
        os.unlink(tmp_path)


def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0;">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; margin-bottom: 1rem;">
                Configuration
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Only show API key input if not set in environment
        if not os.environ.get('OPENAI_API_KEY'):
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key",
                key="openai_api_key"
            )
        
        st.markdown("""
        <div style="padding: 1rem 0;">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; margin-bottom: 1rem;">
                Meeting Context
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
    
    # Main content
    render_header()
    
    client = init_openai_client()
    
    if not client:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
            <h3>Enter your OpenAI API key to begin</h3>
            <p style="color: #6b7280;">Add your API key in the sidebar to unlock communication analysis</p>
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
    
    # Input tabs
    tab1, tab2 = st.tabs(["🎙️ Record Audio", "📁 Upload File"])
    
    meeting_context = {
        "meeting_type": meeting_type,
        "objective": objective,
        "audience": audience,
        "speaker_role": speaker_role or "Executive"
    }
    
    with tab1:
        st.markdown("""
        <div class="record-container">
            <h3 style="margin-top: 0; color: #1f2937;">Record Your Communication</h3>
            <p style="color: #6b7280;">Click the button below to start recording. Speak clearly for best results.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use streamlit-webrtc or audio_recorder_streamlit for recording
        # For now, we'll use a simpler approach with st.audio_input (Streamlit 1.33+)
        
        try:
            audio_value = st.audio_input("Record your audio", key="audio_recorder")
            
            if audio_value:
                st.audio(audio_value)
                
                if st.button("🚀 Analyze Recording", key="analyze_recorded", use_container_width=True):
                    with st.status("Analyzing your communication...", expanded=True) as status:
                        st.write("🎙️ Processing audio...")
                        
                        # Save audio to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                            tmp.write(audio_value.getvalue())
                            tmp_path = tmp.name
                        
                        try:
                            st.write("📝 Transcribing with Whisper AI...")
                            transcript = transcribe_audio(client, tmp_path)
                            transcript_text = transcript.text
                            
                            st.write("🧠 Running deep analysis with GPT-4...")
                            analysis = analyze_communication(client, transcript_text, meeting_context)
                            
                            st.session_state['analysis'] = analysis
                            st.session_state['transcript'] = transcript_text
                            st.session_state['show_results'] = True
                            
                            status.update(label="Analysis complete!", state="complete")
                            st.rerun()
                            
                        finally:
                            os.unlink(tmp_path)
                            
        except Exception as e:
            st.info("🎙️ Audio recording requires Streamlit 1.33 or later. Please use the **Upload File** tab instead, or update Streamlit.")
    
    with tab2:
        st.markdown("### Upload Recording")
        
        uploaded_file = st.file_uploader(
            "Drag and drop your meeting recording",
            type=['mp3', 'mp4', 'wav', 'm4a', 'webm', 'mpeg4', 'ogg'],
            help="Supported: MP3, MP4, WAV, M4A, WebM, OGG (max 200MB)"
        )
        
        if uploaded_file:
            st.markdown(f"""
            <div class="status-badge status-success">
                ✓ {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.1f} MB)
            </div>
            """, unsafe_allow_html=True)
            
            st.audio(uploaded_file)
            
            if st.button("🚀 Analyze Communication", key="analyze_uploaded", use_container_width=True):
                # Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    with st.status("Analyzing your communication...", expanded=True) as status:
                        st.write("📝 Transcribing with Whisper AI...")
                        transcript = transcribe_audio(client, tmp_path)
                        transcript_text = transcript.text
                        st.write(f"✓ Transcribed {len(transcript_text.split())} words")
                        
                        st.write("🧠 Running deep analysis with GPT-4...")
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
            <div style="text-align: center; padding: 2rem; color: #6b7280;">
                <p>Upload an audio or video recording of a meeting, presentation, or conversation.</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
