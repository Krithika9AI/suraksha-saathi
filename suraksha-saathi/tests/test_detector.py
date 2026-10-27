import csv
from pathlib import Path

from app.detector import analyze

DATA = Path(__file__).parent.parent / "sample_data" / "sample_messages.csv"


def test_sample_messages_match_expected_level():
    with open(DATA, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            v = analyze(row["text"])
            assert v.level == row["expected_level"], (row["text"], v)


def test_digital_arrest_detected():
    v = analyze("You are under digital arrest, do not tell anyone")
    assert "digital_arrest" in v.scam_types and v.level == "HIGH"


def test_benign_message_is_low():
    assert analyze("Dinner at 8 tonight?").level == "LOW"


def test_advice_is_localised():
    assert "1930" in analyze("share otp", lang="hi").advice
    assert "1930" in analyze("share otp", lang="ta").advice


def test_hindi_and_tamil_scams_are_high():
    hi = analyze("आपको गिरफ्तार किया जाएगा। तुरंत पैसे भेजें और किसी को न बताएं।", lang="hi")
    ta = analyze("உங்களை கைது செய்வோம். உடனடியாக பணம் அனுப்புங்கள். யாரிடமும் சொல்ல வேண்டாம்.", lang="ta")
    assert hi.level == "HIGH" and ta.level == "HIGH"
    assert "गिरफ्तारी" in hi.reasons[0] and "கைது" in ta.reasons[0]


def test_normal_hindi_and_tamil_messages_are_low():
    assert analyze("माँ, मैं शाम 7 बजे तक घर पहुँच जाऊँगा।", lang="hi").level == "LOW"
    assert analyze("அம்மா, நான் மாலை 7 மணிக்கு வீடு வருவேன்.", lang="ta").level == "LOW"


def test_web_page_and_api_work():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200 and "Suraksha Saathi" in page.text
    r = client.post("/analyze", json={"text": "Share OTP to claim your lottery prize money", "lang": "en"})
    assert r.status_code == 200 and r.json()["level"] == "HIGH"


def test_score_is_capped():
    assert analyze("digital arrest kyc update pending share otp you won lottery urgent do not tell http://bit.ly/x").score == 100
