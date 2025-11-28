#!/usr/bin/env python3
"""
TTS Hotkey - Versão Standalone Configurável
Este arquivo permite personalizar as configurações antes de compilar.
"""

# =============================================================================
# 🔧 CONFIGURAÇÕES - EDITE AQUI ANTES DE COMPILAR
# =============================================================================

class Config:
    """Configurações centralizadas do TTS Hotkey."""
    
    # 🌐 Discord Bot Configuration
    DISCORD_BOT_URL = "https://python-tts-s3z8.onrender.com"
    DISCORD_CHANNEL_ID = None  # Ex: "123456789012345678" (opcional)
    DISCORD_MEMBER_ID = None   # Ex: "987654321098765432" (IMPORTANTE: seu Discord User ID)
    
    @classmethod
    def get_config_file(cls):
        """Get configuration file path."""
        return Path.home() / "tts_hotkey_config.json"
    
    @classmethod
    def load_from_file(cls):
        """Load configuration from file."""
        config_file = cls.get_config_file()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cls.DISCORD_MEMBER_ID = data.get('discord_member_id')
                    cls.DISCORD_CHANNEL_ID = data.get('discord_channel_id')
                    cls.DISCORD_BOT_URL = data.get('discord_bot_url', cls.DISCORD_BOT_URL)
                    cls.TTS_ENGINE = data.get('tts_engine', cls.TTS_ENGINE)
                    cls.TTS_LANGUAGE = data.get('tts_language', cls.TTS_LANGUAGE)
                    print(f"[CONFIG] ✅ Configuração carregada de: {config_file}")
                    # Update environment variables after loading
                    cls.update_environment_variables()
            except Exception as e:
                print(f"[CONFIG] ⚠️ Erro ao carregar configuração: {e}")
    
    @classmethod
    def save_to_file(cls):
        """Save configuration to file."""
        config_file = cls.get_config_file()
        try:
            data = {
                'discord_member_id': cls.DISCORD_MEMBER_ID,
                'discord_channel_id': cls.DISCORD_CHANNEL_ID,
                'discord_bot_url': cls.DISCORD_BOT_URL,
                'tts_engine': cls.TTS_ENGINE,
                'tts_language': cls.TTS_LANGUAGE,
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[CONFIG] ✅ Configuração salva em: {config_file}")
        except Exception as e:
            print(f"[CONFIG] ❌ Erro ao salvar configuração: {e}")
    
    @classmethod
    def update_environment_variables(cls):
        """Update environment variables after configuration changes."""
        os.environ['DISCORD_BOT_URL'] = cls.DISCORD_BOT_URL or ''
        if cls.DISCORD_CHANNEL_ID:
            os.environ['DISCORD_CHANNEL_ID'] = cls.DISCORD_CHANNEL_ID
        if cls.DISCORD_MEMBER_ID:
            os.environ['DISCORD_MEMBER_ID'] = cls.DISCORD_MEMBER_ID
        os.environ['TTS_ENGINE'] = cls.TTS_ENGINE
        os.environ['TTS_LANGUAGE'] = cls.TTS_LANGUAGE
        os.environ['TTS_VOICE_ID'] = cls.TTS_VOICE_ID
        if cls.TTS_OUTPUT_DEVICE:
            os.environ['TTS_OUTPUT_DEVICE'] = cls.TTS_OUTPUT_DEVICE
        print(f"[CONFIG] ✅ Variáveis de ambiente atualizadas - DISCORD_MEMBER_ID: {cls.DISCORD_MEMBER_ID}")

    @classmethod
    def is_configured(cls):
        """Check if minimum configuration is present."""
        return cls.DISCORD_MEMBER_ID is not None
    
    # 🎤 TTS Configuration  
    TTS_ENGINE = "gtts"           # gtts, pyttsx3, edge-tts
    TTS_LANGUAGE = "pt"           # pt, en, es, fr, etc.
    TTS_VOICE_ID = "roa/pt-br"   # Voice for specific engines
    TTS_RATE = 180               # Speech rate (words per minute)
    
    # 🔊 Audio Output
    TTS_OUTPUT_DEVICE = None     # Ex: "CABLE Input (VB-Audio Virtual Cable)"
    
    # ⚙️ Hotkey Configuration
    TRIGGER_OPEN = "{"           # Character to start recording
    TRIGGER_CLOSE = "}"          # Character to stop and speak
    
    # 🎨 Interface
    SHOW_NOTIFICATIONS = True    # Show desktop notifications
    CONSOLE_LOGS = True          # Show detailed console logs
    
    # ⏱️ Network Configuration
    REQUEST_TIMEOUT = 10         # Seconds to wait for Discord bot
    RETRY_ATTEMPTS = 1           # Number of retries if request fails
    
    # 🔐 Advanced (usually don't need to change)
    USER_AGENT = "TTS-Hotkey/2.0"
    MAX_TEXT_LENGTH = 500        # Maximum characters to speak

# =============================================================================
# 💡 COMO USAR:
# 1. Execute o .exe - uma janela de configuração aparecerá na primeira vez
# 2. Insira seu Discord User ID e outras configurações
# 3. Pronto! Use {texto} para falar
# 
# 🔧 PARA RECOMPILAR:
# 1. Edite as configurações padrão acima (opcional)
# 2. Execute: build_configurable.ps1
# 3. Distribua o novo .exe
# =============================================================================

import os
import tempfile
import keyboard
import pyttsx3
import threading
import json
from pathlib import Path

# GUI imports with fallback
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
    _tkinter_available = True
except ImportError:
    _tkinter_available = False
    print("[tts_hotkey] ⚠️ tkinter not available, using console configuration only")

# Set embedded configuration from Config class
os.environ.setdefault('DISCORD_BOT_URL', Config.DISCORD_BOT_URL or '')
if Config.DISCORD_CHANNEL_ID:
    os.environ.setdefault('DISCORD_CHANNEL_ID', Config.DISCORD_CHANNEL_ID)
if Config.DISCORD_MEMBER_ID:
    os.environ.setdefault('DISCORD_MEMBER_ID', Config.DISCORD_MEMBER_ID)
os.environ.setdefault('TTS_ENGINE', Config.TTS_ENGINE)
os.environ.setdefault('TTS_LANGUAGE', Config.TTS_LANGUAGE)
os.environ.setdefault('TTS_VOICE_ID', Config.TTS_VOICE_ID)
if Config.TTS_OUTPUT_DEVICE:
    os.environ.setdefault('TTS_OUTPUT_DEVICE', Config.TTS_OUTPUT_DEVICE)

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image
    _pystray_available = True
except Exception:
    _pystray_available = False
    print("[tts_hotkey] ⚠️ pystray not available, running without system tray icon")

# Optional: play audio directly to a specific output device
try:
    import sounddevice as sd
    import soundfile as sf
    _sd_available = True
    try:
        import numpy as np
    except Exception:
        np = None
except Exception:
    sd = None
    sf = None
    _sd_available = False

# Test if requests is available
try:
    import requests
    _requests_available = True
except ImportError:
    _requests_available = False
    print("[tts_hotkey] ❌ requests library not available - will use local TTS only")

recording = False
buffer = []
suppress_events = threading.Event()

# GUI Configuration Window
class ConfigWindow:
    """GUI window for configuring TTS Hotkey settings."""
    
    def __init__(self):
        self.result = None
        self.root = None
    
    def show_config_dialog(self):
        """Show configuration dialog."""
        if not _tkinter_available:
            return self._console_config()
        
        try:
            self.root = tk.Tk()
            self.root.title("TTS Hotkey - Configuração")
            self.root.geometry("500x400")
            self.root.resizable(False, False)
            
            # Center the window
            self.root.eval('tk::PlaceWindow . center')
            
            self._create_widgets()
            self.root.mainloop()
            
            return self.result
        except Exception as e:
            print(f"[CONFIG] Erro na interface gráfica: {e}")
            return self._console_config()
    
    def _create_widgets(self):
        """Create the configuration widgets."""
        # Title
        title_label = tk.Label(self.root, text="🎤 TTS Hotkey - Configuração", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Discord Member ID (required)
        ttk.Label(main_frame, text="Discord User ID (obrigatório):", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.member_id_var = tk.StringVar(value=Config.DISCORD_MEMBER_ID or "")
        member_id_entry = ttk.Entry(main_frame, textvariable=self.member_id_var, width=50)
        member_id_entry.pack(fill="x", pady=(0, 5))
        
        # Help text for Discord ID
        help_text = tk.Text(main_frame, height=3, wrap=tk.WORD, font=("Arial", 8))
        help_text.insert("1.0", "💡 Para obter seu Discord User ID:\n"
                                "1. No Discord, vá em Configurações > Avançado > Modo Desenvolvedor (ativar)\n"
                                "2. Clique com botão direito em seu nome e escolha 'Copiar ID'")
        help_text.config(state="disabled", bg="#f0f0f0")
        help_text.pack(fill="x", pady=(0, 15))
        
        # Bot URL
        ttk.Label(main_frame, text="URL do Bot (opcional):").pack(anchor="w", pady=(0, 5))
        self.bot_url_var = tk.StringVar(value=Config.DISCORD_BOT_URL or "")
        bot_url_entry = ttk.Entry(main_frame, textvariable=self.bot_url_var, width=50)
        bot_url_entry.pack(fill="x", pady=(0, 10))
        
        # TTS Engine
        ttk.Label(main_frame, text="Engine de TTS:").pack(anchor="w", pady=(0, 5))
        self.engine_var = tk.StringVar(value=Config.TTS_ENGINE)
        engine_combo = ttk.Combobox(main_frame, textvariable=self.engine_var, 
                                   values=["gtts", "pyttsx3", "edge-tts"], state="readonly")
        engine_combo.pack(fill="x", pady=(0, 10))
        
        # Language
        ttk.Label(main_frame, text="Idioma:").pack(anchor="w", pady=(0, 5))
        self.language_var = tk.StringVar(value=Config.TTS_LANGUAGE)
        language_combo = ttk.Combobox(main_frame, textvariable=self.language_var,
                                     values=["pt", "en", "es", "fr"], state="readonly")
        language_combo.pack(fill="x", pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 Salvar e Continuar", 
                  command=self._save_config).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self._cancel).pack(side="right")
    
    def _save_config(self):
        """Save configuration and close."""
        member_id = self.member_id_var.get().strip()
        
        if not member_id:
            messagebox.showerror("Erro", "Discord User ID é obrigatório!")
            return
        
        if not member_id.isdigit():
            messagebox.showerror("Erro", "Discord User ID deve conter apenas números!")
            return
        
        # Update Config class
        Config.DISCORD_MEMBER_ID = member_id
        Config.DISCORD_BOT_URL = self.bot_url_var.get().strip() or Config.DISCORD_BOT_URL
        Config.TTS_ENGINE = self.engine_var.get()
        Config.TTS_LANGUAGE = self.language_var.get()
        
        # Save to file
        Config.save_to_file()
        
        # CRITICAL: Update environment variables for immediate use
        Config.update_environment_variables()
        
        self.result = True
        self.root.quit()
        self.root.destroy()
    
    def _cancel(self):
        """Cancel configuration."""
        self.result = False
        self.root.quit()
        self.root.destroy()
    
    def _console_config(self):
        """Fallback console configuration."""
        print("\n" + "="*50)
        print("🎤 TTS Hotkey - Configuração via Console")
        print("="*50)
        
        # Discord Member ID
        current_id = Config.DISCORD_MEMBER_ID or ""
        while True:
            member_id = input(f"Discord User ID [{current_id}]: ").strip()
            if not member_id and current_id:
                member_id = current_id
                break
            if member_id and member_id.isdigit():
                break
            print("❌ Discord User ID deve conter apenas números!")
        
        Config.DISCORD_MEMBER_ID = member_id
        Config.save_to_file()
        
        print("✅ Configuração salva!")
        return True

def show_config():
    """Show current configuration from Config class."""
    print("=" * 70)
    print("🎤 TTS Hotkey - Configuração Personalizada")
    print("=" * 70)
    
    # Discord Configuration
    print("🌐 DISCORD:")
    print(f"   Bot URL: {Config.DISCORD_BOT_URL or 'Não configurado'}")
    if Config.DISCORD_CHANNEL_ID:
        print(f"   📺 Channel ID: {Config.DISCORD_CHANNEL_ID}")
    if Config.DISCORD_MEMBER_ID:
        print(f"   👤 Member ID: {Config.DISCORD_MEMBER_ID}")
    else:
        print(f"   ⚠️  Member ID: NÃO CONFIGURADO (recomendado para melhor funcionamento)")
    
    # TTS Configuration
    print(f"\n🎤 TTS:")
    print(f"   Engine: {Config.TTS_ENGINE}")
    print(f"   Idioma: {Config.TTS_LANGUAGE}")
    print(f"   Velocidade: {Config.TTS_RATE} wpm")
    if Config.TTS_OUTPUT_DEVICE:
        print(f"   🔊 Device: {Config.TTS_OUTPUT_DEVICE}")
    
    # Hotkey Configuration
    print(f"\n⌨️ HOTKEYS:")
    print(f"   Iniciar: '{Config.TRIGGER_OPEN}'")
    print(f"   Finalizar: '{Config.TRIGGER_CLOSE}'")
    print(f"   Exemplo: {Config.TRIGGER_OPEN}olá mundo{Config.TRIGGER_CLOSE}")
    
    # Network Configuration
    print(f"\n🌐 REDE:")
    print(f"   Timeout: {Config.REQUEST_TIMEOUT}s")
    print(f"   Tentativas: {Config.RETRY_ATTEMPTS}")
    
    # Status
    print(f"\n📊 STATUS:")
    discord_available = Config.DISCORD_BOT_URL and _requests_available
    if discord_available:
        print("   ✅ Modo Discord: Enviará áudio para o bot")
    else:
        print("   🔇 Modo Local: Reproduzirá áudio localmente")
        if not Config.DISCORD_BOT_URL:
            print("   💡 Configure Config.DISCORD_BOT_URL para usar Discord")
        if not _requests_available:
            print("   💡 Biblioteca 'requests' não disponível")
    
    print(f"\n🔧 RECURSOS:")
    print(f"   Notificações: {'✅' if Config.SHOW_NOTIFICATIONS else '❌'}")
    print(f"   Logs detalhados: {'✅' if Config.CONSOLE_LOGS else '❌'}")
    print(f"   System Tray: {'✅' if _pystray_available else '❌'}")
    
    print("\n📝 COMO CONFIGURAR:")
    if not Config.DISCORD_MEMBER_ID:
        print("   ⚠️  Na primeira execução, uma janela aparecerá para configuração")
    print("   1. Insira seu Discord User ID (obrigatório)")
    print("   2. Configure outras opções se necessário")
    print("   3. Clique em 'Salvar e Continuar'")
    print("   4. Use {texto} para falar!")
    
    print("\n🔧 PARA RECONFIGURAR:")
    if _pystray_available:
        print("   • Clique com botão direito no ícone da bandeja → Configurações")
    print("   • Ou delete o arquivo: ~/tts_hotkey_config.json e reinicie")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("   • Configure DISCORD_MEMBER_ID para melhor detecção do canal")
    print("   • Bot tenta conectar automaticamente onde você estiver")
    print("   • Bot sai da sala após 30 minutos de inatividade")
    print("   • Use /join no Discord se precisar conectar manualmente")
    print("=" * 70)

def _speak_and_send(text: str, backspaces: int):
    """Send text to Discord or speak locally."""
    suppress_events.set()
    try:
        discord_bot_url = os.getenv('DISCORD_BOT_URL')
        
        if discord_bot_url and _requests_available:
            print(f"[tts_hotkey] 🚀 Enviando '{text}' para Discord...")
            try:
                payload = {'text': text}
                ch = os.getenv('DISCORD_CHANNEL_ID')
                if ch:
                    payload['channel_id'] = ch
                member = os.getenv('DISCORD_MEMBER_ID')
                print(f"[DEBUG] DISCORD_MEMBER_ID from env: '{member}'")
                print(f"[DEBUG] Config.DISCORD_MEMBER_ID: '{Config.DISCORD_MEMBER_ID}'")
                if member:
                    payload['member_id'] = member
                else:
                    print("[DEBUG] No member_id found in environment variables!")
                
                url = discord_bot_url.rstrip('/') + '/speak'
                resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                
                if resp.ok:
                    print("[tts_hotkey] ✅ Enviado com sucesso!")
                    for _ in range(backspaces):
                        keyboard.send('backspace')
                    return
                else:
                    print(f"[tts_hotkey] ❌ Erro: {resp.status_code}, usando TTS local")
            except requests.exceptions.Timeout:
                print('[tts_hotkey] ⏰ Timeout, usando TTS local')
            except Exception as e:
                print(f'[tts_hotkey] ❌ Erro: {e}, usando TTS local')
        
        # Local TTS fallback
        print(f"[tts_hotkey] 🔊 Reproduzindo localmente: '{text}'")
        engine = pyttsx3.init()
        engine.setProperty('rate', Config.TTS_RATE)
        engine.say(text)
        engine.runAndWait()
        
        for _ in range(backspaces):
            keyboard.send('backspace')
            
    finally:
        suppress_events.clear()

def on_key(event):
    global recording, buffer
    
    if suppress_events.is_set():
        return
    
    if event.event_type != keyboard.KEY_DOWN:
        return
    
    key = event.name
    
    if key in (Config.TRIGGER_OPEN, 'open_bracket', '[', 'left_bracket', 'braceleft'):
        recording = True
        buffer = []
        return
    
    if recording:
        if key in (Config.TRIGGER_CLOSE, 'close_bracket', ']', 'right_bracket', 'braceright'):
            recording = False
            text = ''.join(buffer).strip()
            if text:
                backspaces = len(buffer) + 2
                t = threading.Thread(target=_speak_and_send, args=(text, backspaces), daemon=True)
                t.start()
            buffer = []
            return
        
        if key in ('backspace', 'back'):
            if buffer:
                buffer.pop()
            return
        
        if key == 'space':
            buffer.append(' ')
        elif len(key) == 1:
            buffer.append(key)

# System tray functions (if available)
if _pystray_available:
    def create_icon_image():
        try:
            icon_path = Path(__file__).resolve().parents[1] / "icon.png"
            if icon_path.exists():
                return Image.open(icon_path)
        except:
            pass
        
        # Fallback icon
        img = Image.new('RGB', (64, 64), color='#2C2F33')
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([22, 15, 42, 35], fill='#7289DA')
        draw.ellipse([22, 30, 42, 45], fill='#7289DA')
        return img
    
    def on_status_click(icon, item):
        discord_url = Config.DISCORD_BOT_URL
        if discord_url and Config.DISCORD_MEMBER_ID:
            print(f"✅ Conectado ao Discord: {discord_url}")
            print(f"👤 User ID: {Config.DISCORD_MEMBER_ID}")
        else:
            print("⚠️ Discord não configurado completamente")
    
    def on_configure(icon, item):
        """Open configuration dialog."""
        print("🔧 Abrindo configurações...")
        config_window = ConfigWindow()
        config_window.show_config_dialog()
    
    def on_quit(icon, item):
        print("🛑 Encerrando TTS Hotkey...")
        icon.stop()
        os._exit(0)
    
    def setup_tray_icon():
        menu = Menu(
            MenuItem('TTS Hotkey', on_status_click, default=True),
            MenuItem('Digite {texto} para falar', lambda: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem('⚙️ Configurações', on_configure),
            MenuItem('Sair', on_quit)
        )
        
        icon_image = create_icon_image()
        return Icon("TTS Hotkey", icon_image, "TTS Hotkey", menu)

def main():
    # Load existing configuration
    Config.load_from_file()
    
    # Check if configuration is needed
    if not Config.is_configured():
        print("🔧 Primeira execução detectada! Vamos configurar o TTS Hotkey...")
        config_window = ConfigWindow()
        if not config_window.show_config_dialog():
            print("❌ Configuração cancelada. Encerrando...")
            return
    
    show_config()
    
    # Setup keyboard hook
    keyboard.hook(on_key)
    
    if _pystray_available:
        # Run with system tray
        icon = setup_tray_icon()
        icon.run()
    else:
        # Run without tray (console mode)
        print("⌨️ Sistema ativo! Pressione Ctrl+C para sair...")
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n🛑 Encerrando...")

if __name__ == '__main__':
    main()