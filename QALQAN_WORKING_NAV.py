import html
import json
import urllib.request
import urllib.error
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

BLUE = "#79C9B0"
PEACH = "#D9A36E"
LAVENDER = "#9BBBD0"
MINT = "#79C9B0"
DARK = "#E6EDF4"
MUTED = "#9BAFC0"

RULES = [
    {
        "name": "Urgency and pressure",
        "weight": 2,
        "terms": [
            "act now", "immediately", "urgent", "urgently",
            "within 24 hours", "right now", "limited time",
            "last chance", "срочно", "немедленно", "прямо сейчас",
            "в течение 24 часов", "последний шанс", "в течение 15 минут", "в течение 30 минут",
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
            "код подтверждения", "данные карты", "личные данные", "номер карты",
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
            "требуется оплата", "сделайте перевод", "оплатите штраф", "штраф в размере",
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
            "последнее предупреждение", "служба безопасности банка", "служба безопасности вашего банка", "подозрительную активность", "предотвращения блокировки",
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
    """Transparent, offline scam-risk rules. No API, no keys, no network calls."""
    normalized = normalize(message)
    findings = []

    # Each category is counted once, even if several expressions match.
    # Expressions are indicative signals, not definitive proof of fraud.
    categories = [
        ("Urgency and pressure", 2, "The sender pressures you to act quickly.", [
            r"\bсрочн\w*\b", r"\bнемедленн\w*\b", r"\bнезамедлительн\w*\b",
            r"\bпрямо сейчас\b", r"\bв течение\s+\d+\s*(?:минут|час\w*)\b",
            r"\b(?:за|через)\s+\d+\s*(?:минут|час\w*)\b",
            r"\b(?:осталось|дается|даётся)\s+\d+\s*(?:минут|час\w*)\b",
            r"\bпоследн\w+\s+(?:шанс|предупрежден\w*)\b",
            r"\b(?:urgent|immediately|act now|right now|last chance)\b",
            r"\b(?:within|in)\s+\d+\s*(?:minutes?|hours?)\b",
            r"\b(?:шұғыл|дереу|тез арада)\b",
        ]),
        ("Threats and intimidation", 3, "Threats of punishment, blocking, or prosecution are used to pressure you.", [
            r"\b(?:заблокир\w*|блокировк\w*|замороз\w*|арест\w*|отключ\w*)\b",
            r"\b(?:уголовн\w+\s+дел\w*|возбужден\w+\s+дел\w*|судебн\w+\s+разбирательств\w*)\b",
            r"\b(?:правоохранительн\w+\s+орган\w*|передан\w+\s+в\s+полици\w*|передан\w+\s+в\s+суд)\b",
            r"\b(?:штраф\w*|наказан\w*|ответственност\w*|задержан\w*)\b",
            r"\b(?:account (?:will be )?(?:blocked|locked|suspended)|legal action|arrest|prosecution)\b",
            r"\b(?:бұғаттал\w*|айыппұл|полицияға)\b",
        ]),
        ("Money or payment demand", 3, "The message asks for a transfer, payment, or fee.", [
            r"\b(?:переведите|перевести|переводите|отправьте|скиньте|внесите|оплатите|заплатите)\b.{0,50}\b(?:деньги|сумм\w*|тенге|тг|₸|рубл\w*|штраф\w*|комисси\w*|сбор\w*|сч[её]т|реквизит\w*)\b",
            r"\b(?:оплатите|переведите|заплатите|внесите)\s+\d[\d\s]*(?:₸|тг|тенге|руб|₽|\$)\b",
            r"\b(?:для получения|чтобы получить)\b.{0,65}\b(?:оплат\w*|перевед\w*|заплат\w*)\b",
            r"\b(?:предоплат\w*|комисси\w+\s+за\s+(?:вывод|получение)|перевод\s+на\s+(?:карту|сч[её]т))\b",
            r"\b(?:transfer|send|pay)\b.{0,40}\b(?:money|fee|deposit|fine|payment)\b",
            r"\b(?:ақша аудар\w*|төлем жаса\w*|айыппұл төле\w*)\b",
        ]),
        ("Password, code or personal data", 4, "The message requests sensitive account, identity, or bank information.", [
            r"\b(?:парол\w*|пин[- ]?код\w*|cvv|cvc|код\s+(?:из\s+смс|подтверждения|доступа)|одноразов\w+\s+код\w*)\b",
            r"\b(?:номер\s+карт\w*|данн\w+\s+(?:карт\w*|паспорт\w*|удостоверени\w*)|личн\w+\s+данн\w*)\b",
            r"\b(?:подтверд\w*|сообщ\w*|назов\w*|введ\w*|отправ\w*)\b.{0,45}\b(?:личност\w*|данн\w*|код\w*|парол\w*|карт\w*)\b",
            r"\b(?:password|passcode|verification code|otp|cvv|card details|personal data|pin code)\b",
            r"\b(?:құпиясөз|растау кодын|карта деректері)\b",
        ]),
        ("Impersonation of an organization", 2, "The sender claims authority from a bank, agency, or support team.", [
            r"\b(?:служб\w+\s+безопасност\w*|сотрудник\w+\s+(?:банк\w*|полици\w*|служб\w*))\b",
            r"\b(?:центральн\w+\s+банк\w*|национальн\w+\s+банк\w*|налогов\w+\s+(?:служб\w*|орган\w*))\b",
            r"\b(?:от\s+имени\s+(?:банк\w*|полици\w*|госорган\w*)|официальн\w+\s+уведомлен\w*)\b",
            r"\b(?:bank security|security department|government agency|official notice)\b",
        ]),
        ("Links or external actions", 1, "A link or external destination needs independent verification.", [
            r"https?://[^\s<>]+", r"www\.[^\s<>]+",
            r"\b(?:перейдите|переходите|нажмите|откройте|кликните)\b.{0,30}\b(?:ссылк\w*|сайт\w*|адрес\w*)\b",
            r"\b(?:click|follow|open)\b.{0,20}\b(?:link|url|website)\b",
            r"\bсілтемеге\s+өтіңіз\b",
        ]),
        ("Secrecy or isolation", 2, "The sender discourages you from verifying the message with others.", [
            r"\b(?:никому\s+не\s+(?:говорите|рассказывайте|сообщайте)|не\s+сообщайте\s+(?:об\s+этом|третьим\s+лицам))\b",
            r"\b(?:держите\s+в\s+секрете|это\s+конфиденциально|не\s+обращайтесь\s+в\s+банк)\b",
            r"\b(?:do not tell anyone|keep this secret|don't contact the bank)\b",
        ]),
        ("Unexpected prize or easy profit", 2, "Unexpected prizes or easy profits can be used as bait.", [
            r"\b(?:вы\s+выиграли|поздравляем.{0,25}выигр\w*|заберите\s+(?:приз|подарок)|вам\s+полагается\s+(?:приз|выплата))\b",
            r"\b(?:гарантированн\w+\s+(?:доход|заработок)|быстр\w+\s+заработок|легк\w+\s+деньги)\b",
            r"\b(?:you (?:have )?won|claim your prize|guaranteed profit|free money)\b",
            r"\b(?:ұтып алдыңыз|сіз жеңдіңіз)\b",
        ]),
        ("Suspicious installation or remote access", 4, "Requests to install software or give remote access can be dangerous.", [
            r"\b(?:установите|скачайте|загрузите)\b.{0,45}\b(?:приложени\w*|программ\w*|apk|файл\w*)\b",
            r"\b(?:удаленн\w+\s+доступ|доступ\s+к\s+экран\w*|демонстраци\w+\s+экран\w*)\b",
            r"\b(?:install this app|download the apk|remote access|share your screen)\b",
        ]),
    ]

    for name, weight, explanation, patterns in categories:
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, normalized, flags=re.IGNORECASE):
                fragment = message[match.start():match.end()].strip()
                if fragment and fragment.casefold() not in [m.casefold() for m in matches]:
                    matches.append(fragment)
                if len(matches) >= 5:
                    break
            if len(matches) >= 5:
                break
        if matches:
            findings.append({
                "name": name,
                "weight": weight,
                "matches": matches,
                "explanation": explanation,
            })

    names = {item["name"] for item in findings}

    # Context matters: a warning ABOUT scams is not itself a scam.
    educational = bool(re.search(
        r"(?:никогда\s+не\s+(?:сообщайте|передавайте|вводите|переходите)|"
        r"не\s+(?:сообщайте|передавайте)\s+(?:парол|код)|"
        r"(?:мошенник|фишинг|скам|осторожно|как распознать|признаки мошенничества)|"
        r"(?:never share|do not share|beware of scams))",
        normalized,
    ))
    direct_request = bool(re.search(
        r"(?:\b(?:срочно\s+)?(?:назовите|сообщите|введите|подтвердите|переведите|"
        r"оплатите|заплатите|скиньте|отправьте|установите|скачайте)\b|"
        r"\b(?:send|enter|verify|transfer|pay|install)\b)", normalized,
    ))

    # Calibrated, non-additive scale. A single weak clue stays weak.
    weights = {
        "Urgency and pressure": 1,
        "Threats and intimidation": 2,
        "Money or payment demand": 2,
        "Password, code or personal data": 2,
        "Impersonation of an organization": 1,
        "Links or external actions": 1,
        "Secrecy or isolation": 1,
        "Unexpected prize or easy profit": 2,
        "Suspicious installation or remote access": 3,
    }
    score = sum(weights[name] for name in names)

    # A targeted threat plus money/data is substantially more concerning.
    if "Threats and intimidation" in names and "Money or payment demand" in names:
        score += 2
    if "Password, code or personal data" in names and direct_request:
        score += 2
    if "Urgency and pressure" in names and (
        "Money or payment demand" in names or "Password, code or personal data" in names
    ):
        score += 1
    if "Impersonation of an organization" in names and direct_request:
        score += 1
    if "Secrecy or isolation" in names and "Money or payment demand" in names:
        score += 1

    # Without a request for money/data or an intimidating threat, a few
    # isolated signals should not max out the scale.
    serious = {
        "Threats and intimidation", "Money or payment demand",
        "Password, code or personal data", "Suspicious installation or remote access",
    }
    serious_count = len(names & serious)
    if serious_count == 0:
        score = min(score, 4)
    elif serious_count == 1:
        score = min(score, 6)
    elif serious_count == 2:
        score = min(score, 8)

    # In educational / protective messages, detected keywords are quotations
    # or warnings, not demands from the sender. Keep findings but lower risk.
    if educational and not direct_request:
        score = min(score, 2)
    elif educational and "никогда не" in normalized:
        score = min(score, 3)

    score = max(0, min(int(score), 10))
    if score >= 7:
        risk = "Suspicious"
        recommendation = (
            "High risk: do not pay, open links, share codes, or install files. "
            "Contact the organization using its official app or website."
        )
    elif score >= 3:
        risk = "Needs attention"
        recommendation = (
            "Check the sender independently. Avoid unexpected links, "
            "payments, passwords and verification codes."
        )
    else:
        risk = "Low detected risk"
        recommendation = (
            "Few warning signs were found. This does not prove the message is safe. "
            "Verify unexpected requests independently."
        )
    return {"score": score, "risk": risk, "findings": findings, "recommendation": recommendation}


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
                '<mark style="background:#FF8F70;'
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
    st.session_state.nav_choice = page


def nav_changed():
    st.session_state.page = st.session_state.nav_choice


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
        background: #0A111C;
        color: #E6EDF4;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: #E6EDF4;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    section[data-testid="stSidebar"] {
        background: #142333 !important;
        border-right: 1px solid #24364A;
    }

    /* Force sidebar text to stay dark */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {
        color: #E6EDF4;
    }

    section[data-testid="stSidebar"] h1 {
        color: #79C9B0 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #E6EDF4 !important;
        background: transparent;
        border-radius: 10px;
        padding: 9px 10px;
        transition: background 0.15s ease;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
    section[data-testid="stSidebar"] [data-testid="stRadio"] label span {
        color: #E6EDF4 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #1A3442 !important;
    }

    /* Selected navigation item */
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #79C9B0 !important;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] input {
        accent-color: #79C9B0 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        gap: 8px;
    }

    .hero {
        background: linear-gradient(125deg, #101D2C 0%, #142538 55%, #18343B 100%);
        padding: 32px;
        border-radius: 24px;
        border: 1px solid #26394A;
        margin-bottom: 22px;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 12px;
        font-weight: 800;
        color: #79C9B0;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 38px;
        line-height: 1.15;
        font-weight: 800;
        margin: 10px 0;
        color: #E6EDF4;
    }

    .hero-copy {
        color: #B2C7BA;
        font-size: 16px;
        max-width: 720px;
    }

    .soft-card {
        background: white;
        border: 1px solid #26394A;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .soft-card h3 {
        margin-top: 0;
    }

    .metric-card {
        background: white;
        border: 1px solid #26394A;
        border-radius: 18px;
        padding: 20px;
        min-height: 115px;
    }

    .metric-label {
        color: #9BAFC0;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #E6EDF4;
        font-family: 'Manrope', sans-serif;
        font-size: 29px;
        font-weight: 800;
        margin-top: 5px;
    }

    .tag {
        display: inline-block;
        background: #142333;
        color: #B0DED0;
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: 700;
    }

    .stButton > button {
        background: #79C9B0;
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        min-height: 42px;
    }

    .stButton > button:hover {
        background: #67BBA0;
        color: white !important;
        border: none;
    }

    .stTextArea textarea {
        border-radius: 14px;
        border-color: #30495A;
        background: #101D2A;
    }

    div[data-baseweb="select"] > div {
        border-radius: 12px;
    }

    hr {
        border-color: #26394A;
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

    /* QALQAN entrance: staggered drop, white first, then the real theme colors. */
    @keyframes qalqan-drop-color {
        0% { opacity: 0; transform: translateY(-14px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes qalqan-sidebar-in {
        0% { opacity: 0; transform: translateY(-28px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Force the new midnight theme across Streamlit's main canvas and sidebar. */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #0A111C !important;
        color: #E6EDF4 !important;
    }
    [data-testid="stSidebar"] {
        background: #0D1723 !important;
        border-right: 1px solid #26394A !important;
        animation: qalqan-sidebar-in 650ms cubic-bezier(.2,.8,.2,1) both;
    }
    [data-testid="stSidebar"] * { color: #D8E3ED; }
    .block-container { color: #E6EDF4; }
    .block-container [data-testid="stElementContainer"] {
        animation: qalqan-drop-color 650ms cubic-bezier(.2,.8,.2,1) both;
    }
    .block-container [data-testid="stElementContainer"]:nth-of-type(2) { animation-delay: 100ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(3) { animation-delay: 200ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(4) { animation-delay: 300ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(5) { animation-delay: 400ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(6) { animation-delay: 500ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(7) { animation-delay: 600ms; }
    .block-container [data-testid="stElementContainer"]:nth-of-type(8) { animation-delay: 700ms; }
    .hero { animation: qalqan-drop-color 750ms cubic-bezier(.2,.8,.2,1) both; }
    .soft-card, .metric-card {
        background: #101D2A !important;
        border: 1px solid #26394A !important;
        color: #E6EDF4 !important;
        transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
    }
    .soft-card:hover, .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,.16);
        border-color: #79C9B0 !important;
    }
    .hero {
        background: linear-gradient(125deg, #101D2A 0%, #142B3A 55%, #1A3038 100%) !important;
        border: 1px solid #30495A !important;
    }
    .hero-title, .metric-value { color: #E6EDF4 !important; }
    .eyebrow, .tag { color: #B0DED0 !important; }
    .tag { background: #142333 !important; }
    .stButton > button {
        background: #79C9B0 !important;
        color: #09151D !important;
        border: 1px solid #79C9B0 !important;
        border-radius: 12px;
        font-weight: 800;
        transition: transform 200ms ease, box-shadow 200ms ease, background-color 200ms ease;
    }
    .stButton > button:hover {
        background: #B0DED0 !important;
        color: #09151D !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 14px rgba(121,201,176,.12);
    }
    /* Keep every interactive state in the same restrained blue-green palette. */
    .stButton > button:focus,
    .stButton > button:focus-visible,
    .stButton > button:active,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        outline: none !important;
        box-shadow: 0 0 0 1px #79C9B0 !important;
        border-color: #79C9B0 !important;
        background-color: #18303A !important;
        color: #E6EDF4 !important;
    }
    .stButton > button:focus p,
    .stButton > button:active p { color: #E6EDF4 !important; }
    input, textarea, [data-baseweb="select"] * { accent-color: #79C9B0 !important; }

    .stTextArea textarea, .stTextInput input {
        background: #0D1925 !important;
        color: #E6EDF4 !important;
        border-color: #30495A !important;
        border-radius: 14px;
    }
    div[data-baseweb="select"] > div {
        background: #0D1925 !important;
        border-color: #30495A !important;
        border-radius: 12px;
    }
    hr { border-color: #26394A !important; }
    p, label, h1, h2, h3, h4, li { color: #D8E3ED; }
    a { color: #B0DED0 !important; }
    .footer { color: #9BAFC0; font-size: 12px; padding: 28px 0 0; }

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
    st.markdown("**NAVIGATION**")
    for item in PAGES:
        st.button(item, key="side_" + item, on_click=go_to, args=(item,), use_container_width=True)
    st.markdown("---")
    st.markdown("**Creative Lab edition**")
    st.caption("A student prototype for safer digital communication.")

# Always-visible navigation: works even when the Streamlit sidebar is collapsed.
st.caption("🛡️ QALQAN  ·  Navigate between sections")
if "nav_choice" not in st.session_state or st.session_state.nav_choice not in PAGES:
    st.session_state.nav_choice = st.session_state.page
st.radio("Sections", PAGES, key="nav_choice", on_change=nav_changed,
         horizontal=True, label_visibility="collapsed")
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
        st.button("Open analyzer", key="overview_analyzer", use_container_width=True,
                  on_click=go_to, args=("🔎 Analyzer",))

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
        st.button("Open Safety Academy", key="overview_academy", use_container_width=True,
                  on_click=go_to, args=("📚 Safety Academy",))

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
                Paste any message to scan. The examples are only for testing.
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
            with st.spinner("Analyzing with QALQAN rules..."):
                result = analyze_message(message)
                analysis_mode = "Offline risk assessment (no AI or API key needed)"
            st.session_state.analysis_mode = analysis_mode
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
        st.caption(st.session_state.get("analysis_mode", "Rule-based analysis"))

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
            if result.get("ai_reasons"):
                for reason in result["ai_reasons"]:
                    st.markdown("• " + html.escape(reason))
                st.caption("Highlighted phrases below come from rule-based detection.")
            elif result["findings"]:
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
            "AI-assisted when available, otherwise rule-based. The score is a heuristic, "
            "not proof that a message is safe or fraudulent. Do not paste private data."
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
                        <div style="font-size:12px;color:#9BAFC0">{description}</div>
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
        - Analyze pasted text using transparent offline safety rules, without external AI.
        - Explain detected warning signs.
        - Offer basic safety recommendations.
        - Run a labeled test set and display evaluation metrics.
        """
    )

    st.markdown("### Current limitations")
    st.markdown(
        """
        - Offline analysis does not require an API key or internet connection.
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
