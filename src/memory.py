import json
import os
from src.models import CallTranscript, ImprovementRule, Strategy


class MemoryManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.conversations_dir = os.path.join(data_dir, "conversations")
        self.memory_dir = os.path.join(data_dir, "memory")
        self.strategies_dir = os.path.join(data_dir, "strategies")
        self.evals_dir = os.path.join(data_dir, "evals")
        for d in [self.conversations_dir, self.memory_dir, self.strategies_dir, self.evals_dir]:
            os.makedirs(d, exist_ok=True)

    def save_transcripts(self, generation: int, transcripts: list[CallTranscript]):
        gen_dir = os.path.join(self.conversations_dir, f"gen_{generation}")
        os.makedirs(gen_dir, exist_ok=True)
        data = [t.model_dump() for t in transcripts]
        with open(os.path.join(gen_dir, "transcripts.json"), "w") as f:
            json.dump(data, f, indent=2)

    def load_transcripts(self, generation: int) -> list[CallTranscript]:
        path = os.path.join(self.conversations_dir, f"gen_{generation}", "transcripts.json")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            data = json.load(f)
        return [CallTranscript(**t) for t in data]

    def save_rules(self, rules: list[ImprovementRule]):
        data = [r.model_dump() for r in rules]
        with open(os.path.join(self.memory_dir, "rules.json"), "w") as f:
            json.dump(data, f, indent=2)

    def load_rules(self) -> list[ImprovementRule]:
        path = os.path.join(self.memory_dir, "rules.json")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            data = json.load(f)
        return [ImprovementRule(**r) for r in data]

    def add_rules(self, new_rules: list[ImprovementRule]):
        existing = self.load_rules()
        existing.extend(new_rules)
        self.save_rules(existing)

    def save_outcomes(self, generation: int, aggregated: dict):
        path = os.path.join(self.memory_dir, "outcomes.json")
        all_outcomes = {}
        if os.path.exists(path):
            with open(path) as f:
                all_outcomes = json.load(f)
        all_outcomes[f"gen_{generation}"] = aggregated
        with open(path, "w") as f:
            json.dump(all_outcomes, f, indent=2)

    def save_strategies(self, generation: int, strategies: list[Strategy]):
        data = [s.model_dump() for s in strategies]
        with open(os.path.join(self.strategies_dir, f"gen_{generation}.json"), "w") as f:
            json.dump(data, f, indent=2)

    def load_strategies(self, generation: int) -> list[Strategy]:
        path = os.path.join(self.strategies_dir, f"gen_{generation}.json")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            data = json.load(f)
        return [Strategy(**s) for s in data]

    def save_eval_report(self, report: dict):
        with open(os.path.join(self.evals_dir, "report.json"), "w") as f:
            json.dump(report, f, indent=2)

    def get_rules_as_strings(self) -> list[str]:
        rules = self.load_rules()
        return [f"When {r.trigger}: {r.new_response} (evidence: {r.evidence})" for r in rules]
