from pydantic import BaseModel


class Turn(BaseModel):
    role: str  # "agent" or "customer"
    text: str
    audio_path: str | None = None


class CallOutcome(BaseModel):
    converted: bool
    turns: int
    rapport: float  # 0.0 to 1.0
    objections_faced: list[str]
    objection_handled: bool

    def fitness_score(self) -> float:
        score = 0.0
        if self.converted:
            score += 50
        score += self.rapport * 30
        score += max(0, (10 - self.turns)) * 2  # fewer turns = better
        if self.objection_handled:
            score += 10
        return score


class Strategy(BaseModel):
    id: int
    name: str
    system_prompt: str
    objection_handlers: dict[str, str] = {}
    generation: int = 0
    parent_ids: list[int] = []
    mutation_applied: str | None = None


class CustomerPersona(BaseModel):
    id: str
    name: str
    persona: str
    difficulty: int = 1  # 1 = easy, increases each generation
    evolved_objections: list[str] = []


class CallTranscript(BaseModel):
    strategy_id: int
    strategy_name: str
    customer_id: str
    generation: int
    turns: list[Turn]
    outcome: CallOutcome


class ImprovementRule(BaseModel):
    id: int
    trigger: str
    old_response: str
    new_response: str
    evidence: str
    generation_learned: int
    success_rate: float = 0.0


class GenerationResult(BaseModel):
    generation: int
    transcripts: list[CallTranscript]
    average_conversion: float
    best_strategy: str
    worst_strategy: str
    rules_learned: list[ImprovementRule]
    strategy_rankings: list[dict]
