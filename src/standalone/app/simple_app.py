#!/usr/bin/env python3
"""
Standalone Application - Simple Version
Main application without complex type checking.
"""

from ..config.standalone_config import StandaloneConfig, ConfigurationRepository, EnvironmentUpdater, ConfigurationValidator
from ..gui.simple_gui import ConfigurationService
from ..services.tts_services import TTSProcessor
from ..services.hotkey_services import HotkeyManager, HotkeyEvent
from ..services.notification_services import SystemTrayService


class SimpleHotkeyHandler:
    """Simple hotkey handler."""
    
    def __init__(self, tts_processor, notification_service):
        self._tts_processor = tts_processor
        self._notification_service = notification_service
    
    def handle_text_captured(self, event: HotkeyEvent) -> None:
        """Handle text capture."""
        if not event.text:
            return
        
        print(f"[APP] 📝 Texto capturado: '{event.text}'")
        self._notification_service.notify_info(
            "TTS Hotkey", 
            f"Processando: '{event.text[:50]}{'...' if len(event.text) > 50 else ''}'"
        )
        self._tts_processor.process_text(event.text, event.character_count)


class SimpleApplication:
    """Simplified standalone application."""
    
    def __init__(self):
        self._config = None
        self._config_repository = None
        self._config_service = None
        self._tts_processor = None
        self._hotkey_manager = None
        self._notification_service = None
        self._initialized = False
        self._running = False
    
    def initialize(self):
        """Initialize application."""
        try:
            # Load configuration
            self._config_repository = ConfigurationRepository()
            self._config = self._config_repository.load()
            
            # Initialize services
            self._config_service = ConfigurationService(prefer_gui=True)
            self._tts_processor = TTSProcessor(self._config)
            self._hotkey_manager = HotkeyManager(self._config)
            self._notification_service = SystemTrayService(self._config)
            
            # Setup integrations
            hotkey_handler = SimpleHotkeyHandler(self._tts_processor, self._notification_service)
            self._hotkey_manager.initialize(hotkey_handler)
            
            self._notification_service.initialize(
                status_click=self._handle_status_click,
                configure=self._handle_configure,
                quit_handler=self._handle_quit
            )
            
            self._hotkey_manager.set_external_suppression_check(
                lambda: self._tts_processor.is_processing()
            )
            
            self._initialized = True
            print("[APP] ✅ Aplicação inicializada")
            return True
            
        except Exception as e:
            print(f"[APP] ❌ Erro na inicialização: {e}")
            return False
    
    def run(self):
        """Run application."""
        if not self._initialized:
            if not self.initialize():
                print("[APP] ❌ Falha na inicialização")
                return
        
        try:
            # Handle initial config if needed
            if not ConfigurationValidator.is_configured(self._config):
                print("[APP] 🔧 Configuração inicial...")
                updated_config = self._config_service.get_configuration(self._config)
                if updated_config:
                    self._config = updated_config
                    self._config_repository.save(self._config)
                    self._update_services_config()
                else:
                    print("[APP] ❌ Configuração cancelada")
                    return
            
            # Update environment
            EnvironmentUpdater.update_from_config(self._config)
            
            # Show current config
            print("\n" + "="*50)
            print("🎤 TTS Hotkey - Configuração Atual")
            print("="*50)
            print(f"✅ Discord: {self._config.discord.bot_url}")
            print(f"👤 User ID: {self._config.discord.member_id}")
            print(f"🎵 Engine: {self._config.tts.engine}")
            print(f"🌍 Idioma: {self._config.tts.language}")
            print(f"⌨️ Hotkey: {self._config.hotkey.keys}")
            print("="*50)
            
            # Start services
            if not self._start_services():
                print("[APP] ❌ Falha ao iniciar serviços")
                return
            
            # Run main loop
            self._run_main_loop()
            
        except KeyboardInterrupt:
            print("\n[APP] 🛑 Interrompido pelo usuário")
        except Exception as e:
            print(f"[APP] ❌ Erro durante execução: {e}")
        finally:
            self._shutdown()
    
    def _start_services(self):
        """Start services."""
        print("[APP] 🚀 Iniciando serviços...")
        
        if not self._hotkey_manager.start():
            print("[APP] ❌ Falha ao iniciar hotkey")
            return False
        
        tray_started = self._notification_service.start()
        if not tray_started:
            print("[APP] ⚠️ System tray não disponível")
        
        self._running = True
        print("[APP] ✅ Serviços iniciados")
        return True
    
    def _run_main_loop(self):
        """Run main loop."""
        tray_available = self._notification_service.is_available()
        
        if tray_available:
            print("[APP] 📋 Sistema executando no system tray")
            print("[APP] 💡 Use o ícone da bandeja do sistema para controlar")
            self._notification_service.run_tray()
        else:
            print("[APP] 💻 Sistema executando em modo console")
            print("[APP] 💡 Pressione Ctrl+C para sair")
            try:
                import time
                while self._running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
    
    def _update_services_config(self):
        """Update services with new config."""
        try:
            self._tts_processor = TTSProcessor(self._config)
            if hasattr(self._hotkey_manager, 'update_config'):
                self._hotkey_manager.update_config(self._config)
            self._notification_service = SystemTrayService(self._config)
        except Exception as e:
            print(f"[APP] ⚠️ Erro ao atualizar configuração dos serviços: {e}")
    
    def _handle_status_click(self):
        """Handle status click."""
        print("[APP] 📊 Status clicked")
    
    def _handle_configure(self):
        """Handle configure request."""
        try:
            print("[APP] 🔧 Abrindo configuração...")
            updated_config = self._config_service.get_configuration(self._config)
            if updated_config:
                self._config = updated_config
                self._config_repository.save(self._config)
                EnvironmentUpdater.update_from_config(self._config)
                self._update_services_config()
                print("[APP] ✅ Configuração atualizada")
        except Exception as e:
            print(f"[APP] ❌ Erro na configuração: {e}")
    
    def _handle_quit(self):
        """Handle quit request."""
        print("[APP] 👋 Encerrando aplicação...")
        self._running = False
    
    def _shutdown(self):
        """Shutdown application."""
        print("[APP] 🛑 Encerrando serviços...")
        
        if hasattr(self._hotkey_manager, 'stop'):
            self._hotkey_manager.stop()
        
        if hasattr(self._notification_service, 'stop'):
            self._notification_service.stop()
        
        print("[APP] ✅ Aplicação encerrada")