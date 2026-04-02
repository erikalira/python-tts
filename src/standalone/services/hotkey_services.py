#!/usr/bin/env python3
"""
Hotkey Services Module - Clean Architecture
Provides keyboard monitoring and hotkey detection services.
"""

import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional, Protocol
from dataclasses import dataclass

from ..config.standalone_config import StandaloneConfig
from ..adapters.keyboard_backend import KeyboardHookBackend, is_keyboard_backend_available


@dataclass
class HotkeyEvent:
    """Event data for hotkey triggers."""
    text: str
    character_count: int
    trigger_open: str
    trigger_close: str


class HotkeyHandler(Protocol):
    """Protocol for handling hotkey events."""
    
    def handle_text_captured(self, event: HotkeyEvent) -> None:
        """Handle when text is captured between hotkey triggers."""
        ...


class KeyboardMonitor(ABC):
    """Abstract interface for keyboard monitoring."""
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """Start keyboard monitoring. Returns True if successful."""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop keyboard monitoring."""
        pass
    
    @abstractmethod
    def is_monitoring(self) -> bool:
        """Check if currently monitoring keyboard."""
        pass


class StandardKeyboardMonitor(KeyboardMonitor):
    """Keyboard monitor using the keyboard library."""
    
    def __init__(self, config: StandaloneConfig, handler: HotkeyHandler, backend: Optional[KeyboardHookBackend] = None):
        self._config = config
        self._handler = handler
        self._backend = backend or KeyboardHookBackend()
        self._recording = False
        self._buffer: list[str] = []
        self._monitoring = False
        self._lock = threading.Lock()
        
        # Track suppression state from external sources
        self._external_suppression_check: Optional[Callable[[], bool]] = None
    
    def set_external_suppression_check(self, check_func: Callable[[], bool]) -> None:
        """Set function to check if events should be suppressed externally."""
        self._external_suppression_check = check_func
    
    def start_monitoring(self) -> bool:
        """Start monitoring keyboard events."""
        if not self._backend.is_available():
            print("[HOTKEY] ❌ Biblioteca 'keyboard' não disponível")
            return False
        
        if self._monitoring:
            return True
        
        try:
            if not self._backend.is_available():
                return False
            self._backend.hook(self._on_key_event)
            self._monitoring = True
            print(f"[HOTKEY] ✅ Monitoramento iniciado - Use {self._config.hotkey.trigger_open}texto{self._config.hotkey.trigger_close}")
            return True
        except Exception as e:
            print(f"[HOTKEY] ❌ Erro ao iniciar monitoramento: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Stop monitoring keyboard events."""
        if self._backend.is_available() and self._monitoring:
            try:
                self._backend.unhook_all()
                self._monitoring = False
                print("[HOTKEY] 🛑 Monitoramento parado")
            except Exception as e:
                print(f"[HOTKEY] ⚠️ Erro ao parar monitoramento: {e}")
    
    def is_monitoring(self) -> bool:
        """Check if currently monitoring."""
        return self._monitoring
    
    def _is_suppressed(self) -> bool:
        """Check if events should be suppressed."""
        return bool(self._external_suppression_check and 
                    self._external_suppression_check())
    
    def _on_key_event(self, event) -> None:
        """Handle keyboard events."""
        if not self._backend.is_available():
            return
        if event.event_type != self._backend.key_down_event:
            return
        
        if self._is_suppressed():
            return
        
        key = event.name
        
        with self._lock:
            self._process_key(key)
    
    def _process_key(self, key: str) -> None:
        """Process individual key presses."""
        # Check for trigger open
        if self._is_trigger_open(key):
            self._recording = True
            self._buffer = []
            return
        
        if self._recording:
            # Check for trigger close
            if self._is_trigger_close(key):
                self._recording = False
                text = ''.join(self._buffer).strip()
                
                if text:
                    # Calculate backspace count (text + 2 triggers)
                    backspace_count = len(self._buffer) + 2
                    
                    event = HotkeyEvent(
                        text=text,
                        character_count=backspace_count,
                        trigger_open=self._config.hotkey.trigger_open,
                        trigger_close=self._config.hotkey.trigger_close
                    )
                    
                    self._handler.handle_text_captured(event)
                
                self._buffer = []
                return
            
            # Handle special keys during recording
            if key in ('backspace', 'back'):
                if self._buffer:
                    self._buffer.pop()
                return
            
            # Add character to buffer
            if key == 'space':
                self._buffer.append(' ')
            elif len(key) == 1:  # Regular character
                self._buffer.append(key)
    
    def _is_trigger_open(self, key: str) -> bool:
        """Check if key is the opening trigger."""
        trigger = self._config.hotkey.trigger_open
        return key in (trigger, 'open_bracket', 'left_bracket', 'braceleft')
    
    def _is_trigger_close(self, key: str) -> bool:
        """Check if key is the closing trigger."""
        trigger = self._config.hotkey.trigger_close
        return key in (trigger, 'close_bracket', 'right_bracket', 'braceright')


class HotkeyService:
    """Main hotkey service that coordinates monitoring and handling."""
    
    def __init__(
        self,
        config: StandaloneConfig,
        handler: HotkeyHandler,
        monitor_factory: Callable[[StandaloneConfig, HotkeyHandler], KeyboardMonitor] | None = None
    ):
        self._config = config
        self._handler = handler
        self._monitor_factory = monitor_factory or (lambda cfg, hnd: StandardKeyboardMonitor(cfg, hnd))
        self._monitor: KeyboardMonitor = self._monitor_factory(config, handler)
        self._active = False
    
    def start(self) -> bool:
        """Start the hotkey service."""
        if self._active:
            return True
        
        success = self._monitor.start_monitoring()
        if success:
            self._active = True
            self._log_startup_info()
        
        return success
    
    def stop(self) -> None:
        """Stop the hotkey service."""
        if self._active:
            self._monitor.stop_monitoring()
            self._active = False
    
    def is_active(self) -> bool:
        """Check if the hotkey service is active."""
        return self._active and self._monitor.is_monitoring()
    
    def set_external_suppression_check(self, check_func: Callable[[], bool]) -> None:
        """Set function to check if events should be suppressed."""
        if isinstance(self._monitor, StandardKeyboardMonitor):
            self._monitor.set_external_suppression_check(check_func)
    
    def _log_startup_info(self) -> None:
        """Log startup information."""
        print("[HOTKEY] 🎯 Triggers configurados:")
        print(f"[HOTKEY]    Iniciar: '{self._config.hotkey.trigger_open}'")
        print(f"[HOTKEY]    Finalizar: '{self._config.hotkey.trigger_close}'")
        print(f"[HOTKEY] 📝 Exemplo: {self._config.hotkey.trigger_open}olá mundo{self._config.hotkey.trigger_close}")
    
    def get_status(self) -> dict:
        """Get status information about the hotkey service."""
        return {
            'active': self._active,
            'monitoring': self._monitor.is_monitoring(),
            'keyboard_available': is_keyboard_backend_available(),
            'trigger_open': self._config.hotkey.trigger_open,
            'trigger_close': self._config.hotkey.trigger_close
        }


class HotkeyManager:
    """High-level manager for hotkey functionality."""
    
    def __init__(
        self,
        config: StandaloneConfig,
        service_factory: Callable[[StandaloneConfig, HotkeyHandler], HotkeyService] | None = None
    ):
        self._config = config
        self._service_factory = service_factory or (lambda cfg, handler: HotkeyService(cfg, handler))
        self._service: Optional[HotkeyService] = None
        self._handler: Optional[HotkeyHandler] = None
    
    def initialize(self, handler: HotkeyHandler) -> bool:
        """Initialize the hotkey manager with a handler."""
        if self._service:
            return True
        
        self._handler = handler
        self._service = self._service_factory(self._config, handler)
        return True
    
    def start(self) -> bool:
        """Start hotkey monitoring."""
        if not self._service:
            print("[HOTKEY] ❌ HotkeyManager não foi inicializado")
            return False
        
        return self._service.start()
    
    def stop(self) -> None:
        """Stop hotkey monitoring."""
        if self._service:
            self._service.stop()
    
    def is_active(self) -> bool:
        """Check if hotkey monitoring is active."""
        return self._service.is_active() if self._service else False
    
    def set_external_suppression_check(self, check_func: Callable[[], bool]) -> None:
        """Set function to check if events should be suppressed."""
        if self._service:
            self._service.set_external_suppression_check(check_func)
    
    def update_config(self, new_config: StandaloneConfig) -> None:
        """Update configuration and restart service if active."""
        was_active = self.is_active()
        
        if was_active:
            self.stop()
        
        self._config = new_config
        
        if was_active and self._handler:
            self._service = self._service_factory(new_config, self._handler)
            self.start()
    
    def get_status(self) -> dict:
        """Get comprehensive status information."""
        if not self._service:
            return {
                'initialized': False,
                'active': False,
                'keyboard_available': is_keyboard_backend_available()
            }
        
        status = self._service.get_status()
        status['initialized'] = True
        return status
