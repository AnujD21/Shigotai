import pytest

from app.matching.roles import role_relevance
from app.matching.skill_taxonomy import canonical_skill_name, find_skills


@pytest.mark.parametrize(
    "text",
    [
        "Partner with our Go To Market team",
        "Shape the Go-To-Market strategy",
        "Make Go/No-Go decisions",
        "Go onsite and meet customers",
        "Grow digital revenue and build trust with Google",
    ],
)
def test_everyday_words_are_not_skills(text):
    assert find_skills(text) == []


@pytest.mark.parametrize(
    ("text", "skill"),
    [
        ("Python or Go, CI/CD", "Go"),
        ("Java、Python、Ruby、Go、Node.JS", "Go"),
        ("PythonやGoなど", "Go"),
        ("Golang microservices", "Go"),
        ("experience with K8s", "Kubernetes"),
        ("C++ and C# required", "C#"),
    ],
)
def test_skills_found_in_english_and_japanese_text(text, skill):
    assert skill in find_skills(text)


def test_java_is_not_found_inside_javascript():
    assert find_skills("Strong JavaScript skills") == ["JavaScript"]


def test_canonical_skill_name_resolves_aliases_and_casing():
    assert canonical_skill_name("pytorch") == "PyTorch"
    assert canonical_skill_name("Golang") == "Go"
    assert canonical_skill_name("  Some Niche Tool ") == "Some Niche Tool"


def test_role_relevance_is_none_without_desired_roles():
    assert role_relevance("Backend Engineer", []) is None


def test_role_relevance_ranks_the_right_kind_of_role():
    wanted = ["Computer Vision Engineer", "Machine Learning Engineer"]
    assert role_relevance("Senior Computer Vision Engineer", wanted) == 1.0
    assert role_relevance("ML Engineer, Perception", wanted) == 1.0
    # Same family (engineering) but a different specialty: some credit.
    assert 0.3 <= role_relevance("Site Reliability Engineer", wanted) < 0.6
    # A different kind of job altogether.
    assert role_relevance("Account Executive, Enterprise", wanted) == 0.0
    assert role_relevance("Internship at Packaging Design Logistics", wanted) == 0.0


def test_role_relevance_understands_japanese_titles():
    assert role_relevance("機械学習エンジニア", ["Machine Learning Engineer"]) == 1.0
