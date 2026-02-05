"""
CommsVision MVP - Executive Communication Analysis Platform
============================================================
Upload meeting recordings → Get actionable communication insights
"""

import streamlit as st
import tempfile
import os
import json
from openai import OpenAI
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CommsVision | Executive Communication Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-score {
        font-size: 3rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .strength-tag {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.25rem;
    }
    .improvement-tag {
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


def init_openai_client():
    """Initialize OpenAI client with API key from sidebar or environment."""
    api_key = st.session_state.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
    if api_key:
        return OpenAI(api_key=api_key)
    return None


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
    """Analyze communication using GPT-4 and return structured insights."""
    
    analysis_prompt = f"""You are an expert executive communication analyst. Analyze this meeting transcript and provide a detailed assessment.

MEETING CONTEXT:
- Meeting Type: {meeting_context.get('meeting_type', 'Not specified')}
- Objective: {meeting_context.get('objective', 'Not specified')}
- Audience: {meeting_context.get('audience', 'Not specified')}
- Speaker Role: {meeting_context.get('speaker_role', 'Not specified')}

TRANSCRIPT:
{transcript_text}

Provide your analysis as a JSON object with this exact structure:
{{
    "communication_effectiveness_score": <0-100>,
    "sub_scores": {{
        "clarity": <0-100>,
        "authority": <0-100>,
        "audience_adaptation": <0-100>,
        "persuasion": <0-100>,
        "emotional_regulation": <0-100>
    }},
    "executive_summary": "<2-3 sentence overview of communication effectiveness>",
    "strengths": [
        "<specific strength 1 with evidence from transcript>",
        "<specific strength 2 with evidence from transcript>",
        "<specific strength 3 with evidence from transcript>"
    ],
    "areas_for_improvement": [
        {{
            "issue": "<specific issue>",
            "evidence": "<quote or pattern from transcript>",
            "recommendation": "<actionable advice>"
        }},
        {{
            "issue": "<specific issue>",
            "evidence": "<quote or pattern from transcript>",
            "recommendation": "<actionable advice>"
        }}
    ],
    "key_moments": [
        {{
            "timestamp_approx": "<early/middle/late in meeting>",
            "description": "<what happened>",
            "impact": "<positive/negative/neutral>",
            "coaching_note": "<what to do differently or continue doing>"
        }}
    ],
    "cognitive_load_assessment": {{
        "score": <0-100>,
        "jargon_density": "<low/medium/high>",
        "sentence_complexity": "<simple/moderate/complex>",
        "topic_switching": "<minimal/moderate/frequent>",
        "recommendation": "<specific advice>"
    }},
    "one_thing_to_change": "<the single highest-impact change for next time>"
}}

Be specific, cite evidence from the transcript, and focus on actionable insights. Be direct but constructive."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert executive communication coach. Always respond with valid JSON only, no markdown formatting."},
            {"role": "user", "content": analysis_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    # Parse the JSON response
    response_text = response.choices[0].message.content.strip()
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
    response_text = response_text.strip()
    
    return json.loads(response_text)


def display_score_gauge(score, label):
    """Display a score with visual indicator."""
    color = "#28a745" if score >= 75 else "#ffc107" if score >= 50 else "#dc3545"
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="font-size: 2.5rem; font-weight: 700; color: {color};">{score}</div>
        <div style="font-size: 0.9rem; color: #666;">{label}</div>
        <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
            <div style="background: {color}; width: {score}%; height: 100%; border-radius: 10px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<p class="main-header">📊 CommsVision</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Executive Communication Analysis Platform</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. Get one at platform.openai.com",
            key="openai_api_key"
        )
        
        if api_key:
            st.success("✓ API key configured")
        else:
            st.warning("Enter your OpenAI API key to begin")
        
        st.divider()
        
        st.header("📋 Meeting Context")
        st.caption("Providing context improves analysis accuracy")
        
        meeting_type = st.selectbox(
            "Meeting Type",
            ["Board Presentation", "Sales Pitch", "Team Update", "Negotiation", 
             "Performance Review", "Client Meeting", "Interview", "Other"]
        )
        
        objective = st.selectbox(
            "Primary Objective",
            ["Persuade / Influence", "Inform / Update", "Decide / Align", 
             "Build Relationship", "Negotiate", "Other"]
        )
        
        audience = st.selectbox(
            "Audience Seniority",
            ["C-Suite / Board", "Senior Leadership", "Peers", "Direct Reports", 
             "External Stakeholders", "Mixed"]
        )
        
        speaker_role = st.text_input(
            "Your Role",
            placeholder="e.g., CEO, Sales Director, Consultant"
        )
    
    # Main content area
    client = init_openai_client()
    
    if not client:
        st.info("👈 Enter your OpenAI API key in the sidebar to get started")
        
        # Show demo/example
        with st.expander("📖 See example analysis output"):
            st.image("https://via.placeholder.com/800x400?text=Example+Analysis+Dashboard", 
                     caption="Example of a completed analysis")
            st.markdown("""
            **What you'll get:**
            - Communication Effectiveness Score (0-100)
            - Sub-scores for Clarity, Authority, Persuasion, and more
            - Specific strengths with evidence from your recording
            - Actionable improvement recommendations
            - Key moments analysis
            - The ONE thing to change for maximum impact
            """)
        return
    
    # File upload section
    st.header("📁 Upload Recording")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your meeting recording",
            type=['mp3', 'mp4', 'wav', 'm4a', 'webm'],
            help="Supported formats: MP3, MP4, WAV, M4A, WebM (max 25MB)"
        )
    
    with col2:
        st.markdown("""
        **Tips for best results:**
        - Clear audio quality
        - 5-30 minute recordings
        - Single speaker focus works best
        """)
    
    if uploaded_file:
        st.success(f"✓ Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.1f} MB)")
        
        # Analysis button
        if st.button("🚀 Analyze Communication", type="primary", use_container_width=True):
            
            meeting_context = {
                "meeting_type": meeting_type,
                "objective": objective,
                "audience": audience,
                "speaker_role": speaker_role
            }
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Step 1: Transcription
                with st.status("Analyzing your communication...", expanded=True) as status:
                    st.write("🎙️ Transcribing audio...")
                    transcript = transcribe_audio(client, tmp_file_path)
                    transcript_text = transcript.text
                    st.write(f"✓ Transcribed {len(transcript_text.split())} words")
                    
                    # Step 2: Analysis
                    st.write("🧠 Analyzing communication patterns...")
                    analysis = analyze_communication(client, transcript_text, meeting_context)
                    st.write("✓ Analysis complete")
                    
                    status.update(label="Analysis complete!", state="complete", expanded=False)
                
                # Store results in session state
                st.session_state['analysis'] = analysis
                st.session_state['transcript'] = transcript_text
                st.session_state['meeting_context'] = meeting_context
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return
            finally:
                # Clean up temp file
                os.unlink(tmp_file_path)
    
    # Display results if available
    if 'analysis' in st.session_state:
        analysis = st.session_state['analysis']
        
        st.divider()
        st.header("📊 Communication Analysis Report")
        st.caption(f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        
        # Main CES Score
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            ces = analysis['communication_effectiveness_score']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">COMMUNICATION EFFECTIVENESS SCORE</div>
                <div class="metric-score">{ces}</div>
                <div class="metric-label">out of 100</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Executive Summary
        st.subheader("Executive Summary")
        st.info(analysis['executive_summary'])
        
        # Sub-scores
        st.subheader("Performance Breakdown")
        sub_scores = analysis['sub_scores']
        cols = st.columns(5)
        
        score_labels = [
            ("clarity", "Clarity"),
            ("authority", "Authority"),
            ("audience_adaptation", "Audience Fit"),
            ("persuasion", "Persuasion"),
            ("emotional_regulation", "Composure")
        ]
        
        for col, (key, label) in zip(cols, score_labels):
            with col:
                display_score_gauge(sub_scores[key], label)
        
        # Strengths and Improvements
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 Strengths")
            for strength in analysis['strengths']:
                st.markdown(f'<span class="strength-tag">✓</span> {strength}', unsafe_allow_html=True)
        
        with col2:
            st.subheader("🎯 Areas for Improvement")
            for item in analysis['areas_for_improvement']:
                with st.expander(f"**{item['issue']}**"):
                    st.markdown(f"**Evidence:** _{item['evidence']}_")
                    st.markdown(f"**Recommendation:** {item['recommendation']}")
        
        # Key Moments
        st.subheader("⚡ Key Moments")
        for moment in analysis['key_moments']:
            impact_color = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}
            st.markdown(f"""
            <div class="insight-box">
                <strong>{impact_color.get(moment['impact'], '⚪')} {moment['timestamp_approx'].title()}</strong><br>
                {moment['description']}<br>
                <em>💡 {moment['coaching_note']}</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Cognitive Load
        st.subheader("🧠 Cognitive Load Assessment")
        cog = analysis['cognitive_load_assessment']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cognitive Load Score", f"{cog['score']}/100")
        col2.metric("Jargon Density", cog['jargon_density'].title())
        col3.metric("Sentence Complexity", cog['sentence_complexity'].title())
        col4.metric("Topic Switching", cog['topic_switching'].title())
        st.markdown(f"**Recommendation:** {cog['recommendation']}")
        
        # The ONE Thing
        st.subheader("🎯 The ONE Thing to Change")
        st.warning(analysis['one_thing_to_change'])
        
        # Transcript (collapsible)
        with st.expander("📝 View Full Transcript"):
            st.text(st.session_state['transcript'])
        
        # Download report
        st.divider()
        report_data = {
            "analysis": analysis,
            "meeting_context": st.session_state['meeting_context'],
            "generated_at": datetime.now().isoformat()
        }
        
        st.download_button(
            "📥 Download Full Report (JSON)",
            data=json.dumps(report_data, indent=2),
            file_name=f"commsvision_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
