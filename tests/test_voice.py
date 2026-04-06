from src.voice import VoiceGenerator


def test_voice_generator_sanitizes_text():
    vg = VoiceGenerator(api_key="fake-key")
    text = "Hey Bob!  Let me   tell you something..."
    sanitized = vg._sanitize_text(text)
    assert "  " not in sanitized


def test_voice_generator_builds_path():
    vg = VoiceGenerator(api_key="fake-key")
    path = vg._build_audio_path(generation=0, call_id="call_001", turn=1)
    assert "gen_0" in path
    assert "call_001" in path
    assert "turn_1" in path
    assert path.endswith(".mp3")
