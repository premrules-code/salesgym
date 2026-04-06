import tempfile
from src.memory import MemoryManager
from src.models import CallTranscript, CallOutcome, Turn, ImprovementRule


def test_save_and_load_transcripts():
    with tempfile.TemporaryDirectory() as tmpdir:
        mm = MemoryManager(data_dir=tmpdir)
        transcripts = [
            CallTranscript(
                strategy_id=1, strategy_name="A", customer_id="bob", generation=0,
                turns=[Turn(role="agent", text="Hi")],
                outcome=CallOutcome(converted=True, turns=1, rapport=0.8, objections_faced=[], objection_handled=True),
            ),
        ]
        mm.save_transcripts(0, transcripts)
        loaded = mm.load_transcripts(0)
        assert len(loaded) == 1
        assert loaded[0].strategy_name == "A"


def test_save_and_load_rules():
    with tempfile.TemporaryDirectory() as tmpdir:
        mm = MemoryManager(data_dir=tmpdir)
        rules = [
            ImprovementRule(id=1, trigger="price", old_response="discount",
                          new_response="ROI", evidence="data", generation_learned=0),
        ]
        mm.save_rules(rules)
        loaded = mm.load_rules()
        assert len(loaded) == 1
        assert loaded[0].trigger == "price"


def test_rules_accumulate():
    with tempfile.TemporaryDirectory() as tmpdir:
        mm = MemoryManager(data_dir=tmpdir)
        rules_gen0 = [
            ImprovementRule(id=1, trigger="price", old_response="a",
                          new_response="b", evidence="c", generation_learned=0),
        ]
        mm.save_rules(rules_gen0)

        rules_gen1 = [
            ImprovementRule(id=2, trigger="skeptic", old_response="d",
                          new_response="e", evidence="f", generation_learned=1),
        ]
        mm.add_rules(rules_gen1)
        all_rules = mm.load_rules()
        assert len(all_rules) == 2


def test_get_rules_as_strings():
    with tempfile.TemporaryDirectory() as tmpdir:
        mm = MemoryManager(data_dir=tmpdir)
        rules = [
            ImprovementRule(id=1, trigger="price", old_response="discount",
                          new_response="ROI framing", evidence="2/3 won", generation_learned=0),
        ]
        mm.save_rules(rules)
        strings = mm.get_rules_as_strings()
        assert len(strings) == 1
        assert "price" in strings[0]
        assert "ROI framing" in strings[0]
