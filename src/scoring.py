from collections import defaultdict
from src.models import CallTranscript


def score_call(transcript: CallTranscript) -> float:
    return transcript.outcome.fitness_score()


def aggregate_generation_scores(transcripts: list[CallTranscript]) -> dict:
    by_strategy = defaultdict(lambda: {"wins": 0, "total": 0, "total_rapport": 0.0, "total_turns": 0})
    by_objection = defaultdict(lambda: {"count": 0, "handled": 0})
    by_customer = defaultdict(lambda: {"wins": 0, "total": 0})

    for t in transcripts:
        s = by_strategy[t.strategy_name]
        s["total"] += 1
        s["total_rapport"] += t.outcome.rapport
        s["total_turns"] += t.outcome.turns
        if t.outcome.converted:
            s["wins"] += 1

        for obj in t.outcome.objections_faced:
            by_objection[obj]["count"] += 1
            if t.outcome.objection_handled:
                by_objection[obj]["handled"] += 1

        c = by_customer[t.customer_id]
        c["total"] += 1
        if t.outcome.converted:
            c["wins"] += 1

    result = {"by_strategy": {}, "by_objection": {}, "by_customer": {}}

    for name, data in by_strategy.items():
        result["by_strategy"][name] = {
            "conversion_rate": data["wins"] / data["total"] if data["total"] > 0 else 0,
            "avg_rapport": data["total_rapport"] / data["total"] if data["total"] > 0 else 0,
            "avg_turns": data["total_turns"] / data["total"] if data["total"] > 0 else 0,
            "wins": data["wins"],
            "total": data["total"],
        }

    for obj, data in by_objection.items():
        result["by_objection"][obj] = {
            "frequency": data["count"],
            "handle_rate": data["handled"] / data["count"] if data["count"] > 0 else 0,
        }

    for cid, data in by_customer.items():
        result["by_customer"][cid] = {
            "conversion_rate": data["wins"] / data["total"] if data["total"] > 0 else 0,
        }

    return result
