# Layer Overview

```mermaid
classDiagram
direction LR

class TTSConfig
class TTSRequest
class AudioFile
class AudioQueueItem
class ITTSEngine
class IVoiceChannel
class IVoiceChannelRepository
class IConfigRepository
class IAudioQueue
class IAudioFileCleanup

class SpeakTextUseCase
class TTSQueueOrchestrator
class VoiceChannelResolutionService
class ConfigureTTSUseCase
class JoinVoiceChannelUseCase
class LeaveVoiceChannelUseCase
class GetCurrentVoiceContextUseCase
class SpeakTextExecutionUseCase
class DesktopTTSExecutionPort

class DiscordVoiceChannelRepository
class InMemoryAudioQueue
class GuildConfigRepository
class GTTSEngine
class Pyttsx3Engine
class FileAudioCleanup
class HTTPServer

class DiscordCommands
class SpeakController
class VoiceContextController

class DesktopApp
class DesktopAppMainWindow
class DesktopAppTTSService
class HotkeyManager
class SystemTrayService

SpeakTextUseCase --> IVoiceChannelRepository
SpeakTextUseCase --> IAudioQueue
SpeakTextUseCase --> VoiceChannelResolutionService
SpeakTextUseCase --> TTSQueueOrchestrator
TTSQueueOrchestrator --> ITTSEngine
TTSQueueOrchestrator --> IConfigRepository
TTSQueueOrchestrator --> IAudioQueue
TTSQueueOrchestrator --> IAudioFileCleanup
VoiceChannelResolutionService --> IVoiceChannelRepository

DiscordVoiceChannelRepository ..|> IVoiceChannelRepository
InMemoryAudioQueue ..|> IAudioQueue
GuildConfigRepository ..|> IConfigRepository
GTTSEngine ..|> ITTSEngine
Pyttsx3Engine ..|> ITTSEngine
FileAudioCleanup ..|> IAudioFileCleanup

DiscordCommands --> SpeakTextUseCase
DiscordCommands --> JoinVoiceChannelUseCase
DiscordCommands --> LeaveVoiceChannelUseCase
SpeakController --> SpeakTextUseCase
VoiceContextController --> GetCurrentVoiceContextUseCase

DesktopApp --> DesktopAppMainWindow
DesktopApp --> HotkeyManager
DesktopApp --> SystemTrayService
DesktopApp --> SpeakTextExecutionUseCase
SpeakTextExecutionUseCase --> DesktopTTSExecutionPort
DesktopAppTTSService ..|> DesktopTTSExecutionPort
```

## Notes

- `core` owns shared entities and contracts.
- `application` coordinates reusable flows.
- `infrastructure` implements ports and external adapters.
- `presentation` delegates to application use cases.
- `desktop` is runtime-specific and should reuse shared logic rather than duplicating it.
