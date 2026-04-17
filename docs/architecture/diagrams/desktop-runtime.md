# Desktop Runtime

```mermaid
classDiagram
direction LR

class DesktopMain {
  +main()
}
class DesktopApp {
  +initialize() bool
  +run()
}

class DesktopAppConfig {
  +tts
  +discord
  +hotkey
  +interface
  +network
  +create_default() DesktopAppConfig
}
class ConfigurationRepository {
  +load() DesktopAppConfig
  +save(config: DesktopAppConfig) bool
}
class ConfigurationService {
  +prefer_gui : bool
  +get_configuration(current_config: DesktopAppConfig) Optional[DesktopAppConfig]
}

class DesktopConfigurationCoordinator {
  +handle_initial_configuration(current_config: DesktopAppConfig) tuple[bool, DesktopAppConfig]
  +save_from_ui(updated_config: DesktopAppConfig) DesktopConfigurationSaveResult
  +reconfigure(current_config: DesktopAppConfig, hotkeys_were_active: bool, resume_hotkeys, notify_error, notify_success, are_hotkeys_active) tuple[Optional[DesktopAppConfig], bool]
}
class DesktopConfigurationApplicationService {
  +is_configured(config: DesktopAppConfig) bool
  +validate(config: DesktopAppConfig) tuple[bool, list[str]]
  +apply(config: DesktopAppConfig) bool
}
class DesktopAppLifecycleCoordinator {
  +start_services(hotkey_manager, notification_service) bool
  +run_main_loop(show_main_window, notification_service, process_pending_ui_action, is_running, shutdown_requested, console_wait_factory)
  +update_services_config(...) tuple[object, object | None]
  +shutdown(...) bool
}
class DesktopAppUIRuntimeCoordinator {
  +action_queue
  +main_window
  +show_main_window(config: DesktopAppConfig, on_save, on_test_connection, on_send_test, on_refresh_voice_context)
  +show_status(get_status, notification_service)
  +handle_configure(ensure_action_coordinators, hotkey_manager, get_configuration_coordinator, current_config, notification_service)
  +queue(action)
  +drain_queued_actions()
}
class DesktopAppTTSProcessor {
  +process_text(text: str, cleanup_count: int, on_complete)
  +is_processing() bool
  +get_service_status() dict
}
class DesktopAppTTSResultPresenter {
  +show_processing(text: str)
  +present(result: TTSExecutionResult)
}
class DesktopAppHotkeyHandler {
  +handle_text_captured(event: HotkeyEvent)
}

class DesktopAppMainWindow {
  +config
  +root
  +show()
  +focus()
  +hide_to_tray()
  +push_log(message: str)
}

class HotkeyManager {
  +initialize(handler: HotkeyHandler) bool
  +start() bool
  +stop()
  +is_active() bool
  +set_external_suppression_check(check_func)
  +update_config(new_config: DesktopAppConfig)
}
class SystemTrayService {
  +initialize(status_click, configure, quit_handler)
  +start() bool
  +stop()
  +is_available() bool
  +is_running() bool
  +notify_info(title: str, message: str)
  +notify_success(title: str, message: str)
  +notify_error(title: str, message: str)
}
class DesktopAppTTSService {
  +speak_text(text: str) bool
  +is_available() bool
  +get_status_info() dict
  +is_remote_available() bool
  +is_local_enabled() bool
  +is_local_available() bool
  +has_transport() bool
  +has_bot_url() bool
  +get_last_error_message() str | None
}
class KeyboardCleanupService {
  +cleanup_typed_text(backspace_count: int)
  +is_suppressing_events() bool
}
class HttpDiscordBotClient {
  +check_connection() DesktopBotConnectionStatus
  +send_text(text: str) bool
  +fetch_voice_context() DesktopBotVoiceContextStatus
  +has_bot_url() bool
  +has_member_id() bool
  +has_transport() bool
  +get_last_error_message() Optional[str]
}

class CheckDesktopBotConnectionUseCase {
  +execute() DesktopBotActionResult
}
class SendDesktopBotTestMessageUseCase {
  +execute() DesktopBotActionResult
}
class FetchDesktopBotVoiceContextUseCase {
  +execute() DesktopBotVoiceContextResult
}
class SpeakTextExecutionUseCase {
  +execute(text: str | None) TTSExecutionResult
  +is_available() bool
  +get_status_info() dict
}
class DesktopTTSExecutionPort {
  <<interface>>
  +speak_text(text: str) bool
  +is_available() bool
  +get_status_info() dict
  +get_last_error_message() str | None
}

DesktopMain --> DesktopApp
DesktopApp --> ConfigurationRepository
DesktopApp --> ConfigurationService
DesktopApp --> DesktopConfigurationCoordinator
DesktopApp --> DesktopAppLifecycleCoordinator
DesktopApp --> DesktopAppUIRuntimeCoordinator
DesktopApp --> DesktopAppTTSProcessor
DesktopApp --> HotkeyManager
DesktopApp --> SystemTrayService

DesktopConfigurationCoordinator --> ConfigurationService
DesktopConfigurationCoordinator --> DesktopConfigurationApplicationService
DesktopConfigurationApplicationService --> ConfigurationRepository

DesktopAppUIRuntimeCoordinator --> DesktopAppMainWindow

DesktopApp --> CheckDesktopBotConnectionUseCase
DesktopApp --> SendDesktopBotTestMessageUseCase
DesktopApp --> FetchDesktopBotVoiceContextUseCase
DesktopApp --> HttpDiscordBotClient

DesktopAppTTSProcessor --> SpeakTextExecutionUseCase
DesktopAppTTSProcessor --> KeyboardCleanupService
DesktopAppHotkeyHandler --> DesktopAppTTSProcessor
DesktopAppHotkeyHandler --> DesktopAppTTSResultPresenter
DesktopAppTTSResultPresenter --> SystemTrayService

SpeakTextExecutionUseCase --> DesktopTTSExecutionPort
DesktopAppTTSService ..|> DesktopTTSExecutionPort
```

## Notes

- `DesktopApp` is intentionally larger because it owns startup and shutdown orchestration.
- `DesktopAppUIRuntimeCoordinator` owns queued UI actions and main-window lifecycle.
- Desktop bot communication now flows directly through explicit use cases plus `HttpDiscordBotClient`.
