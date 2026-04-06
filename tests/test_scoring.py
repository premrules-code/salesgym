from src.scoring import score_call, aggregate_generation_scores
from src.models import CallTranscript, CallOutcome, Turn


def test_score_call_converted():
    transcript = CallTranscript(
        strategy_id=1, strategy_name="Test", customer_id="bob",
        generation=0,
        turns=[
            Turn(role="agent", text="Hey!"),
            Turn(role="customer", text="Tell me more"),
            Turn(role="agent", text="It's $9/month"),
            Turn(role="customer", text="Sure, I'll try the free trial!"),
        ],
        outcome=CallOutcome(
            converted=True, turns=4, rapport=0.8,
            objections_faced=["price"], objection_handled=True,
        ),
    )
    score = score_call(transcript)
    assert score > 70


def test_score_call_lost():
    transcript = CallTranscript(
        strategy_id=2, strategy_name="Test2", customer_id="bob",
        generation=0,
        turns=[
            Turn(role="agent", text="BUY NOW!"),
            Turn(role="customer", text="No thanks, goodbye."),
        ],
        outcome=CallOutcome(
            converted=False, turns=2, rapport=0.1,
            objections_faced=["pushy"], objection_handled=False,
        ),
    )
    score = score_call(transcript)
    assert score < 30


def test_aggregate_scores():
    transcripts = [
        CallTranscript(
            strategy_id=1, strategy_name="A", customer_id="bob", generation=0,
            turns=[Turn(role="agent", text="Hi")],
            outcome=CallOutcome(converted=True, turns=3, rapport=0.8, objections_faced=[], objection_handled=True),
        ),
        CallTranscript(
            strategy_id=1, strategy_name="A", customer_id="sarah", generation=0,
            turns=[Turn(role="agent", text="Hi")],
            outcome=CallOutcome(converted=False, turns=5, rapport=0.4, objections_faced=["price"], objection_handled=False),
        ),
    ]
    agg = aggregate_generation_scores(transcripts)
    assert "A" in agg["by_strategy"]
    assert agg["by_strategy"]["A"]["conversion_rate"] == 0.5
    assert "price" in agg["by_objection"]
