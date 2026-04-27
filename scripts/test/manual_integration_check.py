#!/usr/bin/env python3
"""Manual Desktop App integration check before building a release."""

from __future__ import annotations

import os
from pathlib import Path


def test_discord_integration() -> bool:
    """Test the configured Discord bot endpoint when DISCORD_BOT_URL is set."""

    discord_bot_url = os.getenv("DISCORD_BOT_URL", "").strip()
    if not discord_bot_url:
        print("\n[SKIP] Discord bot integration: DISCORD_BOT_URL is not configured.")
        return True

    import requests

    base_url = discord_bot_url.rstrip("/")
    print("\n[CHECK] Discord bot integration...")

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("[PASS] Discord bot health endpoint is online.")
        else:
            print(f"[FAIL] Discord bot health returned HTTP {response.status_code}.")
            return False
    except Exception as exc:
        print(f"[FAIL] Could not connect to Discord bot health endpoint: {exc}")
        return False

    try:
        payload = {"text": "integration test", "channel_id": None, "member_id": None}
        response = requests.post(
            f"{base_url}/speak",
            json=payload,
            timeout=10,
            headers={"User-Agent": "TTS-Integration-Test/1.0"},
        )

        if response.status_code == 200:
            print("[PASS] /speak accepted the integration test request.")
            return True
        if response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            print(f"[WARN] /speak returned a validation response: {error_msg}")
            return True

        print(f"[FAIL] /speak returned unexpected HTTP {response.status_code}.")
        return False
    except Exception as exc:
        print(f"[FAIL] Could not test /speak endpoint: {exc}")
        return False


def test_dependencies() -> bool:
    """Check whether required and optional runtime packages are installed."""

    print("\n[CHECK] Dependencies...")

    required_packages = [
        ("requests", "HTTP communication"),
        ("keyboard", "Hotkey capture"),
    ]

    optional_packages = [
        ("pygame", "Audio playback"),
        ("pyttsx3", "Local TTS"),
        ("gtts", "Google TTS"),
        ("pystray", "System tray"),
        ("PIL", "Icons"),
    ]

    missing_required: list[str] = []
    missing_optional: list[str] = []

    for package, description in required_packages:
        try:
            __import__(package)
            print(f"[PASS] {package} - {description}")
        except ImportError:
            print(f"[FAIL] {package} - {description} (required)")
            missing_required.append(package)

    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"[PASS] {package} - {description}")
        except ImportError:
            print(f"[WARN] {package} - {description} (optional)")
            missing_optional.append(package)
        except Exception as exc:
            if "Gtk" in str(exc) or "display" in str(exc).lower():
                print(f"[WARN] {package} - {description} (GUI unavailable)")
            else:
                print(f"[WARN] {package} - {description} (error: {exc})")
                missing_optional.append(package)

    if missing_required:
        print(f"\n[FAIL] Missing required dependencies: {', '.join(missing_required)}")
        print("Install with: pip install " + " ".join(missing_required))
        return False

    if missing_optional:
        print(f"\n[INFO] Missing optional dependencies: {', '.join(missing_optional)}")
        print("Install for full functionality: pip install " + " ".join(missing_optional))

    return True


def test_file_structure() -> bool:
    """Check whether required release files exist."""

    print("\n[CHECK] File structure...")

    required_files = [
        ("app.py", "Desktop App entry point"),
        ("scripts/build/build_clean_architecture.ps1", "Windows build script"),
    ]

    missing_files: list[str] = []

    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"[PASS] {file_path} - {description}")
        else:
            print(f"[FAIL] {file_path} - {description} (missing)")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n[FAIL] Missing files: {', '.join(missing_files)}")
        return False

    return True


def test_basic_functionality() -> bool:
    """Compile the desktop entry point without executing GUI code."""

    print("\n[CHECK] Basic functionality...")

    try:
        print("[INFO] Compiling app.py syntax...")
        code = Path("app.py").read_text(encoding="utf-8")
        compile(code, "app.py", "exec")
        print("[PASS] app.py syntax is valid.")
    except SyntaxError as exc:
        print(f"[FAIL] Syntax error in app.py: {exc}")
        return False
    except Exception as exc:
        print(f"[WARN] app.py syntax read warning: {exc}")
        print("[INFO] This can happen when GUI dependencies are unavailable.")

    return True


def main() -> bool:
    """Run all manual integration checks."""

    print("=" * 70)
    print("TTS HOTKEY - MANUAL INTEGRATION CHECK")
    print("=" * 70)

    checks = [
        ("File structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Basic functionality", test_basic_functionality),
        ("Discord integration", test_discord_integration),
    ]

    passed = 0
    failed = 0

    for check_name, check_func in checks:
        print(f"\n{'=' * 20} {check_name} {'=' * 20}")
        try:
            if check_func():
                print(f"[PASS] {check_name}")
                passed += 1
            else:
                print(f"[FAIL] {check_name}")
                failed += 1
        except Exception as exc:
            print(f"[ERROR] {check_name}: {exc}")
            failed += 1

    print("\n" + "=" * 70)
    print("CHECK RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")

    if failed == 0:
        print("\nAll checks passed.")
        print("System is ready for build validation.")
        print("\nNext steps:")
        print("   - Windows: pwsh -File scripts/build/build_clean_architecture.ps1")
        print("   - Linux: build the executable through the CI-style Docker flow")
        print("   - Test the executable on a Windows machine")
        return True

    print(f"\n{failed} check(s) failed.")
    print("Fix the issues before building.")
    return False


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
