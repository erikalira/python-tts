#!/usr/bin/env python3

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from multiple possible locations
def load_env_file():
    possible_paths = [
        # Current directory
        Path(".") / ".env",
        # Parent directory (original behavior)
        Path(__file__).resolve().parents[1] / ".env",
        # Same directory as script
        Path(__file__).resolve().parent / ".env",
        # User home directory
        Path.home() / ".env",
    ]
    
    loaded = False
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            print(f"[test] ✅ Loaded .env from: {env_path}")
            loaded = True
            break
        else:
            print(f"[test] ❌ .env not found at: {env_path}")
    
    if not loaded:
        print("[test] ⚠️ No .env file found, using system environment variables only")
    
    # Show current environment configuration
    discord_url = os.getenv('DISCORD_BOT_URL')
    member_id = os.getenv('DISCORD_MEMBER_ID')
    
    print(f"[test] DISCORD_BOT_URL = {discord_url!r}")
    print(f"[test] DISCORD_MEMBER_ID = {member_id!r}")
    
    if discord_url:
        print("[test] ✅ Discord bot configured - will send requests to bot")
    else:
        print("[test] ⚠️ No Discord bot URL - will use local TTS only")

def test_discord_request(text: str):
    """Test sending a request to Discord bot like tts_hotkey does."""
    print("\n" + "="*50)
    print("🧪 TESTE DE CONEXÃO COM DISCORD BOT")
    print("="*50)
    
    # If DISCORD_BOT_URL is set, send the text to the bot instead of local playback
    discord_bot_url = os.getenv('DISCORD_BOT_URL')
    print(f"[test] Checking Discord bot URL: {discord_bot_url!r}")
    
    if discord_bot_url:
        print("[test] 🚀 Sending request to Discord bot...")
        try:
            payload = {'text': text}
            # optionally send member id so the bot can infer the current guild/channel
            member = os.getenv('DISCORD_MEMBER_ID')
            if member:
                payload['member_id'] = member
                print(f"[test] Added member_id: {member}")
            
            url = discord_bot_url.rstrip('/') + '/speak'
            print(f"[test] 📡 POST -> {url}")
            print(f"[test] 📦 Payload: {payload}")
            
            # Use longer timeout for Render cold starts + TTS processing
            print("[test] ⏳ Sending request (timeout: 10s)...")
            resp = requests.post(url, json=payload, timeout=10)
            print(f"[test] 📨 Bot response: {resp.status_code} {resp.text!r}")
            
            if resp.ok:
                print("[test] ✅ Successfully sent to Discord bot!")
                print("[test] 🎯 A request foi enviada com sucesso!")
                return True
            else:
                print(f"[test] ❌ Bot returned non-OK status: {resp.status_code}")
                return False
        except requests.exceptions.Timeout:
            print('[test] ⏰ Request timed out after 10s (server might be cold starting)')
            return False
        except requests.exceptions.ConnectionError as e:
            print(f'[test] 🌐 Connection error: {e}')
            return False
        except Exception as e:
            print(f'[test] ❌ Unexpected error sending to Discord bot: {e}')
            import traceback
            traceback.print_exc()
            return False
    else:
        print("[test] ❌ No Discord bot URL configured")
        return False

def main():
    print("🧪 Teste de Conexão do TTS Hotkey com Discord")
    print()
    
    # Load environment
    load_env_file()
    print()
    
    # Test Discord connection
    success = test_discord_request("teste de conexão do hotkey")
    
    print("\n" + "="*50)
    if success:
        print("✅ TESTE PASSOU: O hotkey deve funcionar com Discord!")
        print("   Se ainda não funcionar no .exe, o problema pode ser:")
        print("   1. O arquivo .env não está no local correto para o .exe")
        print("   2. As dependências (requests) não foram incluídas no .exe")
        print("   3. O .exe está sendo executado em um diretório diferente")
    else:
        print("❌ TESTE FALHOU: O hotkey vai usar TTS local apenas")
        print("   Verifique as configurações do Discord bot")
    print("="*50)

if __name__ == '__main__':
    main()
