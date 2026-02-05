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

# Premium CSS styling
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header styling */
    .hero-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    .brand-logo {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .brand-logo-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .brand-tagline {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.7);
        font-weight: 400;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Recording section */
    .record-container {
        background: linear-gradient(180deg, #fafbfc 0%, #f1f5f9 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .record-btn-container {
        margin: 1.5rem 0;
    }
    
    .recording-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .status-ready {
        background: #e0f2fe;
        color: #0369a1;
    }
    
    .status-recording {
        background: #fee2e2;
        color: #dc2626;
        animation: pulse 1.5s infinite;
    }
    
    .status-complete {
        background: #d1fae5;
        color: #059669;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse-dot {
        width: 10px;
        height: 10px;
        background: #dc2626;
        border-radius: 50%;
        animation: pulse-dot 1s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    /* Upload area */
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(180deg, #fafbfc 0%, #f1f5f9 100%);
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #3b82f6;
        background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);
    }
    
    /* Score card - main CES */
    .ces-container {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
    }
    
    .ces-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    .ces-label {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .ces-score {
        font-size: 5rem;
        font-weight: 700;
        line-height: 1;
        margin: 0.5rem 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .ces-max {
        font-size: 1.25rem;
        opacity: 0.8;
    }
    
    .ces-verdict {
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 1rem;
        padding: 0.5rem 1.5rem;
        background: rgba(255,255,255,0.2);
        border-radius: 30px;
        display: inline-block;
    }
    
    /* Sub-score cards */
    .subscore-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f5;
        transition: all 0.3s ease;
    }
    
    .subscore-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .subscore-value {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .subscore-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    .subscore-bar {
        height: 6px;
        background: #e5e7eb;
        border-radius: 3px;
        margin-top: 1rem;
        overflow: hidden;
    }
    
    .subscore-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 1s ease-out;
    }
    
    /* Executive summary */
    .executive-summary {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-left: 4px solid #3b82f6;
        padding: 1.5rem 2rem;
        border-radius: 0 12px 12px 0;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #334155;
    }
    
    /* Insight cards */
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f5;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .insight-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .insight-icon-strength {
        background: #d1fae5;
        color: #059669;
    }
    
    .insight-icon-improve {
        background: #fef3c7;
        color: #d97706;
    }
    
    .insight-icon-moment {
        background: #dbeafe;
        color: #2563eb;
    }
    
    .insight-content {
        flex: 1;
    }
    
    .insight-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    
    .insight-text {
        font-size: 0.925rem;
        color: #4b5563;
        line-height: 1.5;
    }
    
    /* One thing to change - hero action */
    .action-hero {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }
    
    .action-hero-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #92400e;
        margin-bottom: 0.75rem;
    }
    
    .action-hero-text {
        font-size: 1.25rem;
        font-weight: 600;
        color: #78350f;
        line-height: 1.5;
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1.25rem 0;
    }
    
    .section-icon {
        width: 32px;
        height: 32px;
        background: #f3f4f6;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin: 0;
    }
    
    /* Cognitive load meter */
    .cog-meter {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f5;
    }
    
    .cog-meter-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .cog-meter-row:last-child {
        border-bottom: none;
    }
    
    .cog-meter-label {
        font-size: 0.925rem;
        color: #4b5563;
    }
    
    .cog-meter-value {
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
    }
    
    .cog-low { background: #d1fae5; color: #059669; }
    .cog-medium { background: #fef3c7; color: #d97706; }
    .cog-high { background: #fee2e2; color: #dc2626; }
    
    /* Report footer */
    .report-footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #9ca3af;
        font-size: 0.875rem;
    }
    
    /* Loading animation */
    .loading-container {
        text-align: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid #f3f4f6;
        border-top: 4px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1.5rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-size: 1.1rem;
        color: #4b5563;
        font-weight: 500;
    }
    
    .loading-subtext {
        font-size: 0.925rem;
        color: #9ca3af;
        margin-top: 0.5rem;
    }
    
    /* Transcript box */
    .transcript-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 0.875rem;
        line-height: 1.7;
        color: #374151;
        max-height: 400px;
        overflow-y: auto;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-success {
        background: #d1fae5;
        color: #059669;
    }
    
    /* Audio recorder custom styling */
    .audio-recorder-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    /* Timer display */
    .timer-display {
        font-size: 2.5rem;
        font-weight: 600;
        font-family: 'SF Mono', 'Monaco', monospace;
        color: #1f2937;
        margin: 1rem 0;
    }
    
    .timer-recording {
        color: #dc2626;
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
    """Render the hero header."""
    st.markdown("""
    <div class="hero-header">
        <div class="brand-logo">
            <div class="brand-logo-icon">◐</div>
            CoMentor
        </div>
        <div class="brand-tagline">Executive Communication Intelligence</div>
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
