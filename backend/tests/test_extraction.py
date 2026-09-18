from app.ai.dev_provider import DevLLMProvider

provider = DevLLMProvider()


def test_extracts_explicit_jlpt_level_from_japanese_text():
    result = provider.extract_requirements("AI Engineer", "日本語能力N2以上が必要です。Python required.", "mixed")
    assert result["jlpt_requirement"] == "N2"


def test_does_not_invent_jlpt_when_only_business_japanese_mentioned():
    result = provider.extract_requirements(
        "AI Engineer", "Business-level Japanese communication required. Python required.", "en"
    )
    assert result["jlpt_requirement"] is None
    assert "Business-level Japanese" in result["japanese_requirement"]


def test_visa_sponsorship_defaults_to_not_stated():
    result = provider.extract_requirements("Engineer", "Python required. 3+ years of experience.", "en")
    assert result["visa_sponsorship"] == "NOT_STATED"


def test_visa_sponsorship_detected_when_explicitly_offered():
    result = provider.extract_requirements("Engineer", "Visa sponsorship available for qualified candidates.", "en")
    assert result["visa_sponsorship"] == "YES"


def test_visa_sponsorship_detected_when_explicitly_declined():
    result = provider.extract_requirements("Engineer", "No visa sponsorship is available for this role.", "en")
    assert result["visa_sponsorship"] == "NO"


def test_required_vs_preferred_skill_split():
    description = "Required: Python, Docker. Preferred: AWS, Kubernetes."
    result = provider.extract_requirements("Engineer", description, "en")
    assert "Python" in result["required_skills"]
    assert "Docker" in result["required_skills"]
    assert "AWS" in result["preferred_skills"]
    assert "AWS" not in result["required_skills"]


def test_new_graduate_positive_signal():
    result = provider.extract_requirements("Engineer", "New graduates are welcome to apply. Python required.", "en")
    assert result["new_graduate_allowed"] is True


def test_new_graduate_negative_signal():
    result = provider.extract_requirements("Engineer", "Experienced candidates only. Python required.", "en")
    assert result["new_graduate_allowed"] is False


def test_no_signal_leaves_new_graduate_unknown():
    result = provider.extract_requirements("Engineer", "Python required. 2+ years of experience.", "en")
    assert result["new_graduate_allowed"] is None


def test_minimum_experience_years_extracted():
    result = provider.extract_requirements("Engineer", "5+ years of experience with Python required.", "en")
    assert result["minimum_experience"] == 5.0
