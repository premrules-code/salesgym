import json
import anthropic
from src.models import Strategy, ImprovementRule


class EvolutionEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if api_key and api_key != "fake-key" else None

    def _classify(self, rankings: list[dict]) -> tuple[list, list, list]:
        keep = [r for r in rankings if r["action"] == "KEEP"]
        mutate = [r for r in rankings if r["action"] == "MUTATE"]
        replace = [r for r in rankings if r["action"] == "REPLACE"]
        return keep, mutate, replace

    def _build_mutation_prompt(self, strategy: Strategy, rules: list[ImprovementRule]) -> str:
        rules_text = "\n".join(
            f"- When {r.trigger}: instead of '{r.old_response}', do '{r.new_response}' (evidence: {r.evidence})"
            for r in rules
        )
        return f"""You are evolving a sales strategy by applying improvement rules.

CURRENT STRATEGY:
Name: {strategy.name}
System Prompt: {strategy.system_prompt}

IMPROVEMENT RULES TO APPLY:
{rules_text}

TASK: Rewrite the system prompt to incorporate these rules naturally. Keep the strategy's core personality but make it smarter based on the evidence. Return ONLY the new system prompt text, nothing else."""

    def _build_crossover_prompt(self, parent_a: Strategy, parent_b: Strategy) -> str:
        return f"""You are creating a new sales strategy by combining the best elements of two successful strategies.

PARENT A (higher performing):
Name: {parent_a.name}
Prompt: {parent_a.system_prompt}

PARENT B:
Name: {parent_b.name}
Prompt: {parent_b.system_prompt}

TASK: Create a new strategy that combines the opening style of Parent A with the conversation approach of Parent B. Return ONLY the new system prompt text, nothing else."""

    async def evolve(
        self,
        strategies: list[Strategy],
        rankings: list[dict],
        rules: list[ImprovementRule],
        generation: int,
    ) -> list[Strategy]:
        keep, mutate, replace = self._classify(rankings)
        name_to_strategy = {s.name: s for s in strategies}
        new_strategies = []
        next_id = max(s.id for s in strategies) + 1

        # Keep top strategies unchanged
        for r in keep:
            if r["name"] in name_to_strategy:
                s = name_to_strategy[r["name"]]
                new_strategies.append(s.model_copy(update={"generation": generation}))

        # Mutate middle strategies
        for r in mutate:
            if r["name"] not in name_to_strategy:
                continue
            s = name_to_strategy[r["name"]]
            prompt = self._build_mutation_prompt(s, rules)
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            new_prompt = response.content[0].text.strip()
            new_strategies.append(Strategy(
                id=s.id,
                name=f"{s.name} v{generation}",
                system_prompt=new_prompt,
                objection_handlers=s.objection_handlers,
                generation=generation,
                parent_ids=[s.id],
                mutation_applied=f"Applied {len(rules)} improvement rules from gen {generation - 1}",
            ))

        # Replace bottom strategies with crossovers of top performers
        top_strategies = [name_to_strategy[r["name"]] for r in keep if r["name"] in name_to_strategy]
        if not top_strategies:
            top_strategies = strategies[:2]

        for i, r in enumerate(replace):
            parent_a = top_strategies[i % len(top_strategies)]
            parent_b = top_strategies[(i + 1) % len(top_strategies)]
            prompt = self._build_crossover_prompt(parent_a, parent_b)
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            new_prompt = response.content[0].text.strip()
            new_strategies.append(Strategy(
                id=next_id,
                name=f"{parent_a.name}-{parent_b.name} Hybrid",
                system_prompt=new_prompt,
                generation=generation,
                parent_ids=[parent_a.id, parent_b.id],
                mutation_applied=f"Crossover of {parent_a.name} + {parent_b.name}",
            ))
            next_id += 1

        return new_strategies
