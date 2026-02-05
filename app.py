from dotenv import load_dotenv
load_dotenv()

import os
import json
import tempfile
from datetime import datetime
from enum import Enum

import streamlit as st
from openai import OpenAI


# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CoMentor | AI Communication Coach for Executives",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ══════════════════════════════════════════════════════════════════════════════
# Subscription Plans
# ══════════════════════════════════════════════════════════════════════════════
class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


PLANS = {
    SubscriptionTier.FREE: {
        "name": "Starter",
        "price": 0,
        "price_display": "Free",
        "analyses_per_month": 3,
        "max_audio_minutes": 5,
        "features": [
            "3 analyses per month",
            "Up to 5 min recordings",
            "Communication Effectiveness Score",
            "Basic strengths & improvements",
            "Email support",
        ],
        "cta": "Get Started Free",
        "popular": False,
    },
    SubscriptionTier.PRO: {
        "name": "Professional",
        "price": 29,
        "price_display": "$29/mo",
        "analyses_per_month": 50,
        "max_audio_minutes": 30,
        "features": [
            "50 analyses per month",
            "Up to 30 min recordings",
            "Full diagnostic report",
            "Cognitive load analysis",
            "Key moments detection",
            "Progress tracking dashboard",
            "Priority support",
        ],
        "cta": "Start Pro Trial",
        "popular": True,
    },
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise",
        "price": 99,
        "price_display": "$99/mo",
        "analyses_per_month": -1,  # Unlimited
        "max_audio_minutes": 120,
        "features": [
            "Unlimited analyses",
            "Up to 2 hour recordings",
            "Team analytics & benchmarks",
            "Custom coaching frameworks",
            "API access",
            "White-label reports",
            "Dedicated success manager",
            "SSO & security compliance",
        ],
        "cta": "Contact Sales",
        "popular": False,
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# Premium CSS - Editorial/Magazine Aesthetic with Warm Tones
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500&family=Source+Sans+3:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

:root {
    /* Warm, sophisticated palette */
    --ink: #1a1a2e;
    --ink-light: #2d2d44;
    --ink-muted: #4a4a68;
    --cream: #faf8f5;
    --cream-dark: #f0ede8;
    --paper: #ffffff;
    --accent: #c9a227;
    --accent-dark: #a8871f;
    --accent-light: #f4e9c4;
    --success: #2d8a6e;
    --success-light: #e8f5f0;
    --warning: #d4a017;
    --warning-light: #fef9e8;
    --error: #c44536;
    --error-light: #fceeed;
    
    /* Typography */
    --font-display: 'Playfair Display', Georgia, serif;
    --font-body: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
    
    /* Spacing */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    --space-2xl: 3rem;
    --space-3xl: 4rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(26, 26, 46, 0.06);
    --shadow-md: 0 4px 12px rgba(26, 26, 46, 0.08);
    --shadow-lg: 0 12px 40px rgba(26, 26, 46, 0.12);
    --shadow-xl: 0 24px 60px rgba(26, 26, 46, 0.16);
    
    /* Borders */
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 20px;
    --radius-xl: 28px;
}

/* Base styles */
.stApp {
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--ink);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.block-container {
    max-width: 1280px;
    padding: 0 var(--space-lg);
}

/* ═══════════════════════════════════════════════════════════════════════════
   NAVIGATION
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-nav {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(250, 248, 245, 0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(26, 26, 46, 0.06);
    padding: var(--space-md) var(--space-xl);
    margin: 0 calc(-1 * var(--space-lg)) var(--space-xl);
}

.cm-nav-inner {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.cm-logo {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}

.cm-logo-mark {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(201, 162, 39, 0.3);
}

.cm-logo-text {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.02em;
}

.cm-nav-links {
    display: flex;
    align-items: center;
    gap: var(--space-xl);
}

.cm-nav-link {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--ink-muted);
    text-decoration: none;
    transition: color 0.2s;
}

.cm-nav-link:hover {
    color: var(--ink);
}

.cm-nav-cta {
    background: var(--ink);
    color: white;
    padding: var(--space-sm) var(--space-lg);
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.9rem;
    text-decoration: none;
    transition: all 0.2s;
    box-shadow: var(--shadow-sm);
}

.cm-nav-cta:hover {
    background: var(--ink-light);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* ═══════════════════════════════════════════════════════════════════════════
   HERO SECTION
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-hero {
    text-align: center;
    padding: var(--space-3xl) var(--space-lg);
    position: relative;
    overflow: hidden;
}

.cm-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(201, 162, 39, 0.08) 0%, transparent 60%);
    animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.1); opacity: 1; }
}

.cm-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    background: var(--accent-light);
    color: var(--accent-dark);
    padding: var(--space-sm) var(--space-md);
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: var(--space-lg);
    position: relative;
}

.cm-hero-badge::before {
    content: '✦';
    font-size: 0.75rem;
}

.cm-hero h1 {
    font-family: var(--font-display);
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.03em;
    color: var(--ink);
    margin: 0 auto var(--space-lg);
    max-width: 900px;
    position: relative;
}

.cm-hero h1 em {
    font-style: italic;
    color: var(--accent-dark);
}

.cm-hero-sub {
    font-size: 1.25rem;
    line-height: 1.7;
    color: var(--ink-muted);
    max-width: 640px;
    margin: 0 auto var(--space-xl);
    position: relative;
}

.cm-hero-cta {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-md);
    flex-wrap: wrap;
    position: relative;
}

.cm-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-md) var(--space-xl);
    border-radius: var(--radius-md);
    font-weight: 700;
    font-size: 1rem;
    text-decoration: none;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: none;
}

.cm-btn-primary {
    background: linear-gradient(135deg, var(--ink) 0%, var(--ink-light) 100%);
    color: white;
    box-shadow: var(--shadow-lg), 0 0 0 0 rgba(26, 26, 46, 0.2);
}

.cm-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl), 0 0 0 4px rgba(26, 26, 46, 0.1);
}

.cm-btn-secondary {
    background: var(--paper);
    color: var(--ink);
    border: 2px solid var(--ink);
}

.cm-btn-secondary:hover {
    background: var(--ink);
    color: white;
}

.cm-hero-proof {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-lg);
    margin-top: var(--space-2xl);
    padding-top: var(--space-xl);
    border-top: 1px solid rgba(26, 26, 46, 0.08);
    position: relative;
}

.cm-proof-item {
    text-align: center;
}

.cm-proof-number {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
    color: var(--ink);
}

.cm-proof-label {
    font-size: 0.85rem;
    color: var(--ink-muted);
    font-weight: 500;
}

/* ═══════════════════════════════════════════════════════════════════════════
   DEMO SECTION
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-demo-section {
    background: var(--paper);
    border-radius: var(--radius-xl);
    padding: var(--space-2xl);
    margin: var(--space-2xl) 0;
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-section-header {
    text-align: center;
    margin-bottom: var(--space-2xl);
}

.cm-section-header h2 {
    font-family: var(--font-display);
    font-size: 2.25rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 var(--space-sm);
    letter-spacing: -0.02em;
}

.cm-section-header p {
    color: var(--ink-muted);
    font-size: 1.1rem;
    margin: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FEATURES GRID
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-lg);
    margin: var(--space-2xl) 0;
}

@media (max-width: 900px) {
    .cm-features { grid-template-columns: 1fr; }
}

.cm-feature {
    background: var(--paper);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    border: 1px solid rgba(26, 26, 46, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.cm-feature:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: rgba(201, 162, 39, 0.2);
}

.cm-feature-icon {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, var(--accent-light) 0%, rgba(201, 162, 39, 0.15) 100%);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: var(--space-md);
}

.cm-feature h3 {
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 var(--space-sm);
}

.cm-feature p {
    color: var(--ink-muted);
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PRICING SECTION
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-pricing {
    padding: var(--space-3xl) 0;
}

.cm-pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-lg);
    align-items: start;
}

@media (max-width: 900px) {
    .cm-pricing-grid { grid-template-columns: 1fr; }
}

.cm-plan {
    background: var(--paper);
    border-radius: var(--radius-xl);
    padding: var(--space-xl);
    border: 2px solid rgba(26, 26, 46, 0.06);
    transition: all 0.3s;
    position: relative;
}

.cm-plan:hover {
    border-color: rgba(201, 162, 39, 0.3);
}

.cm-plan.popular {
    border-color: var(--accent);
    box-shadow: var(--shadow-xl), 0 0 0 4px rgba(201, 162, 39, 0.1);
    transform: scale(1.02);
}

.cm-plan-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    color: white;
    padding: var(--space-xs) var(--space-md);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.cm-plan-name {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 var(--space-xs);
}

.cm-plan-price {
    display: flex;
    align-items: baseline;
    gap: var(--space-xs);
    margin-bottom: var(--space-lg);
}

.cm-plan-amount {
    font-family: var(--font-display);
    font-size: 3rem;
    font-weight: 700;
    color: var(--ink);
}

.cm-plan-period {
    color: var(--ink-muted);
    font-size: 0.95rem;
}

.cm-plan-features {
    list-style: none;
    padding: 0;
    margin: 0 0 var(--space-xl);
}

.cm-plan-features li {
    display: flex;
    align-items: flex-start;
    gap: var(--space-sm);
    padding: var(--space-sm) 0;
    font-size: 0.95rem;
    color: var(--ink-muted);
    border-bottom: 1px solid rgba(26, 26, 46, 0.04);
}

.cm-plan-features li:last-child {
    border-bottom: none;
}

.cm-plan-features li::before {
    content: '✓';
    color: var(--success);
    font-weight: 700;
    flex-shrink: 0;
}

.cm-plan-cta {
    width: 100%;
    padding: var(--space-md);
    border-radius: var(--radius-md);
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.25s;
    border: 2px solid transparent;
}

.cm-plan-cta-primary {
    background: var(--ink);
    color: white;
}

.cm-plan-cta-primary:hover {
    background: var(--ink-light);
}

.cm-plan-cta-secondary {
    background: transparent;
    color: var(--ink);
    border-color: var(--ink);
}

.cm-plan-cta-secondary:hover {
    background: var(--ink);
    color: white;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HOW IT WORKS
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-steps {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-xl);
    margin: var(--space-2xl) 0;
    position: relative;
}

@media (max-width: 900px) {
    .cm-steps { grid-template-columns: 1fr; }
}

.cm-step {
    text-align: center;
    position: relative;
}

.cm-step-number {
    width: 64px;
    height: 64px;
    background: var(--accent-light);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-dark);
    margin: 0 auto var(--space-md);
    border: 3px solid var(--accent);
}

.cm-step h3 {
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 var(--space-sm);
}

.cm-step p {
    color: var(--ink-muted);
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   TESTIMONIALS
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-testimonials {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-lg);
    margin: var(--space-2xl) 0;
}

@media (max-width: 900px) {
    .cm-testimonials { grid-template-columns: 1fr; }
}

.cm-testimonial {
    background: var(--paper);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    border: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-testimonial-quote {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-style: italic;
    line-height: 1.7;
    color: var(--ink);
    margin: 0 0 var(--space-lg);
}

.cm-testimonial-author {
    display: flex;
    align-items: center;
    gap: var(--space-md);
}

.cm-testimonial-avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
}

.cm-testimonial-name {
    font-weight: 700;
    color: var(--ink);
    margin: 0;
}

.cm-testimonial-role {
    font-size: 0.85rem;
    color: var(--ink-muted);
    margin: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CTA SECTION
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-cta-section {
    background: linear-gradient(135deg, var(--ink) 0%, var(--ink-light) 100%);
    border-radius: var(--radius-xl);
    padding: var(--space-3xl);
    text-align: center;
    margin: var(--space-2xl) 0;
    position: relative;
    overflow: hidden;
}

.cm-cta-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.cm-cta-section h2 {
    font-family: var(--font-display);
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    margin: 0 0 var(--space-md);
    position: relative;
}

.cm-cta-section p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.15rem;
    margin: 0 0 var(--space-xl);
    position: relative;
}

.cm-cta-section .cm-btn {
    position: relative;
}

.cm-btn-light {
    background: white;
    color: var(--ink);
}

.cm-btn-light:hover {
    background: var(--cream);
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
}

/* ═══════════════════════════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-footer {
    padding: var(--space-2xl) 0;
    border-top: 1px solid rgba(26, 26, 46, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-lg);
}

.cm-footer-links {
    display: flex;
    gap: var(--space-xl);
}

.cm-footer-link {
    color: var(--ink-muted);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s;
}

.cm-footer-link:hover {
    color: var(--ink);
}

.cm-footer-copy {
    color: var(--ink-muted);
    font-size: 0.85rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   ANALYSIS TOOL STYLES
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-tool-card {
    background: var(--paper);
    border-radius: var(--radius-xl);
    padding: var(--space-2xl);
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-tool-header {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    margin-bottom: var(--space-xl);
    padding-bottom: var(--space-lg);
    border-bottom: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-tool-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent-light) 0%, rgba(201, 162, 39, 0.2) 100%);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.cm-tool-title {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
}

.cm-tool-subtitle {
    color: var(--ink-muted);
    font-size: 0.9rem;
    margin: 0;
}

/* Override Streamlit components */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--space-sm);
    background: transparent;
    padding: 0;
    border-bottom: 2px solid rgba(26, 26, 46, 0.06);
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    padding: var(--space-md) var(--space-lg);
    font-weight: 700;
    color: var(--ink-muted);
    background: transparent;
    border: none;
}

.stTabs [aria-selected="true"] {
    background: var(--paper);
    color: var(--ink);
    border-bottom: 2px solid var(--accent);
}

/* Streamlit buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--ink) 0%, var(--ink-light) 100%) !important;
    color: white !important;
    border: none !important;
    padding: var(--space-md) var(--space-xl) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-md) !important;
    transition: all 0.25s !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(26, 26, 46, 0.15);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    background: var(--cream);
    transition: all 0.2s;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent);
    background: var(--accent-light);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--paper);
    border-right: 1px solid rgba(26, 26, 46, 0.06);
}

/* ═══════════════════════════════════════════════════════════════════════════
   REPORT STYLES
   ═══════════════════════════════════════════════════════════════════════════ */
.cm-score-hero {
    background: linear-gradient(135deg, var(--success) 0%, #1d6b54 100%);
    color: white;
    padding: var(--space-2xl);
    border-radius: var(--radius-xl);
    text-align: center;
    box-shadow: var(--shadow-lg);
    margin-bottom: var(--space-xl);
}

.cm-score-label {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.9;
}

.cm-score-value {
    font-family: var(--font-display);
    font-size: 5rem;
    font-weight: 700;
    line-height: 1;
    margin: var(--space-sm) 0;
}

.cm-score-verdict {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    padding: var(--space-xs) var(--space-md);
    border-radius: 999px;
    font-weight: 700;
}

.cm-report-section {
    background: var(--paper);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    margin-bottom: var(--space-lg);
    border: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-report-section-header {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    margin-bottom: var(--space-lg);
}

.cm-report-section-icon {
    width: 36px;
    height: 36px;
    background: var(--accent-light);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
}

.cm-report-section-title {
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
}

.cm-insight-card {
    display: flex;
    gap: var(--space-md);
    padding: var(--space-md);
    background: var(--cream);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-sm);
    border-left: 4px solid var(--success);
}

.cm-insight-card.improve {
    border-left-color: var(--warning);
}

.cm-insight-card.moment {
    border-left-color: var(--accent);
}

.cm-insight-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.cm-insight-icon.strength {
    background: var(--success-light);
    color: var(--success);
}

.cm-insight-icon.improve {
    background: var(--warning-light);
    color: var(--warning);
}

.cm-insight-icon.moment {
    background: var(--accent-light);
    color: var(--accent-dark);
}

.cm-insight-title {
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 var(--space-xs);
}

.cm-insight-text {
    font-size: 0.9rem;
    color: var(--ink-muted);
    line-height: 1.5;
    margin: 0;
}

.cm-subscore-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: var(--space-md);
}

@media (max-width: 900px) {
    .cm-subscore-grid { grid-template-columns: repeat(2, 1fr); }
}

.cm-subscore {
    text-align: center;
    padding: var(--space-md);
    background: var(--cream);
    border-radius: var(--radius-md);
}

.cm-subscore-value {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
}

.cm-subscore-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--ink-muted);
    margin-top: var(--space-xs);
}

.cm-subscore-bar {
    height: 6px;
    background: rgba(26, 26, 46, 0.1);
    border-radius: 999px;
    margin-top: var(--space-sm);
    overflow: hidden;
}

.cm-subscore-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 1s ease;
}

.cm-cog-meter {
    background: var(--cream);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
}

.cm-cog-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-sm) 0;
    border-bottom: 1px solid rgba(26, 26, 46, 0.06);
}

.cm-cog-row:last-child {
    border-bottom: none;
}

.cm-cog-label {
    font-size: 0.9rem;
    color: var(--ink-muted);
}

.cm-cog-badge {
    padding: var(--space-xs) var(--space-sm);
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
}

.cm-cog-low {
    background: var(--success-light);
    color: var(--success);
}

.cm-cog-medium {
    background: var(--warning-light);
    color: var(--warning);
}

.cm-cog-high {
    background: var(--error-light);
    color: var(--error);
}

.cm-one-thing {
    background: linear-gradient(135deg, var(--accent-light) 0%, rgba(201, 162, 39, 0.1) 100%);
    border: 2px solid var(--accent);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
}

.cm-one-thing-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent-dark);
    margin-bottom: var(--space-sm);
}

.cm-one-thing-text {
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--ink);
    line-height: 1.5;
    margin: 0;
}

.cm-exec-summary {
    background: var(--cream);
    border-left: 4px solid var(--accent);
    padding: var(--space-lg);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--ink-muted);
}

.cm-transcript-box {
    background: var(--cream);
    border: 1px solid rgba(26, 26, 46, 0.08);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    font-size: 0.875rem;
    line-height: 1.8;
    color: var(--ink-muted);
    max-height: 400px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# OpenAI Client
# ══════════════════════════════════════════════════════════════════════════════
def init_openai_client() -> OpenAI | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    
    if not api_key:
        api_key = st.session_state.get("openai_api_key")
    
    if not api_key or len(str(api_key).strip()) < 10:
        return None
    
    return OpenAI(api_key=str(api_key).strip())


# ══════════════════════════════════════════════════════════════════════════════
# AI Functions
# ══════════════════════════════════════════════════════════════════════════════
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
            {"role": "system", "content": "You are an elite executive communication analyst. Respond only with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2500,
    )

    text = resp.choices[0].message.content.strip()
    
    if text.startswith("```"):
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p and p.startswith("{"):
                text = p
                break

    return json.loads(text)


# ══════════════════════════════════════════════════════════════════════════════
# UI Components
# ══════════════════════════════════════════════════════════════════════════════
def render_navigation():
    st.markdown("""
<div class="cm-nav">
    <div class="cm-nav-inner">
        <div class="cm-logo">
            <div class="cm-logo-mark">◐</div>
            <span class="cm-logo-text">CoMentor</span>
        </div>
        <div class="cm-nav-links">
            <a href="#features" class="cm-nav-link">Features</a>
            <a href="#pricing" class="cm-nav-link">Pricing</a>
            <a href="#how-it-works" class="cm-nav-link">How It Works</a>
            <a href="#" class="cm-nav-cta">Get Started</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_hero():
    st.markdown("""
<div class="cm-hero">
    <div class="cm-hero-badge">Now in Public Beta</div>
    <h1>Speak with <em>clarity</em>.<br>Lead with <em>presence</em>.</h1>
    <p class="cm-hero-sub">
        CoMentor is your AI communication coach. Analyze meetings, presentations, and pitches 
        to eliminate weak language, build executive presence, and communicate with impact.
    </p>
    <div class="cm-hero-cta">
        <a href="#demo" class="cm-btn cm-btn-primary">Try Free Demo →</a>
        <a href="#pricing" class="cm-btn cm-btn-secondary">View Pricing</a>
    </div>
    <div class="cm-hero-proof">
        <div class="cm-proof-item">
            <div class="cm-proof-number">500+</div>
            <div class="cm-proof-label">Executives coached</div>
        </div>
        <div class="cm-proof-item">
            <div class="cm-proof-number">23%</div>
            <div class="cm-proof-label">Avg. score improvement</div>
        </div>
        <div class="cm-proof-item">
            <div class="cm-proof-number">4.9★</div>
            <div class="cm-proof-label">User rating</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_features():
    st.markdown("""
<div id="features">
    <div class="cm-section-header">
        <h2>Built for leaders who mean business</h2>
        <p>Every metric designed to help you command attention and drive action</p>
    </div>
</div>
<div class="cm-features">
    <div class="cm-feature">
        <div class="cm-feature-icon">📊</div>
        <h3>Communication Effectiveness Score</h3>
        <p>Your single source of truth. A composite metric that tells you exactly how impactful your communication is—and where to improve.</p>
    </div>
    <div class="cm-feature">
        <div class="cm-feature-icon">🧠</div>
        <h3>Cognitive Load Analysis</h3>
        <p>Ensure your message lands. We measure jargon density, sentence complexity, and topic switching to optimize retention.</p>
    </div>
    <div class="cm-feature">
        <div class="cm-feature-icon">👑</div>
        <h3>Authority & Presence</h3>
        <p>Command the room. Track linguistic patterns that signal confidence, expertise, and leadership to your audience.</p>
    </div>
    <div class="cm-feature">
        <div class="cm-feature-icon">🎯</div>
        <h3>Filler Word Detection</h3>
        <p>Eliminate the "ums," "likes," and hedge words that undermine your credibility and dilute your message.</p>
    </div>
    <div class="cm-feature">
        <div class="cm-feature-icon">⚡</div>
        <h3>Key Moments Detection</h3>
        <p>Pinpoint the exact moments that made or broke your communication—with specific coaching for each.</p>
    </div>
    <div class="cm-feature">
        <div class="cm-feature-icon">📈</div>
        <h3>Progress Tracking</h3>
        <p>Watch yourself improve over time. See trends, celebrate wins, and stay motivated on your leadership journey.</p>
    </div>
</div>
""", unsafe_allow_html=True)


def render_pricing():
    st.markdown("""
<div class="cm-pricing" id="pricing">
    <div class="cm-section-header">
        <h2>Simple, transparent pricing</h2>
        <p>Start free, upgrade when you're ready to accelerate</p>
    </div>
    <div class="cm-pricing-grid">
        <div class="cm-plan">
            <h3 class="cm-plan-name">Starter</h3>
            <div class="cm-plan-price">
                <span class="cm-plan-amount">$0</span>
                <span class="cm-plan-period">/month</span>
            </div>
            <ul class="cm-plan-features">
                <li>3 analyses per month</li>
                <li>Up to 5 min recordings</li>
                <li>Communication Effectiveness Score</li>
                <li>Basic strengths & improvements</li>
                <li>Email support</li>
            </ul>
            <button class="cm-plan-cta cm-plan-cta-secondary">Get Started Free</button>
        </div>
        <div class="cm-plan popular">
            <div class="cm-plan-badge">Most Popular</div>
            <h3 class="cm-plan-name">Professional</h3>
            <div class="cm-plan-price">
                <span class="cm-plan-amount">$29</span>
                <span class="cm-plan-period">/month</span>
            </div>
            <ul class="cm-plan-features">
                <li>50 analyses per month</li>
                <li>Up to 30 min recordings</li>
                <li>Full diagnostic report</li>
                <li>Cognitive load analysis</li>
                <li>Key moments detection</li>
                <li>Progress tracking dashboard</li>
                <li>Priority support</li>
            </ul>
            <button class="cm-plan-cta cm-plan-cta-primary">Start Pro Trial</button>
        </div>
        <div class="cm-plan">
            <h3 class="cm-plan-name">Enterprise</h3>
            <div class="cm-plan-price">
                <span class="cm-plan-amount">$99</span>
                <span class="cm-plan-period">/month</span>
            </div>
            <ul class="cm-plan-features">
                <li>Unlimited analyses</li>
                <li>Up to 2 hour recordings</li>
                <li>Team analytics & benchmarks</li>
                <li>Custom coaching frameworks</li>
                <li>API access</li>
                <li>White-label reports</li>
                <li>Dedicated success manager</li>
                <li>SSO & security compliance</li>
            </ul>
            <button class="cm-plan-cta cm-plan-cta-secondary">Contact Sales</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_how_it_works():
    st.markdown("""
<div id="how-it-works">
    <div class="cm-section-header">
        <h2>Three steps to executive presence</h2>
        <p>Start improving your communication in under 5 minutes</p>
    </div>
</div>
<div class="cm-steps">
    <div class="cm-step">
        <div class="cm-step-number">1</div>
        <h3>Record or Upload</h3>
        <p>Capture your meeting, presentation, or pitch. Record directly in your browser or upload an existing file.</p>
    </div>
    <div class="cm-step">
        <div class="cm-step-number">2</div>
        <h3>Get Your Analysis</h3>
        <p>Our AI analyzes your speech patterns, word choice, pacing, and presence markers in seconds.</p>
    </div>
    <div class="cm-step">
        <div class="cm-step-number">3</div>
        <h3>Improve & Track</h3>
        <p>Receive personalized recommendations and watch your executive presence grow with each session.</p>
    </div>
</div>
""", unsafe_allow_html=True)


def render_testimonials():
    st.markdown("""
<div class="cm-section-header">
    <h2>Trusted by leaders everywhere</h2>
    <p>See what executives are saying about CoMentor</p>
</div>
<div class="cm-testimonials">
    <div class="cm-testimonial">
        <p class="cm-testimonial-quote">"I used to say 'basically' and 'you know' constantly. After two weeks with CoMentor, my board noticed the difference. My CES went from 62 to 84."</p>
        <div class="cm-testimonial-author">
            <div class="cm-testimonial-avatar">JD</div>
            <div>
                <p class="cm-testimonial-name">James Davidson</p>
                <p class="cm-testimonial-role">CEO, TechFlow Inc.</p>
            </div>
        </div>
    </div>
    <div class="cm-testimonial">
        <p class="cm-testimonial-quote">"As a non-native speaker, I was always nervous about presenting. CoMentor gave me the confidence and clarity to pitch to investors successfully."</p>
        <div class="cm-testimonial-author">
            <div class="cm-testimonial-avatar">SK</div>
            <div>
                <p class="cm-testimonial-name">Sofia Kowalski</p>
                <p class="cm-testimonial-role">Founder, GreenPath</p>
            </div>
        </div>
    </div>
    <div class="cm-testimonial">
        <p class="cm-testimonial-quote">"I've done executive coaching for years. CoMentor is like having a communication coach in my pocket—available whenever I need feedback."</p>
        <div class="cm-testimonial-author">
            <div class="cm-testimonial-avatar">ML</div>
            <div>
                <p class="cm-testimonial-name">Michael Lin</p>
                <p class="cm-testimonial-role">VP Sales, Orbit Systems</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_cta():
    st.markdown("""
<div class="cm-cta-section">
    <h2>Ready to speak with impact?</h2>
    <p>Join 500+ executives who are transforming their communication. Start free, no credit card required.</p>
    <a href="#demo" class="cm-btn cm-btn-light">Get Started Free →</a>
</div>
""", unsafe_allow_html=True)


def render_footer():
    st.markdown("""
<div class="cm-footer">
    <div class="cm-logo">
        <div class="cm-logo-mark">◐</div>
        <span class="cm-logo-text">CoMentor</span>
    </div>
    <div class="cm-footer-links">
        <a href="#" class="cm-footer-link">Privacy</a>
        <a href="#" class="cm-footer-link">Terms</a>
        <a href="#" class="cm-footer-link">Contact</a>
        <a href="#" class="cm-footer-link">Blog</a>
    </div>
    <div class="cm-footer-copy">© 2025 CoMentor. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)


def get_score_color(score: int) -> str:
    if score >= 80:
        return "#2d8a6e"
    if score >= 60:
        return "#3da37f"
    if score >= 40:
        return "#d4a017"
    return "#c44536"


def render_report(analysis: dict, transcript_text: str):
    score = analysis["communication_effectiveness_score"]
    verdict = analysis.get("score_verdict", "Competent")

    # Score hero
    st.markdown(f"""
<div class="cm-score-hero">
    <div class="cm-score-label">Communication Effectiveness Score</div>
    <div class="cm-score-value">{score}</div>
    <div class="cm-score-verdict">{verdict}</div>
</div>
""", unsafe_allow_html=True)

    # Executive summary
    st.markdown(f"""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">📋</div>
        <h3 class="cm-report-section-title">Executive Summary</h3>
    </div>
    <div class="cm-exec-summary">{analysis["executive_summary"]}</div>
</div>
""", unsafe_allow_html=True)

    # Sub-scores
    sub = analysis["sub_scores"]
    labels = [
        ("clarity", "Clarity"),
        ("authority", "Authority"),
        ("audience_adaptation", "Audience Fit"),
        ("persuasion", "Persuasion"),
        ("emotional_regulation", "Composure"),
    ]
    
    st.markdown("""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">📊</div>
        <h3 class="cm-report-section-title">Performance Breakdown</h3>
    </div>
    <div class="cm-subscore-grid">
""", unsafe_allow_html=True)
    
    for key, label in labels:
        val = sub[key]
        color = get_score_color(val)
        st.markdown(f"""
        <div class="cm-subscore">
            <div class="cm-subscore-value" style="color: {color};">{val}</div>
            <div class="cm-subscore-label">{label}</div>
            <div class="cm-subscore-bar">
                <div class="cm-subscore-fill" style="width: {val}%; background: {color};"></div>
            </div>
        </div>
""", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Strengths and improvements
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">💪</div>
        <h3 class="cm-report-section-title">Strengths</h3>
    </div>
""", unsafe_allow_html=True)
        for s in analysis["strengths"]:
            st.markdown(f"""
    <div class="cm-insight-card">
        <div class="cm-insight-icon strength">✓</div>
        <div>
            <p class="cm-insight-title">{s["title"]}</p>
            <p class="cm-insight-text">{s["detail"]}</p>
        </div>
    </div>
""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">🎯</div>
        <h3 class="cm-report-section-title">Areas to Improve</h3>
    </div>
""", unsafe_allow_html=True)
        for imp in analysis["improvements"]:
            st.markdown(f"""
    <div class="cm-insight-card improve">
        <div class="cm-insight-icon improve">↑</div>
        <div>
            <p class="cm-insight-title">{imp["title"]}</p>
            <p class="cm-insight-text">{imp["detail"]}</p>
        </div>
    </div>
""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Key moments
    st.markdown("""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">⚡</div>
        <h3 class="cm-report-section-title">Key Moments</h3>
    </div>
""", unsafe_allow_html=True)
    
    for moment in analysis["key_moments"]:
        st.markdown(f"""
    <div class="cm-insight-card moment">
        <div class="cm-insight-icon moment">•</div>
        <div>
            <p class="cm-insight-title">{moment["timestamp"].title()}: {moment["title"]}</p>
            <p class="cm-insight-text">{moment["insight"]}</p>
        </div>
    </div>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Cognitive load
    cog = analysis["cognitive_load"]
    
    def cog_class(level: str) -> str:
        return {"low": "cm-cog-low", "medium": "cm-cog-medium", "high": "cm-cog-high"}.get(level.lower(), "cm-cog-medium")

    st.markdown(f"""
<div class="cm-report-section">
    <div class="cm-report-section-header">
        <div class="cm-report-section-icon">🧠</div>
        <h3 class="cm-report-section-title">Cognitive Load Analysis</h3>
    </div>
    <div class="cm-cog-meter">
        <div class="cm-cog-row">
            <span class="cm-cog-label">Overall Cognitive Load</span>
            <span class="cm-cog-badge {cog_class(cog["overall"])}">{cog["overall"].title()}</span>
        </div>
        <div class="cm-cog-row">
            <span class="cm-cog-label">Jargon Density</span>
            <span class="cm-cog-badge {cog_class(cog["jargon"])}">{cog["jargon"].title()}</span>
        </div>
        <div class="cm-cog-row">
            <span class="cm-cog-label">Sentence Complexity</span>
            <span class="cm-cog-badge {cog_class(cog["complexity"])}">{cog["complexity"].title()}</span>
        </div>
        <div class="cm-cog-row">
            <span class="cm-cog-label">Topic Switching</span>
            <span class="cm-cog-badge {cog_class(cog["topic_switches"])}">{cog["topic_switches"].title()}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # One thing
    st.markdown(f"""
<div class="cm-one-thing">
    <div class="cm-one-thing-label">🎯 Your One Thing to Change</div>
    <p class="cm-one-thing-text">{analysis["one_thing"]}</p>
</div>
""", unsafe_allow_html=True)

    # Transcript
    with st.expander("📝 View Full Transcript"):
        st.markdown(f'<div class="cm-transcript-box">{transcript_text}</div>', unsafe_allow_html=True)

    # Download
    st.markdown("<br>", unsafe_allow_html=True)
    report_data = {
        "analysis": analysis,
        "transcript": transcript_text,
        "generated_at": datetime.now().isoformat(),
    }
    st.download_button(
        "📥 Download Report (JSON)",
        data=json.dumps(report_data, indent=2),
        file_name=f"comentor_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
    )


# ══════════════════════════════════════════════════════════════════════════════
# Main App
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # Initialize session state
    if "current_plan" not in st.session_state:
        st.session_state.current_plan = SubscriptionTier.FREE
    if "analyses_used" not in st.session_state:
        st.session_state.analyses_used = 0

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key
        env_has_key = bool(os.environ.get("OPENAI_API_KEY"))
        try:
            env_has_key = env_has_key or ("OPENAI_API_KEY" in st.secrets)
        except Exception:
            pass

        if not env_has_key:
            st.text_input(
                "OpenAI API Key",
                type="password",
                help="Your API key is not stored.",
                key="openai_api_key",
            )
        else:
            st.success("✓ API key configured")

        st.markdown("---")
        st.markdown("### 📋 Meeting Context")
        
        meeting_type = st.selectbox("Meeting Type", [
            "Board presentation", "Investor pitch", "Sales call",
            "Team update", "Negotiation", "Client meeting", "Media interview", "Other"
        ])
        
        objective = st.selectbox("Primary Objective", [
            "Persuade / influence", "Inform / update", "Decide / align",
            "Build relationship", "Negotiate terms", "Defend position"
        ])
        
        audience = st.selectbox("Audience", [
            "C-suite / board", "Investors", "Senior leadership",
            "Clients", "Direct reports", "External stakeholders", "Media / public"
        ])
        
        speaker_role = st.text_input("Your Role", placeholder="e.g., CEO, Founder")

        st.markdown("---")
        plan = PLANS[st.session_state.current_plan]
        st.markdown(f"**Current Plan:** {plan['name']}")
        if plan['analyses_per_month'] > 0:
            st.markdown(f"**Analyses Used:** {st.session_state.analyses_used}/{plan['analyses_per_month']}")

    # Main content
    render_navigation()
    render_hero()
    render_features()
    render_how_it_works()
    
    # Demo section
    st.markdown('<div id="demo">', unsafe_allow_html=True)
    st.markdown("""
<div class="cm-section-header">
    <h2>Try it now</h2>
    <p>Upload a recording or record yourself to see CoMentor in action</p>
</div>
""", unsafe_allow_html=True)

    client = init_openai_client()
    
    if not client:
        st.warning("🔐 Add your OpenAI API key in the sidebar to start analyzing.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Check if showing results
        if st.session_state.get("show_results") and "analysis" in st.session_state:
            render_report(st.session_state["analysis"], st.session_state.get("transcript", ""))
            if st.button("← Analyze Another", use_container_width=True):
                st.session_state["show_results"] = False
                st.session_state.pop("analysis", None)
                st.session_state.pop("transcript", None)
                st.rerun()
        else:
            # Upload/Record tabs
            tab_upload, tab_record = st.tabs(["📁 Upload Recording", "🎙️ Record Now"])
            
            meeting_context = {
                "meeting_type": meeting_type,
                "objective": objective,
                "audience": audience,
                "speaker_role": speaker_role or "Executive",
            }

            with tab_upload:
                st.markdown("""
<div class="cm-tool-card">
    <div class="cm-tool-header">
        <div class="cm-tool-icon">📁</div>
        <div>
            <h3 class="cm-tool-title">Upload a Recording</h3>
            <p class="cm-tool-subtitle">MP3, MP4, WAV, M4A, WebM, OGG • Max 30 min for Pro</p>
        </div>
    </div>
""", unsafe_allow_html=True)
                
                uploaded = st.file_uploader(
                    "Drop your file here",
                    type=["mp3", "mp4", "wav", "m4a", "webm", "ogg"],
                    label_visibility="collapsed"
                )
                
                if uploaded:
                    st.audio(uploaded)
                    if st.button("✨ Analyze Communication", key="analyze_upload", use_container_width=True):
                        with st.status("Analyzing...", expanded=True) as status:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
                                tmp.write(uploaded.getvalue())
                                tmp_path = tmp.name
                            
                            try:
                                status.write("🎙️ Transcribing with Whisper...")
                                transcript = transcribe_audio(client, tmp_path)
                                
                                status.write("🧠 Running communication analysis...")
                                analysis = analyze_communication(client, transcript.text, meeting_context)
                                
                                st.session_state["analysis"] = analysis
                                st.session_state["transcript"] = transcript.text
                                st.session_state["show_results"] = True
                                st.session_state.analyses_used += 1
                                
                                status.update(label="✓ Analysis complete!", state="complete")
                                st.rerun()
                            except Exception as e:
                                status.update(label="Analysis failed", state="error")
                                st.error(f"Error: {e}")
                            finally:
                                os.unlink(tmp_path)
                
                st.markdown("</div>", unsafe_allow_html=True)

            with tab_record:
                st.markdown("""
<div class="cm-tool-card">
    <div class="cm-tool-header">
        <div class="cm-tool-icon">🎙️</div>
        <div>
            <h3 class="cm-tool-title">Record Now</h3>
            <p class="cm-tool-subtitle">Record directly in your browser</p>
        </div>
    </div>
""", unsafe_allow_html=True)
                
                try:
                    audio_value = st.audio_input("Click to record", key="audio_recorder")
                    
                    if audio_value:
                        st.audio(audio_value)
                        if st.button("✨ Analyze Recording", key="analyze_record", use_container_width=True):
                            with st.status("Analyzing...", expanded=True) as status:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                                    tmp.write(audio_value.getvalue())
                                    tmp_path = tmp.name
                                
                                try:
                                    status.write("🎙️ Transcribing...")
                                    transcript = transcribe_audio(client, tmp_path)
                                    
                                    status.write("🧠 Analyzing...")
                                    analysis = analyze_communication(client, transcript.text, meeting_context)
                                    
                                    st.session_state["analysis"] = analysis
                                    st.session_state["transcript"] = transcript.text
                                    st.session_state["show_results"] = True
                                    st.session_state.analyses_used += 1
                                    
                                    status.update(label="✓ Complete!", state="complete")
                                    st.rerun()
                                finally:
                                    os.unlink(tmp_path)
                except Exception:
                    st.info("Recording requires Streamlit 1.33+. Please use the Upload tab.")
                
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    render_pricing()
    render_testimonials()
    render_cta()
    render_footer()


if __name__ == "__main__":
    main()
