from app.guardrails import check_message


def test_normal_question_allowed():
    assert check_message("How do I build credit as a college student?").allowed


def test_specific_stock_blocked():
    r = check_message("Should I buy Tesla stock right now?")
    assert not r.allowed and r.category == "specific_security"


def test_ssn_blocked():
    assert check_message("my ssn is 123-45-6789").category == "sensitive_data"


def test_crisis_checked_first():
    r = check_message("I'm so broke I want to end my life")
    assert r.category == "crisis" and "988" in r.message
