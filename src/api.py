import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import DATA_DIR
from src.seed_data import get_initial_strategies, get_customer_personas
from src.arena import Arena
from src.memory import MemoryManager
from src.models import CallTranscript

app = FastAPI(title="SalesGym API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

memory = MemoryManager(data_dir=DATA_DIR)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "salesgym"}


@app.get("/api/strategies")
def get_strategies(generation: int = 0):
    if generation == 0:
        strategies = get_initial_strategies()
    else:
        strategies = memory.load_strategies(generation)
        if not strategies:
            raise HTTPException(404, f"No strategies for generation {generation}")
    return [s.model_dump() for s in strategies]


@app.get("/api/customers")
def get_customers(difficulty: int = 1):
    return [c.model_dump() for c in get_customer_personas(difficulty)]


@app.get("/api/rules")
def get_rules():
    return [r.model_dump() for r in memory.load_rules()]


@app.get("/api/memory")
def get_memory():
    rules = memory.load_rules()
    return {
        "total_rules": len(rules),
        "rules": [r.model_dump() for r in rules],
        "rules_as_strings": memory.get_rules_as_strings(),
    }


class ScoreRequest(BaseModel):
    transcripts: list[dict]


@app.post("/api/score")
def score_calls(request: ScoreRequest):
    from src.scoring import aggregate_generation_scores
    transcripts = [CallTranscript(**t) for t in request.transcripts]
    return aggregate_generation_scores(transcripts)


class RunGenerationRequest(BaseModel):
    generation: int = 0
    num_generations: int = 3


@app.post("/api/run")
async def run_evolution(request: RunGenerationRequest):
    """Run the full evolution loop for N generations."""
    arena = Arena()
    strategies = get_initial_strategies()
    results = []

    for gen in range(request.num_generations):
        print(f"\n{'='*60}")
        print(f"GENERATION {gen}")
        print(f"{'='*60}")

        difficulty = gen + 1
        customers = get_customer_personas(difficulty=difficulty)
        result = await arena.run_generation(strategies, customers, gen)

        gen_summary = {
            "generation": gen,
            "average_conversion": result["average_conversion"],
            "best_strategy": result["analysis"]["rankings"][0]["name"] if result["analysis"]["rankings"] else "N/A",
            "rules_learned": len(result["analysis"]["rules"]),
            "strategic_insight": result["analysis"].get("strategic_insight", ""),
            "num_calls": len(result["transcripts"]),
        }
        results.append(gen_summary)

        print(f"\n  Gen {gen} Summary:")
        print(f"    Conversion: {result['average_conversion']:.0%}")
        print(f"    Best: {gen_summary['best_strategy']}")
        print(f"    Rules learned: {gen_summary['rules_learned']}")

        strategies = result["evolved_strategies"]

    # Build eval report
    eval_report = _build_eval_report(results)
    memory.save_eval_report(eval_report)

    return {"results": results, "eval_report": eval_report}


def _build_eval_report(results: list[dict]) -> dict:
    conversions = [r["average_conversion"] for r in results]
    improving = all(conversions[i] <= conversions[i + 1] for i in range(len(conversions) - 1)) if len(conversions) >= 2 else False
    return {
        "conversion_trend": conversions,
        "improving": improving,
        "total_rules_learned": sum(r["rules_learned"] for r in results),
        "initial_conversion": conversions[0] if conversions else 0,
        "final_conversion": conversions[-1] if conversions else 0,
        "improvement": conversions[-1] - conversions[0] if len(conversions) >= 2 else 0,
    }


@app.get("/api/results")
def get_results():
    """Get all generation results for the dashboard."""
    all_results = []
    gen = 0
    while True:
        transcripts = memory.load_transcripts(gen)
        if not transcripts:
            break
        conversion = sum(1 for t in transcripts if t.outcome.converted) / len(transcripts)
        all_results.append({
            "generation": gen,
            "num_calls": len(transcripts),
            "conversion_rate": conversion,
            "transcripts": [t.model_dump() for t in transcripts],
        })
        gen += 1
    return all_results


@app.get("/api/eval")
def get_eval_report():
    import os
    path = os.path.join(DATA_DIR, "evals", "report.json")
    if not os.path.exists(path):
        raise HTTPException(404, "No eval report yet. Run /api/run first.")
    with open(path) as f:
        return json.load(f)
