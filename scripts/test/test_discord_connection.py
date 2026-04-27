#!/usr/bin/env python3
"""Manual check for Desktop App requests sent to the configured Discord bot."""

from __future__ import annotations

import os
import traceback
from pathlib import Path

import requests
from dotenv import load_dotenv


def load_env_file() -> None:
    """Load the first available .env file from common local locations."""

    possible_paths = [
        Path(".") / ".env",
        Path(__file__).resolve().parents[1] / ".env",
        Path(__file__).resolve().parent / ".env",
        Path.home() / ".env",
    ]

    loaded = False
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[test] Loaded .env from: {env_path}")
            loaded = True
            break
        print(f"[test] .env not found at: {env_path}")

    if not loaded:
        print("[test] No .env file found; using system environment variables only.")

    discord_url = os.getenv("DISCORD_BOT_URL")
    member_id = os.getenv("DISCORD_MEMBER_ID")

    print(f"[test] DISCORD_BOT_URL = {discord_url!r}")
    print(f"[test] DISCORD_MEMBER_ID = {member_id!r}")

    if discord_url:
        print("[test] Discord bot is configured; requests will be sent to the bot.")
    else:
        print("[test] No Discord bot URL is configured; Desktop App will use local TTS.")


def test_discord_request(text: str) -> bool:
    """Send a request to the Discord bot the same way the Desktop App does."""

    print("\n" + "=" * 50)
    print("DISCORD BOT CONNECTION CHECK")
    print("=" * 50)

    discord_bot_url = os.getenv("DISCORD_BOT_URL")
    print(f"[test] Checking Discord bot URL: {discord_bot_url!r}")

    if not discord_bot_url:
        print("[test] No Discord bot URL configured.")
        return False

    print("[test] Sending request to Discord bot...")
    try:
        payload = {"text": text}
        member = os.getenv("DISCORD_MEMBER_ID")
        if member:
            payload["member_id"] = member
            print(f"[test] Added member_id: {member}")

        url = discord_bot_url.rstrip("/") + "/speak"
        print(f"[test] POST -> {url}")
        print(f"[test] Payload: {payload}")

        print("[test] Sending request (timeout: 10s)...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"[test] Bot response: {response.status_code} {response.text!r}")

        if response.ok:
            print("[test] Successfully sent request to Discord bot.")
            return True

        print(f"[test] Bot returned non-OK status: {response.status_code}")
        return False
    except requests.exceptions.Timeout:
        print("[test] Request timed out after 10s.")
        return False
    except requests.exceptions.ConnectionError as exc:
        print(f"[test] Connection error: {exc}")
        return False
    except Exception as exc:
        print(f"[test] Unexpected error sending to Discord bot: {exc}")
        traceback.print_exc()
        return False


def main() -> None:
    """Run the manual Discord connection check."""

    print("Desktop App Discord connection check")
    print()

    load_env_file()
    print()

    success = test_discord_request("hotkey connection test")

    print("\n" + "=" * 50)
    if success:
        print("CHECK PASSED: the hotkey flow should work with Discord.")
        print("If the executable still fails, check:")
        print("   1. Whether .env is in the expected executable location.")
        print("   2. Whether requests was bundled into the executable.")
        print("   3. Whether the executable is running from a different working directory.")
    else:
        print("CHECK FAILED: the hotkey flow will fall back to local TTS only.")
        print("Review the Discord bot configuration.")
    print("=" * 50)


if __name__ == "__main__":
    main()
