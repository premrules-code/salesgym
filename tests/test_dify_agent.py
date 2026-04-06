from src.dify_agent import DifyAgent


def test_dify_agent_builds_inputs():
    agent = DifyAgent(api_key="fake-key", base_url="https://api.dify.ai/v1")
    inputs = agent._build_inputs(
        strategy_prompt="You are a consultative sales agent...",
        improvement_rules=["When price objection -> use ROI framing"],
    )
    assert "consultative" in inputs["system_prompt"]
    assert "ROI" in inputs["system_prompt"]


def test_dify_agent_formats_rules():
    agent = DifyAgent(api_key="fake-key", base_url="https://api.dify.ai/v1")
    rules = ["Rule 1: Do X", "Rule 2: Do Y"]
    formatted = agent._format_rules(rules)
    assert "Rule 1" in formatted
    assert "Rule 2" in formatted


def test_dify_agent_no_rules():
    agent = DifyAgent(api_key="fake-key")
    formatted = agent._format_rules([])
    assert "No rules yet" in formatted
