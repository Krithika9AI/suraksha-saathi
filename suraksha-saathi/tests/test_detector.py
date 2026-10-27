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


def test_score_is_capped():
    assert analyze("digital arrest kyc update pending share otp you won lottery urgent do not tell http://bit.ly/x").score == 100
