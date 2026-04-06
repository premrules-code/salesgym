import pytest
from src.models import Strategy, CustomerPersona, CallOutcome, CallTranscript, Turn


def test_strategy_creation():
    s = Strategy(
        id=1,
        name="The Storyteller",
        system_prompt="You are a warm sales agent...",
        objection_handlers={"price": "Use ROI framing"},
    )
    assert s.id == 1
    assert s.name == "The Storyteller"


def test_customer_persona_creation():
    c = CustomerPersona(
        id="budget_bob",
        name="Budget Bob",
        persona="Small bakery owner. Tight budget.",
        difficulty=1,
    )
    assert c.id == "budget_bob"
    assert c.difficulty == 1


def test_call_outcome_scoring():
    outcome = CallOutcome(
        converted=True,
        turns=4,
        rapport=0.8,
        objections_faced=["price"],
        objection_handled=True,
    )
    assert outcome.fitness_score() > 0


def test_call_outcome_high_score():
    outcome = CallOutcome(converted=True, turns=4, rapport=0.8, objections_faced=["price"], objection_handled=True)
    # 50 (converted) + 24 (0.8*30) + 12 ((10-4)*2) + 10 (handled) = 96
    assert outcome.fitness_score() == 96.0


def test_call_outcome_low_score():
    outcome = CallOutcome(converted=False, turns=2, rapport=0.1, objections_faced=["pushy"], objection_handled=False)
    # 0 + 3 (0.1*30) + 16 ((10-2)*2) + 0 = 19
    assert outcome.fitness_score() == 19.0


def test_call_transcript():
    transcript = CallTranscript(
        strategy_id=1,
        strategy_name="The Storyteller",
        customer_id="budget_bob",
        generation=0,
        turns=[
            Turn(role="agent", text="Hey Bob!"),
            Turn(role="customer", text="What do you want?"),
        ],
        outcome=CallOutcome(
            converted=False, turns=2, rapport=0.3,
            objections_faced=["no_interest"], objection_handled=False,
        ),
    )
    assert len(transcript.turns) == 2
    assert transcript.outcome.converted is False
