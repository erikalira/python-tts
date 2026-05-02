"""Tests for FFmpeg runtime resolution."""

from unittest.mock import patch

from src.infrastructure.discord.ffmpeg_runtime import (
    has_ffmpeg_runtime,
    resolve_ffmpeg_executable,
)


def test_resolve_ffmpeg_executable_uses_valid_configured_path():
    with (
        patch("src.infrastructure.discord.ffmpeg_runtime.os.getenv", return_value="C:/ffmpeg/bin/ffmpeg.exe"),
        patch(
            "src.infrastructure.discord.ffmpeg_runtime._is_usable_executable",
            return_value=True,
        ),
        patch("src.infrastructure.discord.ffmpeg_runtime.shutil.which") as which_mock,
    ):
        resolved = resolve_ffmpeg_executable()

    assert resolved == "C:/ffmpeg/bin/ffmpeg.exe"
    which_mock.assert_not_called()


def test_resolve_ffmpeg_executable_falls_back_to_path_when_configured_path_is_invalid():
    with (
        patch("src.infrastructure.discord.ffmpeg_runtime.os.getenv", return_value="C:/broken/ffmpeg.exe"),
        patch(
            "src.infrastructure.discord.ffmpeg_runtime._is_usable_executable",
            return_value=False,
        ),
        patch("src.infrastructure.discord.ffmpeg_runtime.shutil.which", return_value="/usr/bin/ffmpeg") as which_mock,
    ):
        resolved = resolve_ffmpeg_executable()

    assert resolved == "/usr/bin/ffmpeg"
    which_mock.assert_called_once_with("ffmpeg")


def test_has_ffmpeg_runtime_is_false_when_configured_path_is_invalid_and_path_lookup_fails():
    with (
        patch("src.infrastructure.discord.ffmpeg_runtime.os.getenv", return_value="C:/broken/ffmpeg.exe"),
        patch(
            "src.infrastructure.discord.ffmpeg_runtime._is_usable_executable",
            return_value=False,
        ),
        patch("src.infrastructure.discord.ffmpeg_runtime.shutil.which", return_value=None),
    ):
        assert has_ffmpeg_runtime() is False
