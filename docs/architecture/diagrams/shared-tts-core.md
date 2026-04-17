# Shared TTS Core

```mermaid
classDiagram
direction LR

class TTSConfig {
  +engine : str
  +language : str
  +voice_id : str
  +rate : int
  +output_device : Optional[str]
}
class TTSRequest {
  +text : str
  +channel_id : Optional[int]
  +guild_id : Optional[int]
  +member_id : Optional[int]
}
class AudioFile {
  +path : str
}
class AudioQueueItem {
  +item_id : str
  +status
  +error_message : Optional[str]
  +request
  +mark_processing()
  +mark_completed()
  +mark_failed(error: str)
}

class ITTSEngine {
  <<interface>>
  +generate_audio(text: str, config: TTSConfig) AudioFile
}
class IVoiceChannel {
  <<interface>>
  +connect()
  +disconnect()
  +play_audio(audio: AudioFile)
  +is_connected() bool
}
class IVoiceChannelRepository {
  <<interface>>
  +find_by_member_id(member_id: int) Optional[IVoiceChannel]
  +find_by_channel_id(channel_id: int) Optional[IVoiceChannel]
  +find_by_guild_id(guild_id: Optional[int]) Optional[IVoiceChannel]
  +find_connected_channel() Optional[IVoiceChannel]
}
class IConfigRepository {
  <<interface>>
  +get_config(guild_id: Optional[int]) TTSConfig
  +load_config_async(guild_id: Optional[int]) TTSConfig
  +save_config_async(guild_id: int, config: TTSConfig) bool
}
class IAudioQueue {
  <<interface>>
  +enqueue(item: AudioQueueItem) Optional[str]
  +dequeue(guild_id: Optional[int]) Optional[AudioQueueItem]
  +peek_next(guild_id: Optional[int]) Optional[AudioQueueItem]
  +get_queue_status(guild_id: Optional[int]) dict
}
class IAudioFileCleanup {
  <<interface>>
  +cleanup(audio: AudioFile)
}

class SpeakTextUseCase {
  +execute(request: TTSRequest) SpeakTextResult
}
class TTSQueueOrchestrator {
  +is_processing(guild_id: Optional[int]) bool
  +start_processing_for_item(guild_id: Optional[int]) SpeakTextResult
}
class VoiceChannelResolutionService {
  +infer_guild_id(request: TTSRequest) Optional[int]
  +resolve_for_request(request: TTSRequest) Optional[VoiceChannelResolution]
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
class SpeakTextExecutionUseCase {
  +execute(text: str | None) TTSExecutionResult
  +is_available() bool
  +get_status_info() dict
}
class TTSExecutionResult {
  +success : bool
  +code : str
  +message : str | None
}
class VoiceChannelResolution {
  +channel
  +channel_changed : bool
}
class DesktopTTSExecutionPort {
  <<interface>>
  +speak_text(text: str) bool
  +is_available() bool
  +get_status_info() dict
  +get_last_error_message() str | None
}

AudioQueueItem --> TTSRequest
VoiceChannelResolution --> IVoiceChannel

SpeakTextUseCase --> TTSRequest
SpeakTextUseCase --> AudioQueueItem
SpeakTextUseCase --> IVoiceChannelRepository
SpeakTextUseCase --> IAudioQueue
SpeakTextUseCase --> VoiceChannelResolutionService
SpeakTextUseCase --> TTSQueueOrchestrator

TTSQueueOrchestrator --> ITTSEngine
TTSQueueOrchestrator --> IConfigRepository
TTSQueueOrchestrator --> IAudioQueue
TTSQueueOrchestrator --> IAudioFileCleanup
TTSQueueOrchestrator --> VoiceChannelResolutionService
TTSQueueOrchestrator --> AudioFile
TTSQueueOrchestrator --> AudioQueueItem

VoiceChannelResolutionService --> IVoiceChannelRepository
VoiceChannelResolutionService --> TTSRequest
VoiceChannelResolutionService --> VoiceChannelResolution

ConfigureTTSUseCase --> IConfigRepository
JoinVoiceChannelUseCase --> IVoiceChannelRepository
LeaveVoiceChannelUseCase --> IVoiceChannelRepository
GetCurrentVoiceContextUseCase --> IVoiceChannelRepository

SpeakTextExecutionUseCase --> DesktopTTSExecutionPort
SpeakTextExecutionUseCase --> TTSExecutionResult
```

## Notes

- `SpeakTextUseCase` is the main shared bot TTS entrypoint.
- `TTSQueueOrchestrator` owns queued playback orchestration.
- `SpeakTextExecutionUseCase` is a shared desktop-oriented use case that depends on an explicit execution port.
