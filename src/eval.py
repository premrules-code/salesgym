"""
SalesGym Evaluation Suite

Runs 3 types of evaluations:
1. Conversion metrics - did conversion improve?
2. Strategy quality - are responses actually persuasive?
3. Rule quality - are improvement rules evidence-backed?
"""
import json
import os
from src.config import DATA_DIR
from src.memory import MemoryManager


def run_conversion_eval(memory: MemoryManager) -> dict:
    """Eval 1: Check if conversion improved gen-over-gen."""
    conversions = []
    gen = 0
    while True:
        transcripts = memory.load_transcripts(gen)
        if not transcripts:
            break
        rate = sum(1 for t in transcripts if t.outcome.converted) / len(transcripts)
        conversions.append({"generation": gen, "conversion_rate": rate, "total_calls": len(transcripts)})
        gen += 1

    if len(conversions) < 2:
        return {"pass": False, "reason": "Not enough generations", "data": conversions}

    improving = conversions[-1]["conversion_rate"] > conversions[0]["conversion_rate"]
    return {
        "pass": improving,
        "improvement": conversions[-1]["conversion_rate"] - conversions[0]["conversion_rate"],
        "data": conversions,
    }


def run_rule_quality_eval(memory: MemoryManager) -> dict:
    """Eval 2: Check if improvement rules are evidence-backed."""
    rules = memory.load_rules()
    if not rules:
        return {"pass": False, "reason": "No rules generated"}

    rules_with_evidence = sum(1 for r in rules if r.evidence and len(r.evidence) > 10)
    quality_rate = rules_with_evidence / len(rules)
    return {
        "pass": quality_rate >= 0.5,
        "total_rules": len(rules),
        "rules_with_evidence": rules_with_evidence,
        "quality_rate": quality_rate,
    }


def run_adversarial_eval(memory: MemoryManager) -> dict:
    """Eval 3: Can evolved agent beat easy customers?"""
    gen0_transcripts = memory.load_transcripts(0)
    last_gen = 0
    while memory.load_transcripts(last_gen + 1):
        last_gen += 1
    final_transcripts = memory.load_transcripts(last_gen)

    if not gen0_transcripts or not final_transcripts:
        return {"pass": False, "reason": "Not enough data"}

    gen0_conversion = sum(1 for t in gen0_transcripts if t.outcome.converted) / len(gen0_transcripts)
    final_conversion = sum(1 for t in final_transcripts if t.outcome.converted) / len(final_transcripts)

    return {
        "pass": final_conversion > gen0_conversion,
        "gen0_conversion": gen0_conversion,
        "final_conversion": final_conversion,
        "improvement": final_conversion - gen0_conversion,
    }


def run_full_eval() -> dict:
    memory = MemoryManager(data_dir=DATA_DIR)
    results = {
        "conversion_eval": run_conversion_eval(memory),
        "rule_quality_eval": run_rule_quality_eval(memory),
        "adversarial_eval": run_adversarial_eval(memory),
    }
    results["overall_pass"] = all(r.get("pass", False) for r in results.values())
    memory.save_eval_report(results)
    return results


if __name__ == "__main__":
    results = run_full_eval()
    print(json.dumps(results, indent=2))
