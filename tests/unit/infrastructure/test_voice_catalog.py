"""Tests for runtime voice catalog exposure."""

from types import SimpleNamespace
from unittest.mock import patch

from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog


def test_runtime_tts_catalog_exposes_pyttsx3_voice_names_as_selectable_values():
    catalog = RuntimeTTSCatalog()
    voices = [
        SimpleNamespace(
            id=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0",
            name="Microsoft David",
        ),
        SimpleNamespace(
            id=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PT-BR_MARIA_11.0",
            name="Microsoft Maria",
        ),
    ]

    with patch("src.infrastructure.tts.voice_catalog.list_pyttsx3_voices", return_value=voices):
        options = catalog.list_voice_options()
        david = catalog.get_voice_option("pyttsx3:microsoft david")
        assert david is not None
        assert david.voice_id == "Microsoft David"
        assert catalog.is_voice_available(engine="pyttsx3", voice_id="Microsoft David") is True
        assert catalog.is_voice_available(engine="pyttsx3", voice_id="Unknown Voice") is False
        matched = catalog.find_voice_option(engine="pyttsx3", language="system", voice_id="Microsoft Maria")

    pyttsx3_options = [option for option in options if option.engine == "pyttsx3"]
    assert [option.voice_id for option in pyttsx3_options] == ["Microsoft David", "Microsoft Maria"]
    assert matched is not None
    assert matched.label == "R.E.P.O. - Microsoft Maria"


def test_runtime_tts_catalog_includes_edge_tts_profiles():
    catalog = RuntimeTTSCatalog()

    options = catalog.list_voice_options()

    edge_options = [option for option in options if option.engine == "edge-tts"]
    assert edge_options
    assert any(option.voice_id == "pt-BR-FranciscaNeural" for option in edge_options)
    resolved = catalog.get_voice_option("edge-tts:pt-br-francisca")
    assert resolved is not None
    assert resolved.language == "pt-BR"
