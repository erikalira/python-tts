# Generated Application Diagram

Automatic class diagram for reusable use cases and orchestration in `src.application`.

```mermaid
classDiagram
  class CheckDesktopBotConnectionUseCase {
    execute() DesktopBotActionResultDTO
  }
  class ConfigureTTSResult {
    config : Optional[TTSConfigurationData]
    guild_id : Optional[int]
    message : Optional[str]
    success : bool
  }
  class ConfigureTTSUseCase {
    get_config(guild_id: int) ConfigureTTSResult
    update_config_async(guild_id: int, engine: Optional[str], language: Optional[str], voice_id: Optional[str], rate: Optional[int]) ConfigureTTSResult
  }
  class DesktopBotActionResultDTO {
    message : str
    success : bool
  }
  class DesktopBotConnectionStatusDTO {
    message : str
    success : bool
  }
  class DesktopBotGateway {
    check_connection()* DesktopBotConnectionStatusDTO
    fetch_voice_context()* DesktopBotVoiceContextStatusDTO
    get_last_error_message()* Optional[str]
    has_bot_url()* bool
    has_member_id()* bool
    send_text(text: str)* bool
  }
  class DesktopBotVoiceContextResultDTO {
    channel_name : str | None
    guild_name : str | None
  }
  class DesktopBotVoiceContextStatusDTO {
    channel_id : int | None
    channel_name : str | None
    guild_id : int | None
    guild_name : str | None
    message : str
    success : bool
  }
  class DesktopConfigurationSaveResultDTO {
    message : str
    success : bool
  }
  class DesktopTTSExecutionPort {
    get_last_error_message()* str | None
    get_status_info()* dict[str, Any]
    is_available()* bool
    speak_text(text: str)* bool
  }
  class DesktopTTSFlowService {
    get_last_error_message() str | None
    is_available() bool
    speak_text(text: str | None) bool
  }
  class DesktopTTSStatusGateway {
    has_bot_url()* bool
    has_transport()* bool
    is_local_available()* bool
    is_local_dependency_installed()* bool
    is_local_enabled()* bool
    is_remote_available()* bool
  }
  class DesktopTTSStatusUseCase {
    execute() dict
  }
  class DiscordSpeakPreparationResult {
    error_message : str | None
    request : SpeakTextInputDTO | None
  }
  class DiscordSpeakRequestBuilder {
    build() DiscordSpeakPreparationResult
  }
  class FetchDesktopBotVoiceContextUseCase {
    execute() DesktopBotVoiceContextResultDTO
  }
  class GetCurrentVoiceContextUseCase {
    execute(query: VoiceContextQueryDTO) VoiceContextResult
  }
  class JoinVoiceChannelResult {
    code : str
    error_detail : Optional[str]
    success : bool
  }
  class JoinVoiceChannelUseCase {
    execute(guild_id: Optional[int], member_id: Optional[int]) JoinVoiceChannelResult
  }
  class LeaveVoiceChannelResult {
    code : str
    error_detail : Optional[str]
    success : bool
  }
  class LeaveVoiceChannelUseCase {
    execute(guild_id: Optional[int]) LeaveVoiceChannelResult
  }
  class ResultBase {
  }
  class SendDesktopBotTestMessageUseCase {
    execute() DesktopBotActionResultDTO
  }
  class SpeakTextExecutionUseCase {
    execute(text: str | None) TTSExecutionResult
    get_status_info() dict
    is_available() bool
  }
  class SpeakTextInputDTO {
    channel_id : int | None
    config_override : TTSConfig | None
    guild_id : int | None
    member_id : int | None
    text : str
  }
  class SpeakTextResult {
    code : str
    error_detail : Optional[str]
    item_id : Optional[str]
    position : Optional[int]
    queue_size : Optional[int]
    queued : bool
    success : bool
  }
  class SpeakTextUseCase {
    execute(request: SpeakTextInputDTO) SpeakTextResult
  }
  class TTSCatalog {
    find_voice_option()* TTSVoiceOption | None
    get_voice_option(key: str)* TTSVoiceOption | None
    is_voice_available()* bool
    list_voice_options()* list[TTSVoiceOption]
  }
  class TTSConfigurationData {
    engine : str
    language : str
    rate : int
    voice_id : str
  }
  class TTSEnginePort {
    get_last_error_message()* str | None
    is_available()* bool
    speak(text: str)* bool
  }
  class TTSExecutionResult {
    code : str
    message : str | None
    success : bool
  }
  class TTSFallbackChain {
    get_last_error_message() str | None
    is_available() bool
    speak(text: str) bool
  }
  class TTSQueueOrchestrator {
    is_processing(guild_id: Optional[int]) bool
    start_processing_for_item(guild_id: Optional[int]) SpeakTextResult
  }
  class TTSVoiceOption {
    engine : str
    key : str
    label : str
    language : str
    voice_id : str
  }
  class VoiceChannelResolution {
    channel : IVoiceChannel
    channel_changed : bool
  }
  class VoiceChannelResolutionService {
    infer_guild_id(request: TTSRequest) Optional[int]
    is_member_in_channel(member_id: int, channel: IVoiceChannel) bool
    resolve_for_request(request: TTSRequest) Optional[VoiceChannelResolution]
  }
  class VoiceContextQueryDTO {
    member_id : int | None
  }
  class VoiceContextResult {
    channel_id : Optional[int]
    channel_name : Optional[str]
    code : str
    guild_id : Optional[int]
    guild_name : Optional[str]
    member_id : Optional[int]
    success : bool
  }
  class VoiceRuntimeAvailability {
    get_status()* VoiceRuntimeStatus
  }
  class VoiceRuntimeStatus {
    davey_installed : bool
    ffmpeg_available : bool
    is_available : bool
    pynacl_installed : bool
    missing_dependencies() list[str]
  }
  DesktopBotVoiceContextResultDTO --|> DesktopBotActionResultDTO
  ConfigureTTSResult --|> ResultBase
  JoinVoiceChannelResult --|> ResultBase
  LeaveVoiceChannelResult --|> ResultBase
  SpeakTextResult --|> ResultBase
  TTSConfigurationData --|> ResultBase
  VoiceContextResult --|> ResultBase
```
