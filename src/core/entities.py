"""Domain entities - pure business objects without external dependencies."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import time


@dataclass
class TTSRequest:
    """Represents a text-to-speech request."""
    text: str
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    member_id: Optional[int] = None


@dataclass
class TTSConfig:
    """TTS engine configuration."""
    engine: str = 'gtts'  # 'gtts' or 'pyttsx3'
    language: str = 'pt'
    voice_id: str = 'roa/pt-br'
    rate: int = 180
    output_device: Optional[str] = None


@dataclass
class AudioFile:
    """Represents an audio file path."""
    path: str


class AudioQueueItemStatus(str, Enum):
    """Status of an audio queue item."""
    PENDING = "pending"           # Aguardando processamento
    PROCESSING = "processing"     # Sendo processado
    COMPLETED = "completed"       # Concluído com sucesso
    FAILED = "failed"            # Falhou


@dataclass
class AudioQueueItem:
    """Represents an item in the audio queue.
    
    Tracks a TTS request through the processing pipeline,
    supporting queue-based execution for multiple users.
    """
    request: TTSRequest
    item_id: str = field(default_factory=lambda: f"audio_{int(time.time() * 1000)}")
    status: AudioQueueItemStatus = AudioQueueItemStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    position_in_queue: int = 0  # Posição na fila (0 = próximo a processar)
    
    def mark_processing(self):
        """Mark item as currently being processed."""
        self.status = AudioQueueItemStatus.PROCESSING
        self.started_at = time.time()
    
    def mark_completed(self):
        """Mark item as successfully completed."""
        self.status = AudioQueueItemStatus.COMPLETED
        self.completed_at = time.time()
    
    def mark_failed(self, error: str):
        """Mark item as failed with error message.
        
        Args:
            error: Error description
        """
        self.status = AudioQueueItemStatus.FAILED
        self.error_message = error
        self.completed_at = time.time()
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0.0
    
    @property
    def wait_time_seconds(self) -> float:
        """Get time waited in queue before processing."""
        if self.started_at:
            return self.started_at - self.created_at
        return time.time() - self.created_at
