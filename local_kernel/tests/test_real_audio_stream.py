
import pytest
from local_kernel.audio.real_audio_stream import RealAudioStream

def test_audio_init():
    ra = RealAudioStream()
    assert ra is not None

def test_level_reading():
    ra = RealAudioStream()
    level = ra.get_audio_level()
    assert 0.0 <= level <= 1.0

def test_analysis():
    ra = RealAudioStream()
    # In mock mode, we might get None or an event depending on randomness
    # Just ensure it doesn't crash
    result = ra.analyze_stream()
    if result:
        assert result["type"] == "audio"
