
import os
import json
import time
import textwrap
import streamlit as st
from dotenv import load_dotenv
from google import genai

# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()


# =========================================================
# GEMINI API CONFIGURATION
# =========================================================

API_KEY = None

# Try Streamlit Secrets first (used when deployed)
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    API_KEY = None

# Fall back to .env for local development
if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None


# =========================================================
# GEMINI REQUEST WITH RETRY
# =========================================================

def generate_with_retry(prompt, max_retries=3):
    """Send a Gemini request and retry temporary failures."""

    if client is None:
        raise RuntimeError("Gemini API key is not configured.")

    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return response

        except Exception as e:
            last_error = e

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    raise last_error

st.set_page_config(
    page_title="IdeaLens",
    page_icon="💡",
    layout="wide"
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.html(
    """
    <style>
    /* =====================================================
       IDEALENS — PREMIUM 3D / GLASSMORPHIC UI
       ===================================================== */

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(99,102,241,.18), transparent 28%),
            radial-gradient(circle at 85% 18%, rgba(6,182,212,.14), transparent 25%),
            radial-gradient(circle at 55% 85%, rgba(168,85,247,.12), transparent 30%),
            #070912;
        color: #f8fafc;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Soft 3D atmosphere */
    .stApp::before,
    .stApp::after {
        content: "";
        position: fixed;
        width: 320px;
        height: 320px;
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        filter: blur(55px);
        opacity: .28;
        animation: floatOrb 9s ease-in-out infinite;
    }

    .stApp::before {
        top: 8%;
        left: -120px;
        background: #6366f1;
    }

    .stApp::after {
        right: -120px;
        bottom: 8%;
        background: #06b6d4;
        animation-delay: -4s;
    }

    @keyframes floatOrb {
        0%, 100% { transform: translate3d(0,0,0) scale(1); }
        50% { transform: translate3d(35px,-25px,0) scale(1.12); }
    }

    /* Hero */
    .hero-3d {
        position: relative;
        overflow: hidden;
        margin: .5rem 0 2rem 0;
        padding: 3rem 3.2rem;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 30px;
        background:
            linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.025)),
            rgba(9,13,28,.72);
        box-shadow:
            0 35px 90px rgba(0,0,0,.48),
            inset 0 1px 0 rgba(255,255,255,.12);
        backdrop-filter: blur(20px);
        transform: perspective(1200px) rotateX(.8deg);
    }

    .hero-3d::before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -80px;
        top: -100px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(99,102,241,.55), transparent 68%);
        filter: blur(10px);
    }

    .hero-3d::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        left: 45%;
        bottom: -120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(6,182,212,.40), transparent 70%);
        filter: blur(8px);
    }

    .hero-logo {
        font-size: 4.3rem;
        line-height: 1;
        margin-bottom: .7rem;
        filter: drop-shadow(0 12px 25px rgba(99,102,241,.45));
    }

    .hero-title {
        font-size: clamp(2.6rem, 5vw, 4.7rem);
        font-weight: 850;
        letter-spacing: -2px;
        margin: 0;
        background: linear-gradient(90deg, #ffffff, #c4b5fd, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #cbd5e1;
        margin-top: .8rem;
        max-width: 850px;
    }

    .hero-badges {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 1.4rem;
    }

    .hero-badge {
        padding: .55rem .9rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.12);
        background: rgba(255,255,255,.06);
        color: #e2e8f0;
        font-size: .88rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
    }


    /* =====================================================
       TRUE 3D HERO ELEMENTS
       ===================================================== */

    .hero-scene {
        position: absolute;
        right: 4%;
        top: 50%;
        width: 390px;
        height: 300px;
        transform: translateY(-50%);
        perspective: 1000px;
        pointer-events: none;
    }

    .ai-orb {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 150px;
        height: 150px;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        background:
            radial-gradient(circle at 30% 25%, #ffffff 0 4%, #67e8f9 12%, #6366f1 42%, #312e81 72%, #090d1c 100%);
        box-shadow:
            0 0 25px rgba(103,232,249,.70),
            0 0 70px rgba(99,102,241,.55),
            0 35px 80px rgba(0,0,0,.55),
            inset -20px -25px 40px rgba(0,0,0,.42),
            inset 15px 10px 25px rgba(255,255,255,.28);
        animation: orbFloat 5s ease-in-out infinite;
    }

    .ai-orb::before {
        content: "✦";
        position: absolute;
        inset: 0;
        display: grid;
        place-items: center;
        font-size: 4rem;
        color: rgba(255,255,255,.90);
        text-shadow: 0 0 25px rgba(103,232,249,.9);
    }

    .ai-orb::after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        left: -20px;
        top: -20px;
        border-radius: 50%;
        border: 1px solid rgba(103,232,249,.30);
        box-shadow: 0 0 30px rgba(103,232,249,.18);
    }

    .orbit {
        position: absolute;
        left: 50%;
        top: 50%;
        border: 1px solid rgba(103,232,249,.34);
        border-radius: 50%;
        transform-style: preserve-3d;
        animation: orbitSpin 9s linear infinite;
    }

    .orbit.one {
        width: 260px;
        height: 100px;
        transform: translate(-50%, -50%) rotateX(66deg) rotateZ(12deg);
    }

    .orbit.two {
        width: 290px;
        height: 125px;
        transform: translate(-50%, -50%) rotateX(70deg) rotateY(35deg);
        animation-duration: 12s;
        animation-direction: reverse;
    }

    .orbit-dot {
        position: absolute;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #67e8f9;
        box-shadow: 0 0 18px rgba(103,232,249,.9);
        top: 50%;
        left: -6px;
    }

    .floating-chip {
        position: absolute;
        padding: 10px 14px;
        border-radius: 13px;
        border: 1px solid rgba(255,255,255,.14);
        background: rgba(15,23,42,.70);
        color: #e2e8f0;
        font-size: .78rem;
        font-weight: 700;
        backdrop-filter: blur(12px);
        box-shadow: 0 18px 35px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.10);
    }

    .chip-a {
        right: 4px;
        top: 20px;
        transform: rotateY(-12deg) rotateZ(3deg);
        animation: chipFloat 4.5s ease-in-out infinite;
    }

    .chip-b {
        left: 0;
        bottom: 22px;
        transform: rotateY(10deg) rotateZ(-3deg);
        animation: chipFloat 5.5s ease-in-out infinite reverse;
    }

    .chip-c {
        right: 18px;
        bottom: 10px;
        transform: rotateY(-8deg);
        animation: chipFloat 6s ease-in-out infinite;
    }

    @keyframes orbFloat {
        0%, 100% {
            transform: translate(-50%, -50%) translateY(0) rotate(0deg);
        }
        50% {
            transform: translate(-50%, -50%) translateY(-16px) rotate(8deg);
        }
    }

    @keyframes orbitSpin {
        from { transform: translate(-50%, -50%) rotateX(66deg) rotateZ(0deg); }
        to { transform: translate(-50%, -50%) rotateX(66deg) rotateZ(360deg); }
    }

    @keyframes chipFloat {
        0%, 100% { transform: translateY(0) rotateZ(0deg); }
        50% { transform: translateY(-10px) rotateZ(2deg); }
    }

    /* 3D section cards */
    .feature-3d {
        position: relative;
        padding: 22px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,.10);
        background: linear-gradient(145deg, rgba(255,255,255,.075), rgba(255,255,255,.018));
        box-shadow:
            0 18px 35px rgba(0,0,0,.26),
            inset 0 1px 0 rgba(255,255,255,.09);
        transform: perspective(800px) rotateX(1deg);
    }

    /* Keep the hero readable when the 3D object is visible. */
    @media (max-width: 1050px) {
        .hero-scene {
            opacity: .28;
            right: -30px;
        }
    }

    @media (max-width: 760px) {
        .hero-scene {
            display: none;
        }
    }

    /* Section headings */
    h2, h3 {
        letter-spacing: -.5px;
    }

    /* Glass inputs */
    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(17,24,39,.70) !important;
        border: 1px solid rgba(255,255,255,.11) !important;
        border-radius: 16px !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.05),
            0 12px 30px rgba(0,0,0,.18) !important;
    }

    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: rgba(103,232,249,.65) !important;
        box-shadow: 0 0 0 1px rgba(103,232,249,.25), 0 15px 35px rgba(6,182,212,.12) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 15px !important;
        min-height: 48px !important;
        font-weight: 750 !important;
        border: 1px solid rgba(255,255,255,.13) !important;
        background: linear-gradient(135deg, rgba(99,102,241,.95), rgba(6,182,212,.88)) !important;
        color: white !important;
        box-shadow:
            0 12px 28px rgba(79,70,229,.28),
            inset 0 1px 0 rgba(255,255,255,.18) !important;
        transition: all .2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow:
            0 20px 40px rgba(6,182,212,.22),
            inset 0 1px 0 rgba(255,255,255,.20) !important;
    }

    /* 3D score cards */
    .score-card {
        position: relative;
        padding: 24px 18px;
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,.12);
        text-align: center;
        min-height: 145px;
        overflow: hidden;
        background:
            linear-gradient(145deg, rgba(255,255,255,.095), rgba(255,255,255,.025)),
            rgba(10,14,27,.72);
        box-shadow:
            0 20px 35px rgba(0,0,0,.32),
            inset 0 1px 0 rgba(255,255,255,.10);
        backdrop-filter: blur(16px);
        transform: perspective(900px) translateZ(0);
        transition: transform .25s ease, box-shadow .25s ease;
    }

    .score-card::before {
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        top: -35px;
        right: -25px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(103,232,249,.28), transparent 70%);
    }

    .score-card:hover {
        transform: perspective(900px) rotateX(4deg) rotateY(-4deg) translateY(-6px);
        box-shadow:
            0 30px 55px rgba(0,0,0,.42),
            0 0 30px rgba(99,102,241,.12),
            inset 0 1px 0 rgba(255,255,255,.13);
    }

    .score-number {
        font-size: 2.45rem;
        font-weight: 850;
        background: linear-gradient(135deg, #fff, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .score-label {
        font-size: .92rem;
        color: #cbd5e1;
        margin-top: 7px;
    }

    /* Generic glass recommendation cards */
    .recommendation,
    .glass-card {
        padding: 22px;
        border-radius: 22px;
        border: 1px solid rgba(255,255,255,.11);
        margin-bottom: 14px;
        background:
            linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.025)),
            rgba(10,14,27,.72);
        box-shadow:
            0 20px 40px rgba(0,0,0,.30),
            inset 0 1px 0 rgba(255,255,255,.08);
        backdrop-filter: blur(16px);
        transition: transform .2s ease;
    }

    .recommendation:hover,
    .glass-card:hover {
        transform: translateY(-3px);
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,.10) !important;
        border-radius: 18px !important;
        background: rgba(12,17,31,.60) !important;
        box-shadow: 0 15px 35px rgba(0,0,0,.20) !important;
        overflow: hidden;
    }

    /* Metrics / progress */
    div[data-testid="stMetric"] {
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.10);
        background: rgba(255,255,255,.045);
        box-shadow: 0 15px 30px rgba(0,0,0,.22);
    }

    .stProgress > div > div > div {
        border-radius: 999px !important;
    }

    hr {
        border-color: rgba(255,255,255,.09) !important;
    }

    /* Success/info/warning messages */
    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,.10) !important;
        box-shadow: 0 15px 35px rgba(0,0,0,.20) !important;
    }

    /* Comparison table */
    div[data-testid="stTable"] {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0,0,0,.25);
    }

    @media (max-width: 800px) {
        .hero-3d {
            padding: 2rem 1.5rem;
            border-radius: 22px;
        }
        .hero-logo {
            font-size: 3rem;
        }
        .hero-title {
            font-size: 2.8rem;
        }
    }
    </style>
    """
)


# =========================================================
# HEADER
# =========================================================

st.html(
    textwrap.dedent(
        """
    <div class="hero-3d">
        <div style="position:relative; z-index:2; max-width:62%;">
            <div class="hero-logo">💡</div>
            <div class="hero-title">IdeaLens</div>
            <div class="hero-subtitle">
                AI-Powered Project Discovery, Evaluation & Career Guidance
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🤖 Generative AI</span>
                <span class="hero-badge">🎯 Career Aligned</span>
                <span class="hero-badge">📊 Smart Evaluation</span>
                <span class="hero-badge">🚀 Portfolio Focused</span>
            </div>
        </div>
        <div class="hero-scene">
            <div class="orbit one"><span class="orbit-dot"></span></div>
            <div class="orbit two"><span class="orbit-dot"></span></div>
            <div class="ai-orb"></div>
            <div class="floating-chip chip-a">🧠 AI Analysis</div>
            <div class="floating-chip chip-b">📈 Smart Insights</div>
            <div class="floating-chip chip-c">🎯 Career Match</div>
        </div>
    </div>
        """
    )
)

st.html(
    """
    <div class="feature-3d">
        <div style="font-size:1.05rem; font-weight:800;">✨ Turn an idea into a real project.</div>
        <div style="margin-top:7px; color:#cbd5e1;">
            Describe what you want to build, tell IdeaLens about your skills,
            and get an AI-powered evaluation, skill-gap analysis, roadmap,
            and portfolio-ready recommendation.
        </div>
    </div>
    """
)

st.divider()


# =========================================================
# PROJECT IDEA INPUT
# =========================================================

st.markdown("## 💭 Tell us about your project idea")

project_idea = st.text_area(
    "Describe your project",
    placeholder=(
        "Example: I want to build an AI application that helps "
        "students discover project ideas based on their skills..."
    ),
    height=150
)


# =========================================================
# USER PROFILE
# =========================================================

st.markdown("## 👩‍💻 Tell us about yourself")

col1, col2 = st.columns(2)

with col1:

    career_goal = st.selectbox(
        "🎯 Target Career",
        [
            "AI/ML Engineer",
            "Generative AI Engineer",
            "Data Scientist",
            "Data Analyst",
            "Software Developer",
            "Other"
        ]
    )

with col2:

    experience_level = st.selectbox(
        "📚 Experience Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )


skills = st.text_input(
    "🧠 Your Current Skills",
    placeholder=(
        "Example: Python, SQL, Pandas, Machine Learning, "
        "Power BI, Git"
    )
)


# =========================================================
# ANALYZE PROJECT IDEA
# =========================================================

st.divider()

if st.button(
    "✨ Analyze My Idea",
    use_container_width=True,
    type="primary"
):

    if not project_idea.strip():

        st.warning(
            "Please enter a project idea first."
        )

    elif not skills.strip():

        st.warning(
            "Please enter at least a few of your current skills."
        )

    elif client is None:

        st.error(
            "Gemini API key not found. "
            "Please check your .env file."
        )

    else:

        prompt = f"""
You are an expert AI/ML project mentor, career advisor,
and technical project evaluator.

Analyze a student's project idea based on their career goal,
experience level, and current skills.

PROJECT IDEA:
{project_idea}

TARGET CAREER:
{career_goal}

EXPERIENCE LEVEL:
{experience_level}

CURRENT SKILLS:
{skills}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "project_title": "string",

  "overview": "string",

  "problem": "string",

  "scores": {{
    "innovation": 0,
    "impact": 0,
    "feasibility": 0,
    "technical_depth": 0,
    "resume_value": 0,
    "overall": 0
  }},

  "verdict": "string",

  "tech_stack": [
    "string",
    "string",
    "string",
    "string"
  ],

  "skills_you_will_gain": [
    "string",
    "string",
    "string"
  ],

  "skill_gap": [
    {{
      "skill": "string",
      "importance": "High",
      "reason": "string"
    }},
    {{
      "skill": "string",
      "importance": "Medium",
      "reason": "string"
    }},
    {{
      "skill": "string",
      "importance": "Low",
      "reason": "string"
    }}
  ],

  "recommended_features": [
    "string",
    "string",
    "string",
    "string",
    "string"
  ],

  "roadmap": [
    {{
      "phase": "Phase 1",
      "title": "string",
      "tasks": [
        "string",
        "string"
      ]
    }},
    {{
      "phase": "Phase 2",
      "title": "string",
      "tasks": [
        "string",
        "string"
      ]
    }},
    {{
      "phase": "Phase 3",
      "title": "string",
      "tasks": [
        "string",
        "string"
      ]
    }},
    {{
      "phase": "Phase 4",
      "title": "string",
      "tasks": [
        "string",
        "string"
      ]
    }}
  ],

  "alternative_projects": [
    {{
      "title": "string",
      "description": "string",
      "difficulty": "Beginner",
      "reason": "string"
    }},
    {{
      "title": "string",
      "description": "string",
      "difficulty": "Intermediate",
      "reason": "string"
    }},
    {{
      "title": "string",
      "description": "string",
      "difficulty": "Advanced",
      "reason": "string"
    }}
  ],

  "challenges": [
    "string",
    "string",
    "string"
  ],

  "improvements": [
    "string",
    "string",
    "string"
  ],

  "resume_bullet": "string"
}}

Rules:

- Scores must be between 1 and 10.
- Evaluate the idea honestly.
- Compare the project with the student's current skills.
- Do not list skills the student already knows as major skill gaps.
- Skill gaps should focus on skills genuinely needed.
- Importance must be High, Medium, or Low.
- Give exactly 3 alternative projects.
- Alternative projects must match the career goal and experience level.
- Make the roadmap practical and actionable.
- Make the resume bullet professional and concise.
- Do not include Markdown outside the JSON.
"""

        with st.spinner(
            "🔍 IdeaLens is analyzing your profile..."
        ):

            try:

                response = generate_with_retry(prompt)

                data = json.loads(response.text)

                st.success(
                    "Analysis completed! 🎉"
                )


                # =================================================
                # PROJECT EVALUATION
                # =================================================

                st.markdown(
                    "## 📊 IdeaLens Evaluation"
                )

                st.markdown(
                    f"### 🚀 {data['project_title']}"
                )

                st.write(
                    data["overview"]
                )


                # =================================================
                # PROBLEM
                # =================================================

                with st.expander(
                    "🎯 Problem Being Solved",
                    expanded=True
                ):

                    st.write(
                        data["problem"]
                    )


                # =================================================
                # PROJECT SCORES
                # =================================================

                st.markdown(
                    "### ⭐ Project Scores"
                )

                scores = data["scores"]

                score_columns = st.columns(5)

                score_items = [
                    (
                        "Innovation",
                        scores["innovation"]
                    ),
                    (
                        "Impact",
                        scores["impact"]
                    ),
                    (
                        "Feasibility",
                        scores["feasibility"]
                    ),
                    (
                        "Technical Depth",
                        scores["technical_depth"]
                    ),
                    (
                        "Resume Value",
                        scores["resume_value"]
                    )
                ]

                for column, (label, score) in zip(
                    score_columns,
                    score_items
                ):

                    with column:

                        st.html(
                            f"""
                            <div class="score-card">

                                <div class="score-number">
                                    {score}/10
                                </div>

                                <div class="score-label">
                                    {label}
                                </div>

                            </div>
                            """
                        )


                # =================================================
                # OVERALL SCORE
                # =================================================

                st.markdown(
                    "### 🏆 Overall Score"
                )

                overall = float(
                    scores["overall"]
                )

                st.progress(
                    min(overall / 10, 1.0)
                )

                st.html(
                    f"""
                    <div class="glass-card" style="text-align:center; margin-top:14px;">
                        <div style="font-size:.9rem; color:#94a3b8;">OVERALL PROJECT SCORE</div>
                        <div style="
                            font-size:3.4rem;
                            font-weight:850;
                            margin-top:4px;
                            background:linear-gradient(135deg,#ffffff,#67e8f9,#c4b5fd);
                            -webkit-background-clip:text;
                            -webkit-text-fill-color:transparent;">
                            {overall}/10
                        </div>
                    </div>
                    """
                )


                # =================================================
                # VERDICT
                # =================================================

                st.markdown(
                    "### 💡 AI Verdict"
                )

                st.info(
                    data["verdict"]
                )


                # =================================================
                # TECH STACK
                # =================================================

                st.markdown(
                    "### 🛠️ Recommended Tech Stack"
                )

                for tech in data["tech_stack"]:

                    st.markdown(
                        f"- {tech}"
                    )


                # =================================================
                # SKILLS
                # =================================================

                st.markdown(
                    "### 🧠 Skills You'll Gain"
                )

                for skill in data["skills_you_will_gain"]:

                    st.markdown(
                        f"- {skill}"
                    )


                # =================================================
                # SKILL GAP
                # =================================================

                st.divider()

                st.markdown(
                    "## 🧩 Your Skill Gap"
                )

                st.write(
                    "Based on your current skills, IdeaLens "
                    "identifies the additional skills you may "
                    "need for this project."
                )

                for item in data["skill_gap"]:

                    importance = item["importance"]

                    if importance == "High":

                        icon = "🔴"

                    elif importance == "Medium":

                        icon = "🟡"

                    else:

                        icon = "🟢"

                    with st.expander(
                        f"{icon} {item['skill']} — "
                        f"{importance} Priority"
                    ):

                        st.write(
                            item["reason"]
                        )


                # =================================================
                # RECOMMENDED FEATURES
                # =================================================

                st.markdown(
                    "## ✨ Recommended Features"
                )

                for feature in data[
                    "recommended_features"
                ]:

                    st.markdown(
                        f"- {feature}"
                    )


                # =================================================
                # ROADMAP
                # =================================================

                st.markdown(
                    "## 🗺️ Development Roadmap"
                )

                for phase in data["roadmap"]:

                    with st.expander(
                        f"{phase['phase']} — "
                        f"{phase['title']}"
                    ):

                        for task in phase["tasks"]:

                            st.markdown(
                                f"- {task}"
                            )


                # =================================================
                # ALTERNATIVE PROJECTS
                # =================================================

                st.divider()

                st.markdown(
                    "## 💡 Projects You Could Also Build"
                )

                st.write(
                    "Based on your career goal, experience, "
                    "and skills, IdeaLens suggests these "
                    "alternatives:"
                )

                for project in data[
                    "alternative_projects"
                ]:

                    st.html(
                        f"""
                        <div class="recommendation">

                            <h4>
                                🚀 {project['title']}
                            </h4>

                            <p>
                                {project['description']}
                            </p>

                            <b>Difficulty:</b>
                            {project['difficulty']}

                            <br><br>

                            <b>Why it fits:</b>
                            {project['reason']}

                        </div>
                        """
                    )


                # =================================================
                # CHALLENGES
                # =================================================

                st.markdown(
                    "## ⚠️ Possible Challenges"
                )

                for challenge in data["challenges"]:

                    st.markdown(
                        f"- {challenge}"
                    )


                # =================================================
                # IMPROVEMENTS
                # =================================================

                st.markdown(
                    "## 🚀 How to Make This Project Better"
                )

                for improvement in data[
                    "improvements"
                ]:

                    st.markdown(
                        f"- {improvement}"
                    )


                # =================================================
                # RESUME DESCRIPTION
                # =================================================

                st.divider()

                st.markdown(
                    "## 💼 Resume-Ready Description"
                )

                st.success(
                    data["resume_bullet"]
                )


            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an unexpected "
                    "response format. Please try again."
                )


            except Exception as e:

                st.error(
                    "IdeaLens couldn't complete the analysis right now."
                )

                st.info(
                    "The AI service may be temporarily busy. "
                    "Please try again in a few seconds."
                )


# =========================================================
# COMPARE TWO PROJECT IDEAS
# =========================================================

st.divider()

st.markdown(
    "## ⚖️ Compare Two Project Ideas"
)

st.write(
    "Not sure which project to build? Compare two ideas "
    "and let IdeaLens help you choose the stronger one."
)


compare_col1, compare_col2 = st.columns(2)


with compare_col1:

    project_a = st.text_area(
        "🚀 Project Idea A",
        placeholder=(
            "Example: AI chatbot for college PDFs"
        ),
        height=120,
        key="project_a"
    )


with compare_col2:

    project_b = st.text_area(
        "🚀 Project Idea B",
        placeholder=(
            "Example: AI-powered resume analyzer"
        ),
        height=120,
        key="project_b"
    )


if st.button(
    "⚖️ Compare Ideas",
    use_container_width=True
):

    if not project_a.strip():

        st.warning(
            "Please enter Project Idea A."
        )

    elif not project_b.strip():

        st.warning(
            "Please enter Project Idea B."
        )

    elif not skills.strip():

        st.warning(
            "Please enter your current skills "
            "above before comparing."
        )

    elif client is None:

        st.error(
            "Gemini API key not found. "
            "Please check your .env file."
        )

    else:

        comparison_prompt = f"""
You are an expert AI/ML project mentor,
technical evaluator, and career advisor.

Compare two project ideas for a student.

Student Career Goal:
{career_goal}

Student Experience Level:
{experience_level}

Student Current Skills:
{skills}

PROJECT IDEA A:
{project_a}

PROJECT IDEA B:
{project_b}

Evaluate both projects using:

- Innovation
- Impact
- Feasibility
- Technical Depth
- Resume Value

Give every category a score from 1 to 10.

Calculate an overall score from the five categories.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "project_a": {{
    "title": "string",
    "innovation": 0,
    "impact": 0,
    "feasibility": 0,
    "technical_depth": 0,
    "resume_value": 0,
    "overall": 0
  }},

  "project_b": {{
    "title": "string",
    "innovation": 0,
    "impact": 0,
    "feasibility": 0,
    "technical_depth": 0,
    "resume_value": 0,
    "overall": 0
  }},

  "winner": "A or B",

  "recommendation": "string",

  "reasoning": [
    "string",
    "string",
    "string"
  ]
}}

Rules:

- Scores must be between 1 and 10.
- Overall score must reflect all five categories.
- Consider the student's career goal.
- Consider the student's current skills.
- Consider the student's experience level.
- Do not automatically choose the more complex project.
- Give an honest recommendation.
- Do not include Markdown outside the JSON.
"""


        with st.spinner(
            "⚖️ Comparing your project ideas..."
        ):

            try:

                comparison_response = generate_with_retry(comparison_prompt)

                comparison = json.loads(
                    comparison_response.text
                )


                st.success(
                    "Comparison completed! 🎉"
                )


                # =================================================
                # COMPARISON DATA
                # =================================================

                project_a_data = comparison[
                    "project_a"
                ]

                project_b_data = comparison[
                    "project_b"
                ]


                # =================================================
                # COMPARISON TABLE
                # =================================================

                st.markdown(
                    "### 📊 Project Comparison"
                )

                comparison_table = {

                    "Category": [
                        "Innovation",
                        "Impact",
                        "Feasibility",
                        "Technical Depth",
                        "Resume Value",
                        "Overall"
                    ],

                    project_a_data["title"]: [
                        project_a_data["innovation"],
                        project_a_data["impact"],
                        project_a_data["feasibility"],
                        project_a_data["technical_depth"],
                        project_a_data["resume_value"],
                        project_a_data["overall"]
                    ],

                    project_b_data["title"]: [
                        project_b_data["innovation"],
                        project_b_data["impact"],
                        project_b_data["feasibility"],
                        project_b_data["technical_depth"],
                        project_b_data["resume_value"],
                        project_b_data["overall"]
                    ]
                }

                st.table(
                    comparison_table
                )


                # =================================================
                # WINNER
                # =================================================

                winner = comparison["winner"]


                if winner == "A":

                    winner_title = (
                        project_a_data["title"]
                    )

                    winner_score = (
                        project_a_data["overall"]
                    )

                else:

                    winner_title = (
                        project_b_data["title"]
                    )

                    winner_score = (
                        project_b_data["overall"]
                    )


                st.markdown(
                    "### 🏆 IdeaLens Recommendation"
                )

                st.success(
                    f"Recommended Project: "
                    f"{winner_title}"
                )

                st.metric(
                    "Overall Score",
                    f"{winner_score}/10"
                )


                # =================================================
                # RECOMMENDATION
                # =================================================

                st.markdown(
                    "### 💡 Why IdeaLens Recommends It"
                )

                st.write(
                    comparison["recommendation"]
                )


                # =================================================
                # REASONING
                # =================================================

                st.markdown(
                    "### 🔍 Key Reasons"
                )

                for reason in comparison[
                    "reasoning"
                ]:

                    st.markdown(
                        f"- {reason}"
                    )


            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an unexpected "
                    "comparison format. Please try again."
                )


            except Exception as e:

                st.error(
                    "IdeaLens couldn't compare the projects right now."
                )

                st.info(
                    "The AI service may be temporarily busy. "
                    "Please try again in a few seconds."
                )


# =========================================================
# FOOTER

# =========================================================

st.divider()

st.caption(
    "IdeaLens • AI-powered project discovery, "
    "evaluation & career guidance"
)