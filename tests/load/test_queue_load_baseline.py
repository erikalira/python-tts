import json
import os
import time
from pathlib import Path

import pytest

from src.core.entities import AudioQueueItem, TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue


@pytest.mark.asyncio
@pytest.mark.load
async def test_inmemory_queue_load_baseline_records_throughput():
    queue = InMemoryAudioQueue(max_queue_size=100)
    item_count = 75

    started = time.perf_counter()
    accepted = 0
    for index in range(item_count):
        item = AudioQueueItem(
            request=TTSRequest(
                text=f"load-test-{index}",
                guild_id=1,
                member_id=index,
            )
        )
        if await queue.enqueue(item) is not None:
            accepted += 1
    elapsed_seconds = max(time.perf_counter() - started, 0.000001)

    status = await queue.get_queue_status(1)
    throughput = accepted / elapsed_seconds
    report = {
        "queue": "inmemory",
        "items_attempted": item_count,
        "items_accepted": accepted,
        "elapsed_seconds": elapsed_seconds,
        "enqueue_per_second": throughput,
        "queue_size": status.size,
    }
    _write_report(report)

    assert accepted == item_count
    assert status.size == item_count
    assert throughput > 0


@pytest.mark.asyncio
@pytest.mark.load
async def test_inmemory_queue_load_baseline_records_backpressure():
    queue = InMemoryAudioQueue(max_queue_size=3)
    accepted = []

    for index in range(4):
        item = AudioQueueItem(
            request=TTSRequest(
                text=f"backpressure-{index}",
                guild_id=2,
                member_id=index,
            )
        )
        accepted.append(await queue.enqueue(item))

    status = await queue.get_queue_status(2)

    assert accepted[:3] == [item_id for item_id in accepted[:3] if item_id is not None]
    assert accepted[3] is None
    assert status.size == 3


def _write_report(report: dict[str, object]) -> None:
    report_path = os.getenv("QUEUE_LOAD_REPORT_PATH")
    if not report_path:
        return
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
