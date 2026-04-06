import asyncio
import httpx


class DifyAgent:
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=120.0)

    def _format_rules(self, rules: list[str]) -> str:
        if not rules:
            return "No rules yet — this is the first generation."
        return "\n".join(f"- {rule}" for rule in rules)

    def _build_inputs(self, strategy_prompt: str, improvement_rules: list[str]) -> dict:
        rules_text = self._format_rules(improvement_rules)
        combined = f"""{strategy_prompt}

IMPROVEMENT RULES FROM PAST CALLS (follow these!):
{rules_text}"""
        return {"system_prompt": combined}

    async def send_message(
        self,
        message: str,
        strategy_prompt: str,
        improvement_rules: list[str],
        conversation_id: str | None = None,
        user: str = "salesgym",
    ) -> dict:
        """Send a message to the Dify agent and get a response.

        Returns dict with 'answer' and 'conversation_id'.
        """
        inputs = self._build_inputs(strategy_prompt, improvement_rules)
        payload = {
            "inputs": inputs,
            "query": message,
            "response_mode": "blocking",
            "user": user,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        for attempt in range(3):
            try:
                response = await self._client.post(
                    f"{self.base_url}/chat-messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if response.status_code != 200:
                    print(f"Dify error {response.status_code}: {response.text}")
                    response.raise_for_status()
                data = response.json()
                return {
                    "answer": data.get("answer", ""),
                    "conversation_id": data.get("conversation_id", ""),
                }
            except (httpx.ReadError, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                print(f"Dify connection error (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(2 * (attempt + 1))
                else:
                    raise
