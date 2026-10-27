"""Rule-based scam detector (baseline). An ML classifier can be plugged in via `ml_score`."""
import re
from dataclasses import dataclass, field

# Each rule: (scam_type, weight, regex). Covers English, Hindi and Tamil cues.
RULES = [
    ("digital_arrest", 45, r"digital arrest|cbi|narcotics|customs officer|arrest warrant|गिरफ्तार|கைது"),
    ("kyc_fraud", 35, r"kyc (update|expire|pending)|account (will be )?(blocked|suspended)|केवाईसी|கேஒய்சி"),
    ("otp_theft", 40, r"share (your )?otp|otp (is )?required|ओटीपी बताएं|ஓடிபி"),
    ("upi_collect", 35, r"collect request|approve (the )?request|enter (your )?upi pin|यूपीआई पिन"),
    ("lottery_prize", 35, r"you (have )?won|lottery|lucky draw|prize money|इनाम|பரிசு"),
    ("job_task_scam", 30, r"work from home.*(earn|per day)|like (and )?subscribe.*earn|telegram.*task"),
    ("urgency", 15, r"immediately|within \d+ (minutes|hours)|urgent|last chance|तुरंत|உடனடியாக"),
    ("secrecy", 20, r"do not tell|don't tell|keep this secret|किसी को न बताएं|யாரிடமும் சொல்ல"),
]
URL_RE = re.compile(r"https?://[^\s]+|\b[\w-]+\.(?:xyz|top|click|link|info)\b", re.I)
SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "cutt.ly")

# Plain-language reasons shown to the user, per language.
REASONS = {
    "digital_arrest": {
        "en": "Threatens arrest or claims to be police or CBI",
        "hi": "गिरफ्तारी की धमकी या पुलिस/CBI होने का दावा",
        "ta": "கைது செய்வோம் என மிரட்டுகிறது அல்லது போலீஸ்/CBI என கூறுகிறது",
    },
    "kyc_fraud": {
        "en": "Fake KYC or account-block warning",
        "hi": "फर्जी KYC या खाता बंद होने की चेतावनी",
        "ta": "போலி KYC அல்லது கணக்கு முடக்க எச்சரிக்கை",
    },
    "otp_theft": {
        "en": "Asks you to share an OTP",
        "hi": "OTP साझा करने को कहता है",
        "ta": "OTP பகிரச் சொல்கிறது",
    },
    "upi_collect": {
        "en": "Asks you to approve a UPI request or enter your PIN",
        "hi": "UPI अनुरोध स्वीकार करने या PIN डालने को कहता है",
        "ta": "UPI கோரிக்கையை ஏற்க அல்லது PIN உள்ளிடச் சொல்கிறது",
    },
    "lottery_prize": {
        "en": "Promises a prize or lottery win",
        "hi": "इनाम या लॉटरी जीतने का झांसा",
        "ta": "பரிசு அல்லது லாட்டரி வெற்றி என ஆசை காட்டுகிறது",
    },
    "job_task_scam": {
        "en": "Offers easy money for simple online tasks",
        "hi": "आसान ऑनलाइन काम के बदले कमाई का लालच",
        "ta": "எளிய ஆன்லைன் வேலைக்கு எளிதான பணம் என ஆசை காட்டுகிறது",
    },
    "urgency": {
        "en": "Pushes you to act immediately",
        "hi": "तुरंत कदम उठाने का दबाव",
        "ta": "உடனே செயல்பட அவசரப்படுத்துகிறது",
    },
    "secrecy": {
        "en": "Asks you to keep it secret",
        "hi": "किसी को न बताने को कहता है",
        "ta": "யாரிடமும் சொல்ல வேண்டாம் என்கிறது",
    },
    "link": {
        "en": "Contains a suspicious or unverified link",
        "hi": "संदिग्ध या अज्ञात लिंक है",
        "ta": "சந்தேகத்திற்குரிய இணைப்பு உள்ளது",
    },
}

ADVICE = {
    "en": "Do NOT pay, share OTP/PIN or click links. Call 1930 or report at cybercrime.gov.in. Talk to a family member first.",
    "hi": "पैसे न भेजें, OTP/PIN या लिंक साझा न करें। 1930 पर कॉल करें या cybercrime.gov.in पर शिकायत करें।",
    "ta": "பணம் செலுத்தாதீர்கள், OTP/PIN பகிராதீர்கள். 1930 ஐ அழையுங்கள் அல்லது cybercrime.gov.in இல் புகாரளியுங்கள்.",
}


@dataclass
class Verdict:
    score: int
    level: str
    scam_types: list = field(default_factory=list)
    reasons: list = field(default_factory=list)
    advice: str = ""


def _reason(key: str, lang: str) -> str:
    return REASONS[key].get(lang, REASONS[key]["en"])


def analyze(text: str, lang: str = "en", ml_score: int = 0) -> Verdict:
    t = text.lower()
    score, types, reasons = ml_score, [], []
    for scam_type, weight, pattern in RULES:
        if re.search(pattern, t, re.I):
            score += weight
            if scam_type not in ("urgency", "secrecy"):
                types.append(scam_type)
            reasons.append(_reason(scam_type, lang))
    for url in URL_RE.findall(t):
        score += 25 if any(s in url for s in SHORTENERS) or url.endswith(("xyz", "top", "click", "link")) else 10
        reasons.append(_reason("link", lang))
        break
    score = min(score, 100)
    level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
    return Verdict(score, level, types, reasons, ADVICE.get(lang, ADVICE["en"]))
