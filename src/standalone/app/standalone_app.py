#!/usr/bin/env python3
"""
Standalone Application - Clean Architecture
Main application that orchestrates all services following SOLID principles.
"""

from typing import Optional

from ..config.standalone_config import (
    StandaloneConfig, 
    ConfigurationRepository, 
    EnvironmentUpdater, 
    ConfigurationValidator
)
from ..gui.simple_gui import ConfigurationService
from ..services.tts_services import TTSProcessor
from ..services.hotkey_services import (
    HotkeyManager,
    HotkeyEvent,
    HotkeyHandler
)
from ..services.notification_services import SystemTrayService


class StandaloneHotkeyHandler:
    """Hotkey handler that integrates TTS processing with notifications."""
    
    def __init__(self, 
                 tts_processor: TTSProcessor,
                 notification_service: SystemTrayService):
        self._tts_processor = tts_processor
        self._notification_service = notification_service
    
    def handle_text_captured(self, event: HotkeyEvent) -> None:
        """Handle when text is captured between hotkey triggers."""
        if not event.text:
            return
        
        # Log the capture
        print(f"[APP] 📝 Texto capturado: '{event.text}'")
        
        # Notify start of processing
        self._notification_service.notify_info(
            "TTS Hotkey", 
            f"Processando: '{event.text[:50]}{'...' if len(event.text) > 50 else ''}'"
        )
        
        # Process the text
        self._tts_processor.process_text(event.text, event.character_count)


class StandaloneApplication:
    """Main standalone application class following Clean Architecture."""
    
    def __init__(self):
        # Core components
        self._config: Optional[StandaloneConfig] = None
        self._config_repository: Optional[ConfigurationRepository] = None
        
        # Services
        self._tts_processor: Optional[TTSProcessor] = None
        self._hotkey_manager: Optional[HotkeyManager] = None
        self._notification_service: Optional[SystemTrayService] = None
        
        # UI Services
        self._config_service: Optional[ConfigurationService] = None
        
        # Application state
        self._initialized = False
        self._running = False
    
    def initialize(self) -> bool:
        """Initialize all application components."""
        if self._initialized:
            return True
        
        try:
            # Initialize configuration
            self._config_repository = ConfigurationRepository()
            self._config = self._config_repository.load()
            
            # Initialize UI services
            self._config_service = ConfigurationService(prefer_gui=True)
            
            # Initialize core services
            self._tts_processor = TTSProcessor(self._config)
            self._hotkey_manager = HotkeyManager(self._config)
            self._notification_service = SystemTrayService(self._config)
            
            # Set up integrations
            self._setup_integrations()
            
            self._initialized = True
            print("[APP] ✅ Aplicação inicializada com sucesso")
            return True
            
        except Exception as e:
            print(f"[APP] ❌ Erro durante inicialização: {e}")
            return False
    
    def _setup_integrations(self) -> None:
        """Set up integrations between services."""
        # Create hotkey handler that bridges hotkey events to TTS
        hotkey_handler = StandaloneHotkeyHandler(
            self._tts_processor,
            self._notification_service
        )
        
        # Initialize hotkey manager with handler
        self._hotkey_manager.initialize(hotkey_handler)
        
        # Set up system tray callbacks
        self._notification_service.initialize(
            status_click=self._handle_status_click,
            configure=self._handle_configure,
            quit_handler=self._handle_quit
        )
        
        # Set up TTS processing suppression check
        self._hotkey_manager.set_external_suppression_check(
            lambda: self._tts_processor.is_processing()
        )
    
    def run(self) -> None:
        """Run the standalone application."""
        if not self._initialized:
            if not self.initialize():
                print("[APP] ❌ Falha na inicialização. Encerrando.")
                return
        
        try:
            # Check and handle first-time configuration
            if not self._handle_initial_configuration():
                print("[APP] ❌ Configuração cancelada. Encerrando.")
                return
            
            # Update environment variables
            EnvironmentUpdater.update_from_config(self._config)
            
            # Show current configuration
            self._show_current_configuration()
            
            # Start services
            if not self._start_services():
                print("[APP] ❌ Falha ao iniciar serviços. Encerrando.")
                return
            
            # Run main application loop
            self._run_main_loop()
            
        except KeyboardInterrupt:
            print("\n[APP] 🛑 Interrompido pelo usuário")
        except Exception as e:
            print(f"[APP] ❌ Erro durante execução: {e}")
        finally:
            self._shutdown()
    
    def _handle_initial_configuration(self) -> bool:
        """Handle initial configuration if needed."""
        if not ConfigurationValidator.is_configured(self._config):
            print("[APP] 🔧 Primeira execução detectada! Configurando...")
            
            updated_config = self._config_service.get_configuration(self._config)
            
            if not updated_config:
                return False
            
            # Save updated configuration
            self._config = updated_config
            if not self._config_repository.save(self._config):
                print("[APP] ⚠️ Falha ao salvar configuração, continuando com configuração temporária")
            
            # Update services with new configuration
            self._update_services_config()
        
        return True
    
    def _start_services(self) -> bool:
        """Start all application services."""
        print("[APP] 🚀 Iniciando serviços...")
        
        # Start hotkey monitoring
        if not self._hotkey_manager.start():
            print("[APP] ❌ Falha ao iniciar monitoramento de hotkey")
            return False
        
        # Start system tray (optional)
        tray_started = self._notification_service.start()
        if not tray_started:
            print("[APP] ⚠️ System tray não disponível, executando em modo console")
        
        self._running = True
        print("[APP] ✅ Todos os serviços iniciados")
        return True
    
    def _run_main_loop(self) -> None:
        """Run the main application loop."""
        tray_available = self._notification_service.is_available()
        
        if tray_available:
            # System tray handles the main loop
            print("[APP] 🎯 Executando com system tray...")
            # The tray.run() call is blocking and handles the main loop
        else:
            # Console mode - wait for keyboard interrupt
            print("[APP] ⌨️ Modo console ativo! Pressione Ctrl+C para sair...")
            try:
                import keyboard
                keyboard.wait()
            except ImportError:
                # Fallback if keyboard library is not available
                input("Pressione Enter para sair...")
    
    def _update_services_config(self) -> None:
        """Update all services with new configuration."""
        if self._tts_processor:
            self._tts_processor = TTSProcessor(self._config)
        
        if self._hotkey_manager:
            self._hotkey_manager.update_config(self._config)
        
        if self._notification_service:
            self._notification_service = SystemTrayService(self._config)
            self._setup_integrations()
    
    def _shutdown(self) -> None:
        """Gracefully shutdown all services."""
        print("[APP] 🛑 Encerrando aplicação...")
        
        if self._running:
            if self._hotkey_manager:
                self._hotkey_manager.stop()
            
            if self._notification_service:
                self._notification_service.stop()
            
            self._running = False
        
        print("[APP] ✅ Aplicação encerrada")
    
    # System tray callback handlers
    
    def _handle_status_click(self) -> None:
        """Handle system tray status click."""
        status = self._get_application_status()
        
        print("\n" + "="*50)
        print("📊 TTS Hotkey - Status")
        print("="*50)
        
        if status['discord_configured']:
            print(f"✅ Discord: {self._config.discord.bot_url}")
            print(f"👤 User ID: {self._config.discord.member_id}")
        else:
            print("⚠️ Discord não configurado completamente")
        
        print(f"🎯 Hotkeys: {'✅ Ativo' if status['hotkey_active'] else '❌ Inativo'}")
        print(f"🎤 TTS: {'✅ Disponível' if status['tts_available'] else '❌ Indisponível'}")
        
        print("="*50)
    
    def _handle_configure(self) -> None:
        """Handle system tray configure action."""
        print("[APP] 🔧 Abrindo configurações...")
        
        config_interface = self._config_ui_factory.create_interface()
        updated_config = config_interface.show_configuration_dialog(self._config)
        
        if updated_config:
            # Validate new configuration
            is_valid, errors = ConfigurationValidator.validate(updated_config)
            if not is_valid:
                print(f"[APP] ❌ Configuração inválida: {'; '.join(errors)}")
                return
            
            # Save and apply new configuration
            self._config = updated_config
            self._config_repository.save(self._config)
            
            # Update environment variables
            EnvironmentUpdater.update_from_config(self._config)
            
            # Update services
            self._update_services_config()
            
            print("[APP] ✅ Configuração atualizada com sucesso!")
        else:
            print("[APP] ℹ️ Configuração cancelada")
    
    def _handle_quit(self) -> None:
        """Handle system tray quit action."""
        print("[APP] 🛑 Encerrando via system tray...")
        self._shutdown()
        import os
        os._exit(0)
    
    def _get_application_status(self) -> dict:
        """Get comprehensive application status."""
        return {
            'initialized': self._initialized,
            'running': self._running,
            'discord_configured': (
                self._config and 
                self._config.discord.bot_url and 
                self._config.discord.member_id
            ),
            'hotkey_active': (
                self._hotkey_manager and 
                self._hotkey_manager.is_active()
            ),
            'tts_available': (
                self._tts_processor and 
                self._tts_processor.get_service_status()['tts_available']
            ),
            'tray_available': (
                self._notification_service and 
                self._notification_service.is_available()
            )
        }


def create_standalone_application() -> StandaloneApplication:
    """Factory function to create a standalone application instance."""
    return StandaloneApplication()


def main() -> None:
    """Main entry point for the standalone application."""
    app = create_standalone_application()
    app.run()


if __name__ == '__main__':
    main()