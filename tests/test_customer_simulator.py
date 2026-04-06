from src.customer_simulator import CustomerSimulator
from src.models import CustomerPersona, Turn


def test_simulator_builds_prompt():
    sim = CustomerSimulator(api_key="fake-key")
    persona = CustomerPersona(
        id="budget_bob", name="Budget Bob",
        persona="You are Bob, a budget-conscious bakery owner.",
        difficulty=1,
    )
    history = [
        Turn(role="agent", text="Hey Bob! Let me tell you about CloudSync."),
    ]
    prompt = sim._build_customer_prompt(persona, history)
    assert "Bob" in prompt
    assert "budget" in prompt.lower()
    assert "CloudSync" in prompt


def test_simulator_detects_conversation_end_positive():
    sim = CustomerSimulator(api_key="fake-key")
    assert sim._is_conversation_over("Sure, I'll try the free trial!") is True
    assert sim._is_conversation_over("Sounds good, sign me up") is True


def test_simulator_detects_conversation_end_negative():
    sim = CustomerSimulator(api_key="fake-key")
    assert sim._is_conversation_over("No thanks, goodbye.") is True
    assert sim._is_conversation_over("Not interested, bye") is True


def test_simulator_detects_ongoing():
    sim = CustomerSimulator(api_key="fake-key")
    assert sim._is_conversation_over("Tell me more about the pricing.") is False
    assert sim._is_conversation_over("What makes you different from Dropbox?") is False


def test_positive_outcome_detection():
    sim = CustomerSimulator(api_key="fake-key")
    assert sim._is_positive_outcome("Sure, I'll try the free trial!") is True
    assert sim._is_positive_outcome("No thanks, goodbye.") is False
