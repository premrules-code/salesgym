import asyncio
from src.config import (
    ANTHROPIC_API_KEY, GOOGLE_API_KEY, ELEVENLABS_API_KEY,
    DIFY_API_KEY, DIFY_BASE_URL, DATA_DIR, MAX_TURNS_PER_CALL,
)
from src.models import Strategy, CustomerPersona, CallTranscript, CallOutcome, Turn
from src.customer_simulator import CustomerSimulator
from src.dify_agent import DifyAgent
from src.voice import VoiceGenerator
from src.scoring import score_call, aggregate_generation_scores
from src.analyzer import Analyzer
from src.evolution import EvolutionEngine
from src.memory import MemoryManager


class Arena:
    def __init__(self):
        self.customer_sim = CustomerSimulator(api_key=GOOGLE_API_KEY)
        self.dify = DifyAgent(api_key=DIFY_API_KEY, base_url=DIFY_BASE_URL)
        self.voice = VoiceGenerator(api_key=ELEVENLABS_API_KEY)
        self.analyzer = Analyzer(api_key=ANTHROPIC_API_KEY)
        self.evolution = EvolutionEngine(api_key=ANTHROPIC_API_KEY)
        self.memory = MemoryManager(data_dir=DATA_DIR)

    def _generate_call_pairs(self, strategies, customers) -> list[tuple]:
        return [(s, c) for s in strategies for c in customers]

    async def run_single_call(
        self,
        strategy: Strategy,
        customer: CustomerPersona,
        generation: int,
        improvement_rules: list[str],
    ) -> CallTranscript:
        turns = []
        conversation_id = None
        call_id = f"s{strategy.id}_{customer.id}"

        # Customer initiates (picks up the phone)
        first_message = "Hello? Who's this?"
        turns.append(Turn(role="customer", text=first_message))

        for turn_num in range(MAX_TURNS_PER_CALL):
            # Agent responds via Dify
            last_customer_msg = turns[-1].text if turns[-1].role == "customer" else first_message
            dify_response = await self.dify.send_message(
                message=last_customer_msg,
                strategy_prompt=strategy.system_prompt,
                improvement_rules=improvement_rules,
                conversation_id=conversation_id,
                user=call_id,
            )
            agent_text = dify_response["answer"]
            conversation_id = dify_response["conversation_id"]

            # Generate voice for agent
            try:
                audio_path = await self.voice.generate_audio(
                    text=agent_text, generation=generation,
                    call_id=call_id, turn=turn_num,
                )
            except Exception:
                audio_path = None

            turns.append(Turn(role="agent", text=agent_text, audio_path=audio_path))

            # Check if agent ended the call
            if self.customer_sim._is_conversation_over(agent_text):
                break

            # Customer responds via Gemini
            customer_response = await self.customer_sim.generate_response(customer, turns)
            turns.append(Turn(role="customer", text=customer_response))

            # Check if customer ended the call
            if self.customer_sim._is_conversation_over(customer_response):
                break

        # Determine outcome from final customer message
        last_customer_msg = ""
        for t in reversed(turns):
            if t.role == "customer":
                last_customer_msg = t.text
                break

        converted = self.customer_sim._is_positive_outcome(last_customer_msg)
        objections = self._extract_objections(turns)
        rapport = self._estimate_rapport(turns)

        outcome = CallOutcome(
            converted=converted,
            turns=len(turns),
            rapport=rapport,
            objections_faced=objections,
            objection_handled=converted or rapport > 0.5,
        )

        return CallTranscript(
            strategy_id=strategy.id,
            strategy_name=strategy.name,
            customer_id=customer.id,
            generation=generation,
            turns=turns,
            outcome=outcome,
        )

    def _extract_objections(self, turns: list[Turn]) -> list[str]:
        objections = []
        objection_keywords = {
            "price": ["price", "expensive", "cost", "budget", "afford", "cheap"],
            "already_have_solution": ["already have", "currently use", "dropbox", "existing"],
            "no_time": ["busy", "no time", "gotta go", "in a meeting", "quick"],
            "no_trust": ["don't trust", "scam", "not interested", "who are you"],
        }
        for turn in turns:
            if turn.role == "customer":
                text_lower = turn.text.lower()
                for obj_type, keywords in objection_keywords.items():
                    if any(kw in text_lower for kw in keywords) and obj_type not in objections:
                        objections.append(obj_type)
        return objections

    def _estimate_rapport(self, turns: list[Turn]) -> float:
        if len(turns) < 2:
            return 0.1
        positive_signals = 0
        negative_signals = 0
        for turn in turns:
            if turn.role == "customer":
                text_lower = turn.text.lower()
                if any(w in text_lower for w in ["interesting", "tell me more", "good point", "hmm", "okay", "sure"]):
                    positive_signals += 1
                if any(w in text_lower for w in ["not interested", "goodbye", "stop", "don't call", "pushy"]):
                    negative_signals += 1
        total = positive_signals + negative_signals
        if total == 0:
            return 0.5
        return min(1.0, positive_signals / total)

    async def run_generation(
        self,
        strategies: list[Strategy],
        customers: list[CustomerPersona],
        generation: int,
    ) -> dict:
        improvement_rules = self.memory.get_rules_as_strings()
        pairs = self._generate_call_pairs(strategies, customers)

        # Run all calls (sequentially to avoid API rate limits)
        transcripts = []
        for i, (strategy, customer) in enumerate(pairs):
            print(f"  Running: {strategy.name} vs {customer.name}... ({i+1}/{len(pairs)})")
            transcript = await self.run_single_call(
                strategy, customer, generation, improvement_rules,
            )
            transcripts.append(transcript)
            status = "CONVERTED" if transcript.outcome.converted else "LOST"
            print(f"    → {status} (rapport: {transcript.outcome.rapport:.1f})")
            await asyncio.sleep(1)  # Avoid rate limits

        # Save transcripts
        self.memory.save_transcripts(generation, transcripts)
        self.memory.save_strategies(generation, strategies)

        # Score
        aggregated = aggregate_generation_scores(transcripts)
        self.memory.save_outcomes(generation, aggregated)

        # Analyze with Claude
        print(f"  Analyzing generation {generation} with Claude...")
        analysis = await self.analyzer.analyze(aggregated, transcripts, generation)
        self.memory.add_rules(analysis["rules"])

        # Evolve strategies for next generation
        print(f"  Evolving strategies for generation {generation + 1}...")
        evolved = await self.evolution.evolve(
            strategies, analysis["rankings"], analysis["rules"], generation + 1,
        )

        avg_conversion = sum(1 for t in transcripts if t.outcome.converted) / len(transcripts) if transcripts else 0

        return {
            "generation": generation,
            "transcripts": transcripts,
            "aggregated": aggregated,
            "analysis": analysis,
            "evolved_strategies": evolved,
            "average_conversion": avg_conversion,
        }
