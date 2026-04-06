import json
import anthropic
from src.models import ImprovementRule, CallTranscript


class Analyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key) if api_key and api_key != "fake-key" else None

    def _rank_strategies(self, strategy_data: dict) -> list[dict]:
        ranked = sorted(
            strategy_data.items(),
            key=lambda x: x[1].get("conversion_rate", 0),
            reverse=True,
        )
        total = len(ranked)
        result = []
        for i, (name, data) in enumerate(ranked):
            if i < max(1, int(total * 0.375)):  # Top ~3 of 8
                action = "KEEP"
            elif i < max(2, int(total * 0.75)):  # Middle ~3 of 8
                action = "MUTATE"
            else:  # Bottom ~2 of 8
                action = "REPLACE"
            result.append({"rank": i + 1, "name": name, "action": action, **data})
        return result

    def _build_analysis_prompt(self, aggregated: dict, sample_transcripts: list) -> str:
        strategy_summary = json.dumps(aggregated.get("by_strategy", {}), indent=2)
        objection_summary = json.dumps(aggregated.get("by_objection", {}), indent=2)

        transcript_text = ""
        for t in sample_transcripts[:6]:
            turns = "\n".join(f"  {turn.role}: {turn.text}" for turn in t.turns)
            transcript_text += f"\n--- Call: {t.strategy_name} vs {t.customer_id} (converted: {t.outcome.converted}) ---\n{turns}\n"

        return f"""You are analyzing sales call data to find patterns and generate improvement rules.

STRATEGY PERFORMANCE:
{strategy_summary}

OBJECTION PATTERNS:
{objection_summary}

SAMPLE TRANSCRIPTS:
{transcript_text}

TASK:
1. Identify 2-4 specific improvement rules. Each rule must have:
   - trigger: what situation activates this rule
   - old_response: what the failing agents did
   - new_response: what the successful agents did (or what SHOULD be done)
   - evidence: specific data from the calls supporting this rule

2. Provide a brief strategic insight (2-3 sentences).

Respond in this exact JSON format:
{{
  "rules": [
    {{
      "trigger": "customer mentions price or budget",
      "old_response": "description of what failed",
      "new_response": "description of what should be done instead",
      "evidence": "specific numbers and examples"
    }}
  ],
  "strategic_insight": "2-3 sentence summary of key findings"
}}"""

    async def analyze(
        self, aggregated: dict, transcripts: list[CallTranscript], generation: int
    ) -> dict:
        prompt = self._build_analysis_prompt(aggregated, transcripts)
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text

        # Extract JSON from response
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            data = json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError):
            data = {"rules": [], "strategic_insight": "Analysis failed to parse."}

        rules = []
        for i, rule in enumerate(data.get("rules", [])):
            rules.append(ImprovementRule(
                id=generation * 10 + i + 1,
                trigger=rule.get("trigger", ""),
                old_response=rule.get("old_response", ""),
                new_response=rule.get("new_response", ""),
                evidence=rule.get("evidence", ""),
                generation_learned=generation,
            ))

        rankings = self._rank_strategies(aggregated.get("by_strategy", {}))

        return {
            "rules": rules,
            "rankings": rankings,
            "strategic_insight": data.get("strategic_insight", ""),
        }
