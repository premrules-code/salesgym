from src.seed_data import get_initial_strategies, get_customer_personas


def test_initial_strategies_count():
    strategies = get_initial_strategies()
    assert len(strategies) == 8


def test_strategies_have_unique_names():
    strategies = get_initial_strategies()
    names = [s.name for s in strategies]
    assert len(names) == len(set(names))


def test_strategies_have_prompts():
    strategies = get_initial_strategies()
    for s in strategies:
        assert len(s.system_prompt) > 50
        assert "CloudSync" in s.system_prompt


def test_customer_personas_count():
    personas = get_customer_personas()
    assert len(personas) == 3


def test_personas_have_difficulty_1():
    personas = get_customer_personas()
    for p in personas:
        assert p.difficulty == 1


def test_personas_evolve_at_difficulty_2():
    personas = get_customer_personas(difficulty=2)
    for p in personas:
        assert len(p.evolved_objections) >= 2


def test_personas_evolve_more_at_difficulty_3():
    personas = get_customer_personas(difficulty=3)
    for p in personas:
        assert len(p.evolved_objections) >= 4
