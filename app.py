
import html
import re
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="QALQAN | Message Safety",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Use Streamlit's minimal toolbar where supported.
st.set_option("client.toolbarMode", "minimal")

BLUE = "#3559D8"
PEACH = "#F9C6B5"
LAVENDER = "#DCD2FF"
MINT = "#DDF3E8"
DARK = "#242642"
MUTED = "#74768C"

RULES = [
    {
        "name": "Urgency and pressure",
        "weight": 2,
        "terms": [
            "act now", "immediately", "urgent", "urgently",
            "within 24 hours", "right now", "limited time",
            "last chance", "срочно", "немедленно", "прямо сейчас",
            "в течение 24 часов", "последний шанс",
            "тез арада", "шұғыл", "дереу",
        ],
        "explanation": "The message pressures you to act quickly.",
    },
    {
        "name": "Prize or unexpected reward",
        "weight": 2,
        "terms": [
            "you won", "you have won", "winner", "congratulations",
            "claim your prize", "free iphone", "cash prize",
            "free money", "you are selected", "won a prize",
            "вы выиграли", "ты выиграл", "ваш приз",
            "получите подарок", "бесплатные деньги",
            "ұтып алдыңыз", "сіз жеңдіңіз",
        ],
        "explanation": "Unexpected prizes and rewards can be used as bait.",
    },
    {
        "name": "Sensitive information request",
        "weight": 3,
        "terms": [
            "send your password", "enter your password",
            "share your password", "your verification code",
            "send the code", "enter the code", "bank card details",
            "card number", "cvv", "pin code", "social security number",
            "введите пароль", "отправьте пароль", "назовите код",
            "код подтверждения", "данные карты", "номер карты",
            "пин-код", "пароль от аккаунта",
            "құпиясөз", "растау кодын", "карта деректері",
        ],
        "explanation": "The message asks for private account or payment information.",
    },
    {
        "name": "Suspicious payment or transfer",
        "weight": 3,
        "terms": [
            "pay a fee", "pay to receive", "transfer money",
            "send money", "processing fee", "pay delivery",
            "payment required", "make a deposit", "gift card payment",
            "переведите деньги", "отправьте деньги",
            "оплатите комиссию", "оплатите доставку",
            "требуется оплата", "сделайте перевод",
            "ақша аударыңыз", "төлем жасаңыз",
        ],
        "explanation": "A payment or transfer is requested in a potentially suspicious context.",
    },
    {
        "name": "Links and destinations",
        "weight": 1,
        "terms": [
            "click this link", "click the link", "open this link",
            "verify your account here", "follow this link",
            "перейдите по ссылке", "нажмите на ссылку",
            "откройте ссылку", "ссылка для входа",
            "сілтемеге өтіңіз",
        ],
        "explanation": "The message directs you to a link or online destination.",
    },
    {
        "name": "Impersonation or threats",
        "weight": 2,
        "terms": [
            "your account is blocked", "account will be blocked",
            "account suspended", "your account will be deleted",
            "lose access", "legal action", "police will",
            "we will close your account", "bank security department",
            "your bank account", "final warning",
            "ваш аккаунт заблокирован", "аккаунт будет заблокирован",
            "ваш счёт заблокирован", "потеряете доступ",
            "последнее предупреждение", "служба безопасности банка",
            "полиция", "аккаунт удалят",
            "аккаунтыңыз бұғатталды", "соңғы ескерту",
        ],
        "explanation": "The sender may be impersonating an authority or using threats.",
    },
]

SAMPLES = {
    "Suspicious prize message": (
        "Congratulations! You won a free iPhone. "
        "Claim your prize immediately. Send your password to receive it."
    ),
    "Suspicious parcel message": (
        "Your parcel is waiting. Pay a delivery fee immediately "
        "and click this link to receive your package."
    ),
    "Suspicious password request": (
        "Your account will be blocked. Enter your password "
        "and send your verification code immediately."
    ),
    "Suspicious bank message": (
        "Your bank account is blocked. Click this link and enter "
        "your password or you will lose access to your money."
    ),
    "Ordinary school message": (
        "Hi everyone, remember to bring your notebooks tomorrow. "
        "Our lesson starts at 9."
    ),
    "Ordinary friendly message": (
        "Hey! Do you want to play a game after school? "
        "I will be online at six."
    ),
    "Kazakh example": (
        "Сәлем! Ертең сабақ сағат тоғызда басталады. "
        "Дәптеріңді алып кел."
    ),
}


def normalize(text):
    return re.sub(r"\s+", " ", text.lower().replace("ё", "е")).strip()


def analyze_message(message):
    normalized = normalize(message)
    findings = []

    for rule in RULES:
        matches = [
            term for term in rule["terms"]
            if normalize(term) in normalized
        ]

        if matches:
            findings.append({
                "name": rule["name"],
                "weight": rule["weight"],
                "matches": matches,
                "explanation": rule["explanation"],
            })

    score = min(sum(item["weight"] for item in findings), 10)

    if score >= 4:
        risk = "Suspicious"
        recommendation = (
            "Do not click links or share private information. "
            "Verify the sender through an official channel."
        )
    elif score > 0:
        risk = "Needs attention"
        recommendation = (
            "Pause and check the sender and details independently."
        )
    else:
        risk = "Low detected risk"
        recommendation = (
            "No known warning phrases were detected. "
            "This does not guarantee that the message is safe."
        )

    return {
        "score": score,
        "risk": risk,
        "findings": findings,
        "recommendation": recommendation,
    }


def risk_color(score):
    if score >= 4:
        return "#C74454"
    if score > 0:
        return "#B47720"
    return "#27845D"


def render_highlights(message, findings):
    terms = sorted(
        {term for finding in findings for term in finding["matches"]},
        key=len,
        reverse=True,
    )
    safe_message = html.escape(message)

    for term in terms:
        escaped_term = html.escape(term)
        pattern = re.compile(re.escape(escaped_term), re.IGNORECASE)
        safe_message = pattern.sub(
            lambda match: (
                '<mark style="background:#F9C6B5;'
                'padding:2px 4px;border-radius:4px;">'
                + match.group(0) + "</mark>"
            ),
            safe_message,
        )

    return safe_message


TEST_MESSAGES = [
    {
        "message": "Your account is blocked. Enter your password immediately.",
        "label": True,
        "category": "Account threat",
    },
    {
        "message": "Congratulations! You won a prize. Claim your prize now.",
        "label": True,
        "category": "Prize bait",
    },
    {
        "message": "Pay a fee to receive your parcel. Click this link.",
        "label": True,
        "category": "Parcel fee",
    },
    {
        "message": "Send your verification code and bank card details.",
        "label": True,
        "category": "Private information",
    },
    {
        "message": "Your bank account will be blocked. Transfer money now.",
        "label": True,
        "category": "Bank impersonation",
    },
    {
        "message": "Last chance! Pay a processing fee to claim free money.",
        "label": True,
        "category": "Urgency and payment",
    },
    {
        "message": "Hi! Do you want to play a game after school?",
        "label": False,
        "category": "Friendly message",
    },
    {
        "message": "Please bring your notebook to class tomorrow.",
        "label": False,
        "category": "School reminder",
    },
    {
        "message": "Our lesson starts at nine. See you tomorrow!",
        "label": False,
        "category": "School schedule",
    },
    {
        "message": "I will send you the drawing when I finish it.",
        "label": False,
        "category": "Ordinary conversation",
    },
    {
        "message": "Сәлем! Ертең сабақ сағат тоғызда басталады.",
        "label": False,
        "category": "Kazakh school message",
    },
    {
        "message": "What game are you playing today?",
        "label": False,
        "category": "Gaming conversation",
    },
]


def evaluate_test_set():
    rows = []

    for item in TEST_MESSAGES:
        result = analyze_message(item["message"])
        predicted = result["score"] >= 4
        actual = item["label"]

        if predicted and actual:
            outcome = "True positive"
        elif predicted and not actual:
            outcome = "False positive"
        elif not predicted and actual:
            outcome = "False negative"
        else:
            outcome = "True negative"

        rows.append({
            "Category": item["category"],
            "Message": item["message"],
            "Expected": "Suspicious" if actual else "Ordinary",
            "Predicted": "Suspicious" if predicted else "Ordinary",
            "Score": result["score"],
            "Outcome": outcome,
            "Correct": predicted == actual,
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "🏠 Overview"

if "history" not in st.session_state:
    st.session_state.history = []

if "message_input" not in st.session_state:
    st.session_state.message_input = ""

if "lab_results" not in st.session_state:
    st.session_state.lab_results = None


def go_to(page):
    st.session_state.page = page


def load_sample():
    selected = st.session_state.get("sample_choice", "")
    if selected in SAMPLES:
        st.session_state.message_input = SAMPLES[selected]


def save_analysis(message, result):
    st.session_state.history.insert(0, {
        "message": message,
        "score": result["score"],
        "risk": result["risk"],
    })
    st.session_state.history = st.session_state.history[:10]


# --------------------------------------------------
# Design and FIXED SIDEBAR COLORS
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #FAF9F7;
        color: #242642;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: #242642;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    section[data-testid="stSidebar"] {
        background: #F0EDFF !important;
        border-right: 1px solid #E2DDF7;
    }

    /* Force sidebar text to stay dark */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        color: #242642;
    }

    section[data-testid="stSidebar"] h1 {
        color: #3559D8 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #242642 !important;
        background: transparent;
        border-radius: 10px;
        padding: 9px 10px;
        transition: background 0.15s ease;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] label span {
        color: #242642 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #E5DFFF !important;
    }

    /* Selected navigation item */
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #DCD2FF !important;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] input {
        accent-color: #3559D8 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        gap: 8px;
    }

    .hero {
        background: linear-gradient(125deg, #E8EDFF 0%, #F5EFFF 55%, #FFE9E1 100%);
        padding: 32px;
        border-radius: 24px;
        border: 1px solid #E7E2F6;
        margin-bottom: 22px;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 12px;
        font-weight: 800;
        color: #3559D8;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 38px;
        line-height: 1.15;
        font-weight: 800;
        margin: 10px 0;
        color: #242642;
    }

    .hero-copy {
        color: #5F617B;
        font-size: 16px;
        max-width: 720px;
    }

    .soft-card {
        background: white;
        border: 1px solid #E9E7EF;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .soft-card h3 {
        margin-top: 0;
    }

    .metric-card {
        background: white;
        border: 1px solid #E9E7EF;
        border-radius: 18px;
        padding: 20px;
        min-height: 115px;
    }

    .metric-label {
        color: #74768C;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #242642;
        font-family: 'Manrope', sans-serif;
        font-size: 29px;
        font-weight: 800;
        margin-top: 5px;
    }

    .tag {
        display: inline-block;
        background: #F0EDFF;
        color: #4B42A5;
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: 700;
    }

    .stButton > button {
        background: #3559D8;
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        min-height: 42px;
    }

    .stButton > button:hover {
        background: #2947B7;
        color: white !important;
        border: none;
    }

    .stTextArea textarea {
        border-radius: 14px;
        border-color: #DDD9EB;
        background: #FFFFFF;
    }

    div[data-baseweb="select"] > div {
        border-radius: 12px;
    }

    hr {
        border-color: #E9E7EF;
    }

    /* Hide Streamlit's built-in menu, toolbar, footer, and GitHub links. */
    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    .viewerBadge_container__1QSob,
    a[href*="github.com"],
    a[aria-label*="GitHub"],
    a[title*="GitHub"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Top-to-bottom entrance: begin pale, then return to the original colors. */
    @keyframes qalqan-drop-color {
        0% {
            opacity: 0;
            transform: translateY(-22px);
            filter: grayscale(1) brightness(1.8);
        }
        55% {
            opacity: 1;
            filter: grayscale(0.45) brightness(1.25);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
            filter: grayscale(0) brightness(1);
        }
    }

    @keyframes qalqan-sidebar-in {
        0% {
            opacity: 0;
            transform: translateY(-16px);
            filter: grayscale(1) brightness(1.7);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
            filter: grayscale(0) brightness(1);
        }
    }

    /* Main content appears in a gentle cascade from the top down. */
    .block-container > div {
        animation: qalqan-drop-color 850ms cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .block-container > div:nth-child(2) { animation-delay: 90ms; }
    .block-container > div:nth-child(3) { animation-delay: 180ms; }
    .block-container > div:nth-child(4) { animation-delay: 270ms; }
    .block-container > div:nth-child(5) { animation-delay: 360ms; }
    .block-container > div:nth-child(6) { animation-delay: 450ms; }
    .block-container > div:nth-child(7) { animation-delay: 540ms; }
    .block-container > div:nth-child(8) { animation-delay: 630ms; }

    section[data-testid="stSidebar"] {
        animation: qalqan-sidebar-in 900ms cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .hero {
        animation: qalqan-drop-color 950ms cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .soft-card,
    .metric-card {
        transition: transform 220ms ease, box-shadow 220ms ease,
                    border-color 220ms ease;
    }

    .soft-card:hover,
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(36, 38, 66, 0.07);
        border-color: #DCD7F0;
    }

    .stButton > button {
        transition: transform 180ms ease, box-shadow 180ms ease,
                    background-color 180ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(53, 89, 216, 0.18);
    }

    .footer {
        text-align: center;
        color: #88899B;
        font-size: 12px;
        padding: 28px 0 0;
        animation: qalqan-drop-color 1000ms ease-out both;
    }

    /* Respect visitors who prefer reduced motion. */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar navigation
# --------------------------------------------------

PAGES = [
    "🏠 Overview",
    "🔎 Analyzer",
    "📚 Safety Academy",
    "🧪 Test Lab",
    "💡 About QALQAN",
]

with st.sidebar:
    st.markdown("# 🛡️ QALQAN")
    st.caption("Message safety, made understandable.")
    st.markdown("---")

    st.radio(
        "NAVIGATION",
        PAGES,
        key="page",
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown("**Creative Lab edition**")
    st.caption("A student prototype for safer digital communication.")

page = st.session_state.page


# --------------------------------------------------
# Overview
# --------------------------------------------------

if page == "🏠 Overview":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Your digital safety companion</div>
            <div class="hero-title">Think twice.<br>Click wisely.</div>
            <div class="hero-copy">
                QALQAN checks messages for common warning signs,
                explains what looks suspicious, and helps you decide
                what to verify before taking action.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="soft-card">
                <span class="tag">01 / ANALYZE</span>
                <h3>🔎 Check a message</h3>
                Paste a message and inspect the warning signs.
                QALQAN explains the reasons behind its score.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open analyzer", key="overview_analyzer", use_container_width=True):
            go_to("🔎 Analyzer")
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="soft-card">
                <span class="tag">02 / LEARN</span>
                <h3>📚 Learn the patterns</h3>
                Explore common scam techniques and simple ways
                to protect your accounts and personal information.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Safety Academy", key="overview_academy", use_container_width=True):
            go_to("📚 Safety Academy")
            st.rerun()

    st.markdown("### Your workspace")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Messages analyzed</div>
                <div class="metric-value">{len(st.session_state.history)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        flagged = sum(
            1 for item in st.session_state.history
            if item["score"] >= 4
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Flagged messages</div>
                <div class="metric-value">{flagged}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Built-in test examples</div>
                <div class="metric-value">12</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Recent analyses")

    if not st.session_state.history:
        st.info("Your recent analyses will appear here after you check a message.")
    else:
        for item in st.session_state.history[:5]:
            with st.container(border=True):
                st.markdown(f"**{html.escape(item['message'][:140])}**")
                st.caption(f"Score: {item['score']}/10 · {item['risk']}")


# --------------------------------------------------
# Analyzer
# --------------------------------------------------

elif page == "🔎 Analyzer":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Message scanner</div>
            <div class="hero-title">Let's inspect that message.</div>
            <div class="hero-copy">
                Paste a message below, or choose an example to try.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.selectbox(
        "Try an example",
        ["Choose an example..."] + list(SAMPLES.keys()),
        key="sample_choice",
        on_change=load_sample,
    )

    message = st.text_area(
        "Message to analyze",
        key="message_input",
        height=180,
        placeholder="Paste the message here...",
    )

    if st.button("🔍 Analyze message", key="analyze_button", use_container_width=True):
        if not message.strip():
            st.warning("Paste a message first, then run the analysis.")
        else:
            result = analyze_message(message)
            save_analysis(message, result)
            st.session_state.last_result = result
            st.session_state.last_message = message

    if "last_result" in st.session_state:
        result = st.session_state.last_result
        analyzed_message = st.session_state.last_message
        score = result["score"]
        color = risk_color(score)

        st.markdown("---")
        st.markdown("### Analysis results")

        left, right = st.columns([1, 2])

        with left:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Suspicion score</div>
                    <div class="metric-value" style="color:{color}">
                        {score}<span style="font-size:17px">/10</span>
                    </div>
                    <p style="color:{color};font-weight:700">{result['risk']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(score / 10)

        with right:
            st.markdown("#### What did QALQAN notice?")
            if result["findings"]:
                for finding in result["findings"]:
                    st.markdown(
                        f"""
                        <div class="soft-card">
                            <b>{html.escape(finding['name'])}</b>
                            <span class="tag">+{finding['weight']} points</span>
                            <p>{html.escape(finding['explanation'])}</p>
                            <small>Matched: {html.escape(", ".join(finding['matches']))}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.success("No known warning phrases were detected.")

        st.markdown("#### Message with detected phrases")
        st.markdown(
            f"""
            <div class="soft-card" style="overflow-wrap:anywhere">
                {render_highlights(analyzed_message, result['findings'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### What should you do?")
        st.info(result["recommendation"])
        st.caption(
            "This score is based on phrase-matching rules. "
            "It is not proof that a message is safe or fraudulent."
        )


# --------------------------------------------------
# Safety Academy
# --------------------------------------------------

elif page == "📚 Safety Academy":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Safety Academy</div>
            <div class="hero-title">Spot the red flags.</div>
            <div class="hero-copy">
                Scams often rely on pressure, curiosity, fear, or tempting rewards.
                Knowing the patterns helps you pause and verify.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lessons = [
        (
            "⏰ Urgency and pressure",
            "“Act now or your account will be closed!”",
            "Pause. Verify a warning through an official channel instead of rushing.",
            PEACH,
        ),
        (
            "🎁 Unexpected prizes",
            "“Congratulations! You won a phone!”",
            "Be careful with prizes you never entered to win. Never reveal a password to claim a reward.",
            LAVENDER,
        ),
        (
            "🔐 Private information",
            "“Send us your password and verification code.”",
            "Do not share passwords or one-time codes in response to a message.",
            MINT,
        ),
        (
            "💳 Suspicious payments",
            "“Transfer money to unlock your package.”",
            "Check unexpected payment requests independently.",
            PEACH,
        ),
        (
            "🔗 Unexpected links",
            "“Click here to verify your account.”",
            "Visit the official website yourself instead of trusting an unexpected link.",
            LAVENDER,
        ),
        (
            "🎭 Impersonation and threats",
            "“We are your bank. Your account will be blocked.”",
            "Contact the organization using a verified channel.",
            MINT,
        ),
    ]

    for title, example, advice, color in lessons:
        st.markdown(
            f"""
            <div class="soft-card" style="border-left:5px solid {color}">
                <h3>{title}</h3>
                <p><b>Example:</b> {html.escape(example)}</p>
                <p>{html.escape(advice)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "A message can be dangerous even without these phrases. "
        "Always consider the context and verify the sender."
    )


# --------------------------------------------------
# Test Lab
# --------------------------------------------------

elif page == "🧪 Test Lab":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Evaluation workspace</div>
            <div class="hero-title">Test the detector.</div>
            <div class="hero-copy">
                Run a fixed set of labeled examples and compare QALQAN's
                predictions with the expected labels.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### How the evaluation works")
    st.markdown(
        """
        - **Suspicious** is predicted when the score is **4/10 or higher**.
        - Every example has an expected label assigned in advance.
        - The results show where the detector succeeds and where it makes mistakes.
        """
    )

    if st.button("🧪 Run all 12 tests", key="run_lab", use_container_width=True):
        st.session_state.lab_results = evaluate_test_set()

    if st.session_state.lab_results is None:
        st.info("Run the test set to calculate the evaluation metrics.")
    else:
        df = st.session_state.lab_results

        tp = int((df["Outcome"] == "True positive").sum())
        tn = int((df["Outcome"] == "True negative").sum())
        fp = int((df["Outcome"] == "False positive").sum())
        fn = int((df["Outcome"] == "False negative").sum())
        total = len(df)

        accuracy = (tp + tn) / total if total else 0
        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        specificity = tn / (tn + fp) if (tn + fp) else 0

        st.markdown("---")
        st.markdown("### Performance overview")

        columns = st.columns(4)
        metrics = [
            ("Accuracy", accuracy, "Correct predictions overall"),
            ("Precision", precision, "Flagged messages that are truly suspicious"),
            ("Recall", recall, "Suspicious examples detected"),
            ("Specificity", specificity, "Ordinary examples correctly cleared"),
        ]

        for col, (label, value, description) in zip(columns, metrics):
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value:.0%}</div>
                        <div style="font-size:12px;color:#74768C">{description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.caption(
            f"Evaluated {total} labeled examples. "
            "These results describe this small built-in test set only."
        )

        st.markdown("### Confusion matrix")
        matrix = pd.DataFrame(
            [[tp, fn], [fp, tn]],
            index=["Actually suspicious", "Actually ordinary"],
            columns=["Predicted suspicious", "Predicted ordinary"],
        )
        st.dataframe(matrix, use_container_width=True)

        a, b, c, d = st.columns(4)
        a.metric("True positives", tp)
        b.metric("True negatives", tn)
        c.metric("False positives", fp)
        d.metric("False negatives", fn)

        with st.expander("What do these results mean?"):
            st.markdown(
                """
                - **True positive:** a suspicious message was correctly flagged.
                - **True negative:** an ordinary message was correctly classified.
                - **False positive:** an ordinary message was incorrectly flagged.
                - **False negative:** a suspicious message was missed.

                A useful detector should catch suspicious messages while avoiding
                too many false alarms.
                """
            )

        st.markdown("### Individual test results")
        st.dataframe(
            df[["Category", "Expected", "Predicted", "Score", "Outcome"]],
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("View the full test messages"):
            st.dataframe(
                df[["Category", "Message", "Expected", "Predicted", "Score"]],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### What to improve next")

        if fp > 0:
            st.warning(
                f"QALQAN raised {fp} false alarm(s). "
                "Review these ordinary messages and adjust overly broad rules."
            )
        else:
            st.success("No false alarms in this small test set.")

        if fn > 0:
            st.warning(
                f"QALQAN missed {fn} suspicious message(s). "
                "Review their wording and add useful variations to the rules."
            )
        else:
            st.success("All suspicious examples in this test set were detected.")

        st.caption(
            "This test set is small and hand-written. "
            "For stronger evaluation, test more realistic messages that were "
            "not used while designing the rules."
        )


# --------------------------------------------------
# About QALQAN
# --------------------------------------------------

elif page == "💡 About QALQAN":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">About the project</div>
            <div class="hero-title">QALQAN protects through awareness.</div>
            <div class="hero-copy">
                A student-built prototype that helps people recognize
                suspicious messages and understand common online safety risks.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### The idea")
    st.markdown(
        """
        Online scams often use familiar patterns: urgent demands, unexpected
        prizes, suspicious payment requests, and attempts to collect private data.

        QALQAN checks message text against warning phrases, calculates a
        suspicion score, and explains which patterns were found.
        """
    )

    st.markdown("### What the prototype can do")
    st.markdown(
        """
        - Analyze pasted text using phrase-matching rules.
        - Explain detected warning signs.
        - Offer basic safety recommendations.
        - Run a labeled test set and display evaluation metrics.
        """
    )

    st.markdown("### Current limitations")
    st.markdown(
        """
        - It uses rules, not a trained machine-learning model.
        - It may miss unfamiliar wording, slang, or new scam techniques.
        - It may flag harmless messages containing suspicious phrases.
        - Its score is a heuristic, not a verified probability of fraud.
        - The built-in test set is small and cannot represent every real-world message.
        """
    )

    st.info(
        "QALQAN is a learning and awareness tool. "
        "When a message asks for money, passwords, or verification codes, "
        "verify it through an independent official channel."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        QALQAN · Creative Lab · Think twice. Click wisely.
    </div>
    """,
    unsafe_allow_html=True,
)
