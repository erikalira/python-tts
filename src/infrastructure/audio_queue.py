"""Audio queue implementation for handling multiple users per guild."""
import asyncio
import logging
from typing import Optional, Dict, List
from src.core.interfaces import IAudioQueue
from src.core.entities import AudioQueueItem, AudioQueueItemStatus
import time

logger = logging.getLogger(__name__)


class InMemoryAudioQueue(IAudioQueue):
    """In-memory audio queue per guild for safe multi-user handling.
    
    Maintains separate queues per guild to support multiple Discord servers.
    Uses asyncio.Lock for thread-safe operations.
    """
    
    def __init__(self, max_queue_size: int = 50, max_queue_wait_seconds: int = 3600):
        """Initialize queue structure.
        
        Args:
            max_queue_size: Maximum items per guild queue (prevents spam)
            max_queue_wait_seconds: Max wait time before auto-removal (1 hour default)
        """
        # Structure: {guild_id: [AudioQueueItem, ...]}
        self._queues: Dict[Optional[int], List[AudioQueueItem]] = {}
        self._lock = asyncio.Lock()
        self._max_queue_size = max_queue_size
        self._max_queue_wait = max_queue_wait_seconds
    
    async def enqueue(self, item: AudioQueueItem) -> Optional[str]:
        """Add item to queue for its guild.
        
        Returns:
            item_id: Unique identifier for this audio request, or None if rejected
        """
        async with self._lock:
            guild_id = item.request.guild_id
            
            if guild_id not in self._queues:
                self._queues[guild_id] = []
            
            queue = self._queues[guild_id]
            
            # Validate queue size
            if len(queue) >= self._max_queue_size:
                logger.warning(f"[QUEUE] Guild {guild_id} queue full ({self._max_queue_size} items)")
                item.mark_failed("Fila de áudio cheia. Tente novamente mais tarde.")
                return None
            
            # Update position
            item.position_in_queue = len(queue)
            queue.append(item)
            
            logger.info(f"[QUEUE] Item {item.item_id} enqueued to guild {guild_id}, position: {item.position_in_queue}, from user {item.request.member_id}")
            return item.item_id
    
    async def dequeue(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        """Remove and return next item from queue.
        
        Args:
            guild_id: Guild to get item from
            
        Returns:
            Next AudioQueueItem or None if queue empty
        """
        async with self._lock:
            if guild_id not in self._queues or not self._queues[guild_id]:
                return None
            
            queue = self._queues[guild_id]
            item = queue.pop(0)
            
            # Update positions for remaining items
            for i, remaining_item in enumerate(queue):
                remaining_item.position_in_queue = i
            
            logger.info(f"[QUEUE] Item {item.item_id} dequeued from guild {guild_id}, user {item.request.member_id}")
            return item
    
    async def peek_next(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        """Look at next item without removing it.
        
        Args:
            guild_id: Guild to peek at
            
        Returns:
            Next AudioQueueItem or None if queue empty
        """
        async with self._lock:
            if guild_id not in self._queues or not self._queues[guild_id]:
                return None
            return self._queues[guild_id][0]
    
    async def get_queue_status(self, guild_id: Optional[int]) -> dict:
        """Get current queue status for a guild.
        
        Args:
            guild_id: Guild to get status for
            
        Returns:
            dict with queue size and items info
        """
        async with self._lock:
            if guild_id not in self._queues:
                return {"size": 0, "items": []}
            
            queue = self._queues[guild_id]
            items_info = [
                {
                    "id": item.item_id,
                    "user_id": item.request.member_id,
                    "status": item.status.value,
                    "position": item.position_in_queue,
                    "wait_time_seconds": round(item.wait_time_seconds, 1)
                }
                for item in queue
            ]
            
            return {
                "size": len(queue),
                "items": items_info
            }
    
    async def get_item_position(self, item_id: str) -> int:
        """Get position of specific item in any queue.
        
        Args:
            item_id: Item ID to search for
            
        Returns:
            Position (0-indexed) or -1 if not found
        """
        async with self._lock:
            for guild_queue in self._queues.values():
                for i, item in enumerate(guild_queue):
                    if item.item_id == item_id:
                        return i
            return -1
    
    async def clear_completed(self, guild_id: Optional[int], older_than_seconds: int = 3600):
        """Remove completed/failed items older than X seconds.
        
        Args:
            guild_id: Guild to clean up
            older_than_seconds: Age threshold for cleanup
        """
        async with self._lock:
            if guild_id not in self._queues:
                return
            
            now = time.time()
            queue = self._queues[guild_id]
            original_size = len(queue)
            
            # Keep only pending/processing or recent completed items
            self._queues[guild_id] = [
                item for item in queue
                if item.status in (AudioQueueItemStatus.PENDING, AudioQueueItemStatus.PROCESSING)
                or (item.completed_at and now - item.completed_at < older_than_seconds)
            ]
            
            removed = original_size - len(self._queues[guild_id])
            if removed > 0:
                logger.info(f"[QUEUE] Cleaned {removed} old items from guild {guild_id}")
