# Bot Runtime

```mermaid
classDiagram
direction LR

class BotMain {
  +main()
  +run()
}
class Container {
  +config
  +config_repository
  +voice_channel_repository
  +audio_queue
  +tts_engine_factory
  +tts_engine
  +tts_queue_orchestrator
  +speak_use_case
  +config_use_case
  +join_use_case
  +leave_use_case
  +voice_context_use_case
  +speak_controller
  +voice_context_controller
  +discord_commands
}
class Config {
  +discord_token
  +http_host
  +http_port : int
  +max_text_length : int
  +tts_config
  +validate() tuple[bool, str]
}

class DiscordCommands {
  +_handle_join(interaction)
  +_handle_leave(interaction)
  +_handle_speak(interaction, text: str)
  +_handle_config(interaction, voz, idioma, sotaque)
  +_handle_about(interaction)
}
class DiscordConfigCommandHandler {
  +handle(interaction, voz, idioma, sotaque)
}
class DiscordAboutCommandHandler {
  +handle(interaction, runtime_status)
}
class DiscordSpeakPresenter {
  +build_message(result: SpeakTextResult) str
}
class DiscordJoinPresenter {
  +build_message(result: JoinVoiceChannelResult) str
}
class DiscordLeavePresenter {
  +build_message(result: LeaveVoiceChannelResult) str
}
class SpeakController {
  +handle(request) Response
}
class VoiceContextController {
  +handle(request) Response
}

class SpeakTextUseCase {
  +execute(request: TTSRequest) SpeakTextResult
}
class ConfigureTTSUseCase {
  +get_config(guild_id: int) ConfigureTTSResult
  +update_config_async(guild_id: int, engine, language, voice_id, rate) ConfigureTTSResult
}
class JoinVoiceChannelUseCase {
  +execute(guild_id: Optional[int], member_id: Optional[int]) JoinVoiceChannelResult
}
class LeaveVoiceChannelUseCase {
  +execute(guild_id: Optional[int]) LeaveVoiceChannelResult
}
class GetCurrentVoiceContextUseCase {
  +execute(member_id: Optional[int]) VoiceContextResult
}
class TTSQueueOrchestrator {
  +is_processing(guild_id: Optional[int]) bool
  +start_processing_for_item(guild_id: Optional[int]) SpeakTextResult
}
class VoiceChannelResolutionService {
  +infer_guild_id(request: TTSRequest) Optional[int]
  +resolve_for_request(request: TTSRequest) Optional[VoiceChannelResolution]
}

class HTTPServer {
  +start()
  +stop()
}
class DiscordVoiceChannelRepository {
  +find_by_member_id(member_id: int) Optional[IVoiceChannel]
  +find_by_channel_id(channel_id: int) Optional[IVoiceChannel]
  +find_by_guild_id(guild_id: Optional[int]) Optional[IVoiceChannel]
  +update_member_cache(member_id: int, channel)
}
class InMemoryAudioQueue {
  +enqueue(item: AudioQueueItem) Optional[str]
  +dequeue(guild_id: Optional[int]) Optional[AudioQueueItem]
  +peek_next(guild_id: Optional[int]) Optional[AudioQueueItem]
  +get_queue_status(guild_id: Optional[int]) dict
}
class GuildConfigRepository {
  +get_config(guild_id: int) TTSConfig
  +load_config_async(guild_id: Optional[int]) TTSConfig
  +save_config_async(guild_id: int, config: TTSConfig) bool
}
class TTSEngineFactory {
  +create(config: TTSConfig) ITTSEngine
}
class FileAudioCleanup {
  +cleanup(audio: AudioFile)
}
class DependencyVoiceRuntimeAvailability {
  +get_status() VoiceRuntimeStatus
}

BotMain --> Config
BotMain --> Container
BotMain --> HTTPServer

Container --> GuildConfigRepository
Container --> DiscordVoiceChannelRepository
Container --> InMemoryAudioQueue
Container --> FileAudioCleanup
Container --> TTSEngineFactory
Container --> VoiceChannelResolutionService
Container --> TTSQueueOrchestrator
Container --> SpeakTextUseCase
Container --> ConfigureTTSUseCase
Container --> JoinVoiceChannelUseCase
Container --> LeaveVoiceChannelUseCase
Container --> GetCurrentVoiceContextUseCase
Container --> SpeakController
Container --> VoiceContextController
Container --> DiscordCommands
Container --> DependencyVoiceRuntimeAvailability

DiscordCommands --> SpeakTextUseCase
DiscordCommands --> ConfigureTTSUseCase
DiscordCommands --> JoinVoiceChannelUseCase
DiscordCommands --> LeaveVoiceChannelUseCase
DiscordCommands --> DependencyVoiceRuntimeAvailability
DiscordCommands --> DiscordConfigCommandHandler
DiscordCommands --> DiscordAboutCommandHandler
DiscordCommands --> DiscordSpeakPresenter
DiscordCommands --> DiscordJoinPresenter
DiscordCommands --> DiscordLeavePresenter

SpeakController --> SpeakTextUseCase
VoiceContextController --> GetCurrentVoiceContextUseCase
HTTPServer --> SpeakController
HTTPServer --> VoiceContextController
```

## Notes

- `Container` is a composition root, so its many edges represent wiring rather than domain coupling.
- The important architectural handoff is from presentation into shared use cases.
