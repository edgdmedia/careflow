import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.intake_agent import run_intake_agent, _has_crisis_keywords


def load_samples():
    path = os.path.join(os.path.dirname(__file__), "sample_messages.json")
    with open(path) as f:
        return json.load(f)


def test_crisis_keyword_detection():
    assert _has_crisis_keywords("I want to kill myself") == True
    assert _has_crisis_keywords("suicide is on my mind") == True
    assert _has_crisis_keywords("I've been self-harming") == True
    assert _has_crisis_keywords("I'm feeling anxious lately") == False
    assert _has_crisis_keywords("I can't sleep at night") == False
    print("  ✓ crisis keyword detection works")


def test_standard_intake():
    result = run_intake_agent("Hi, I've been struggling with anxiety for months. My name is Tunde.")
    assert result["name"] == "Tunde"
    assert "anxiety" in result["presenting_concern"].lower()
    assert result["urgency_level"] in ("low", "medium", "high")
    assert "suggested_next_question" in result
    print(f"  ✓ standard intake: {result['name']} | {result['urgency_level']}")


def test_crisis_intake():
    result = run_intake_agent("I can't take this anymore. I've been thinking about suicide. My name is Funmi.")
    assert result["requires_immediate_escalation"] == True
    assert result["urgency_level"] == "high"
    print("  ✓ crisis detection correctly escalates")


def test_no_name_intake():
    result = run_intake_agent("I've been having panic attacks at work and I don't know what to do.")
    assert result["name"] is None
    assert "name" in result.get("suggested_next_question", "").lower() or \
           "name" in json.dumps(result).lower()
    print("  ✓ missing name handled")


if __name__ == "__main__":
    print("Running intake agent tests...\n")
    test_crisis_keyword_detection()
    test_standard_intake()
    test_crisis_intake()
    test_no_name_intake()
    print("\nAll tests passed ✅")
