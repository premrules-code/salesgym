from google import genai
from src.models import CustomerPersona, Turn


class CustomerSimulator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key) if api_key and api_key != "fake-key" else None
        self.model = "gemini-2.0-flash"

    def _build_customer_prompt(self, persona: CustomerPersona, history: list[Turn]) -> str:
        evolved = ""
        if persona.evolved_objections:
            evolved = "\n\nADDITIONAL OBJECTIONS (use these naturally during the conversation):\n"
            evolved += "\n".join(f"- {obj}" for obj in persona.evolved_objections)

        conversation = "\n".join(
            f"{'Sales Agent' if t.role == 'agent' else 'You'}: {t.text}"
            for t in history
        )

        return f"""You are role-playing as a customer receiving a sales call.

YOUR CHARACTER:
{persona.persona}
{evolved}

CONVERSATION SO FAR:
{conversation}

INSTRUCTIONS:
- Stay in character as {persona.name}
- Respond naturally in 1-3 sentences
- If you're convinced, say something like "OK, I'll try it" or "Sign me up for the trial"
- If you want to end the call negatively, say "No thanks, goodbye" or "Not interested, bye"
- Don't break character or mention you're an AI
- Be realistic — real customers aren't always polite

YOUR RESPONSE AS {persona.name}:"""

    def _is_conversation_over(self, response: str) -> bool:
        response_lower = response.lower()
        positive_endings = [
            "i'll try", "sign me up", "free trial", "let's do it",
            "sounds good", "i'm in", "send me", "set me up",
        ]
        negative_endings = [
            "goodbye", "bye", "not interested", "don't call",
            "no thanks", "stop calling", "hang up",
        ]
        for ending in positive_endings + negative_endings:
            if ending in response_lower:
                return True
        return False

    def _is_positive_outcome(self, response: str) -> bool:
        response_lower = response.lower()
        positive = [
            "i'll try", "sign me up", "free trial", "let's do it",
            "sounds good", "i'm in", "send me", "set me up",
            "sure", "ok let's", "okay let", "why not", "i'll give it",
        ]
        return any(p in response_lower for p in positive)

    async def generate_response(self, persona: CustomerPersona, history: list[Turn]) -> str:
        prompt = self._build_customer_prompt(persona, history)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text.strip()
