#!/usr/bin/env python3
"""
TTS Hotkey - Versão Minimalista que Funciona
Aplicação simplificada sem dependências complexas.
"""

import sys
import json
import threading
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class MinimalConfig:
    discord_member_id: str = ""
    discord_bot_url: str = "https://python-tts-s3z8.onrender.com"
    tts_engine: str = "pyttsx3"  # pyttsx3 ou gtts ou discord
    tts_language: str = "pt"
    tts_rate: int = 180
    hotkey_open: str = "{"
    hotkey_close: str = "}"


class MinimalConfigManager:
    """Gerenciador de configuração simplificado."""
    
    def __init__(self):
        self.config_file = Path.cwd() / "tts_config.json"
        self.config = MinimalConfig()
    
    def load(self):
        """Carrega configuração do arquivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = MinimalConfig(**data)
                    print("✅ Configuração carregada")
            else:
                print("📋 Usando configuração padrão")
        except Exception as e:
            print(f"⚠️ Erro ao carregar configuração: {e}")
    
    def save(self):
        """Salva configuração no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            print("💾 Configuração salva")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
            return False
    
    def configure_interactive(self):
        """Configuração interativa via console."""
        print("\n" + "="*50)
        print("🔧 Configuração TTS Hotkey")
        print("="*50)
        
        # Discord User ID
        print("Para usar Discord TTS, você precisa do seu User ID:")
        print("1. No Discord, vá em Configurações > Avançado > Modo Desenvolvedor (ativar)")
        print("2. Clique com botão direito no seu nome e 'Copiar ID do usuário'")
        user_id = input(f"Discord User ID [{self.config.discord_member_id}]: ").strip()
        if user_id:
            self.config.discord_member_id = user_id
        
        # Engine TTS
        print(f"\n🎵 Engines TTS disponíveis:")
        available_engines = []
        if PYTTSX3_AVAILABLE:
            available_engines.append("pyttsx3 (local)")
        if GTTS_AVAILABLE:
            available_engines.append("gtts (Google)")
        if self.config.discord_member_id and REQUESTS_AVAILABLE:
            available_engines.append("discord (via bot)")
        
        for i, engine in enumerate(available_engines, 1):
            print(f"{i}. {engine}")
        
        choice = input(f"Escolha [1-{len(available_engines)}, atual: {self.config.tts_engine}]: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_engines):
                engine_name = available_engines[idx].split()[0]
                self.config.tts_engine = engine_name
        
        # Velocidade (para pyttsx3)
        if self.config.tts_engine == "pyttsx3":
            rate = input(f"Velocidade [50-400, atual: {self.config.tts_rate}]: ").strip()
            if rate.isdigit():
                rate_val = int(rate)
                if 50 <= rate_val <= 400:
                    self.config.tts_rate = rate_val
        
        # Hotkey
        print(f"\n⌨️ Configuração de Hotkeys")
        open_key = input(f"Caractere para abrir [{self.config.hotkey_open}]: ").strip()
        if open_key:
            self.config.hotkey_open = open_key
        
        close_key = input(f"Caractere para fechar [{self.config.hotkey_close}]: ").strip()
        if close_key:
            self.config.hotkey_close = close_key
        
        # Salvar
        if self.save():
            print("✅ Configuração salva com sucesso!")
            return True
        else:
            print("❌ Erro ao salvar configuração!")
            return False


class TTSEngine:
    """Engine TTS simplificado."""
    
    def __init__(self, config: MinimalConfig):
        self.config = config
        self._pyttsx_engine = None
        
        if config.tts_engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self._pyttsx_engine = pyttsx3.init()
                self._pyttsx_engine.setProperty('rate', config.tts_rate)
                print("✅ Engine pyttsx3 inicializado")
            except Exception as e:
                print(f"❌ Erro ao inicializar pyttsx3: {e}")
                self._pyttsx_engine = None
    
    def speak(self, text: str):
        """Fala o texto usando o engine configurado."""
        if not text.strip():
            return
        
        print(f"🗣️ Falando: '{text}'")
        
        try:
            if self.config.tts_engine == "pyttsx3" and self._pyttsx_engine:
                self._pyttsx_engine.say(text)
                self._pyttsx_engine.runAndWait()
            
            elif self.config.tts_engine == "gtts" and GTTS_AVAILABLE:
                self._speak_gtts(text)
            
            elif self.config.tts_engine == "discord" and REQUESTS_AVAILABLE:
                self._speak_discord(text)
            
            else:
                print(f"❌ Engine '{self.config.tts_engine}' não disponível")
                
        except Exception as e:
            print(f"❌ Erro no TTS: {e}")
    
    def _speak_gtts(self, text: str):
        """Usar Google TTS."""
        import tempfile
        import os
        import subprocess
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tts = gTTS(text=text, lang=self.config.tts_language)
            tts.save(tmp_file.name)
            
            # Tentar reproduzir com diferentes players
            players = ['mpg123', 'mpg321', 'ffplay', 'mplayer']
            for player in players:
                try:
                    subprocess.run([player, tmp_file.name], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
                    break
                except FileNotFoundError:
                    continue
            
            # Remover arquivo temporário
            try:
                os.unlink(tmp_file.name)
            except:
                pass
    
    def _speak_discord(self, text: str):
        """Usar Discord TTS via bot."""
        if not self.config.discord_member_id:
            print("❌ Discord User ID não configurado")
            return
        
        data = {
            "text": text,
            "user_id": self.config.discord_member_id
        }
        
        try:
            response = requests.post(
                f"{self.config.discord_bot_url}/tts",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ TTS enviado para Discord")
            else:
                print(f"❌ Erro Discord TTS: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na conexão Discord: {e}")


class HotkeyMonitor:
    """Monitor de hotkeys simplificado."""
    
    def __init__(self, config: MinimalConfig, tts_engine: TTSEngine):
        self.config = config
        self.tts_engine = tts_engine
        self.is_recording = False
        self.recorded_text = ""
        self.running = False
    
    def start(self):
        """Inicia monitoramento de hotkeys."""
        if not KEYBOARD_AVAILABLE:
            print("❌ Biblioteca keyboard não disponível")
            print("💡 Instale com: pip install keyboard")
            return False
        
        print(f"⌨️ Monitorando hotkeys: {self.config.hotkey_open} e {self.config.hotkey_close}")
        print("💡 Digite texto entre os caracteres configurados para usar TTS")
        print("🛑 Pressione Ctrl+C para sair")
        
        self.running = True
        
        def on_key_event(event):
            if event.event_type == keyboard.KEY_DOWN:
                char = event.name
                
                if char == self.config.hotkey_open and not self.is_recording:
                    self.is_recording = True
                    self.recorded_text = ""
                    print(f"🎯 Gravação iniciada...")
                
                elif char == self.config.hotkey_close and self.is_recording:
                    self.is_recording = False
                    if self.recorded_text.strip():
                        threading.Thread(
                            target=self.tts_engine.speak,
                            args=(self.recorded_text.strip(),),
                            daemon=True
                        ).start()
                    self.recorded_text = ""
                    print("🔚 Gravação finalizada")
                
                elif self.is_recording and len(char) == 1:
                    if char == 'space':
                        self.recorded_text += ' '
                    elif char.isalnum() or char in '.,!?;:-_()[]{}@#$%&*+=<>/\\|':
                        self.recorded_text += char
        
        keyboard.hook(on_key_event)
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Parando monitoramento...")
        
        keyboard.unhook_all()
        return True
    
    def stop(self):
        """Para o monitoramento."""
        self.running = False


class MinimalTTSApp:
    """Aplicação TTS minimalista."""
    
    def __init__(self):
        self.config_manager = MinimalConfigManager()
        self.tts_engine = None
        self.hotkey_monitor = None
    
    def run(self):
        """Executa a aplicação."""
        print("=" * 60)
        print("🎤 TTS Hotkey - Versão Minimalista")
        print("=" * 60)
        
        # Carregar configuração
        self.config_manager.load()
        
        # Verificar se precisa configurar
        needs_config = not self.config_manager.config.discord_member_id and \
                      self.config_manager.config.tts_engine == "discord"
        
        if needs_config or not self.config_manager.config_file.exists():
            print("🔧 Configuração necessária...")
            if not self.config_manager.configure_interactive():
                return
        
        # Inicializar TTS
        self.tts_engine = TTSEngine(self.config_manager.config)
        
        # Mostrar configuração atual
        config = self.config_manager.config
        print(f"\n📋 Configuração atual:")
        print(f"🎵 Engine TTS: {config.tts_engine}")
        print(f"⌨️ Hotkeys: {config.hotkey_open} ... {config.hotkey_close}")
        if config.tts_engine == "discord":
            print(f"👤 Discord User ID: {config.discord_member_id}")
        print()
        
        # Iniciar monitoramento
        self.hotkey_monitor = HotkeyMonitor(config, self.tts_engine)
        
        try:
            self.hotkey_monitor.start()
        except KeyboardInterrupt:
            pass
        finally:
            print("👋 Aplicação encerrada")


def main():
    """Função principal."""
    app = MinimalTTSApp()
    app.run()


if __name__ == '__main__':
    main()