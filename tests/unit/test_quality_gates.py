from pathlib import Path

from scripts.test import quality_gates


def test_load_quality_gate_config_reads_repository_thresholds():
    config = quality_gates.load_quality_gate_config("config/quality_gates.json")

    assert config.coverage.global_minimum_percent == 80.0
    assert [domain.name for domain in config.coverage.critical_domains] == [
        "queue",
        "runtime_observability",
    ]
    assert config.sli.max_error_rate == 0.05


def test_evaluate_coverage_gates_aggregates_domain_paths(tmp_path: Path):
    coverage_xml = tmp_path / "coverage.xml"
    coverage_xml.write_text(
        """<?xml version="1.0" ?>
<coverage line-rate="0.82">
  <packages>
    <package name="application">
      <classes>
        <class filename="tts_queue_orchestrator.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
            <line number="3" hits="1"/>
            <line number="4" hits="0"/>
          </lines>
        </class>
      </classes>
    </package>
    <package name="infrastructure">
      <classes>
        <class filename="audio_queue.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
            <line number="3" hits="1"/>
            <line number="4" hits="1"/>
          </lines>
        </class>
        <class filename="runtime_observability.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
          </lines>
        </class>
      </classes>
    </package>
    <package name="bot_runtime">
      <classes>
        <class filename="queue_worker.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
            <line number="3" hits="1"/>
            <line number="4" hits="0"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
""",
        encoding="utf-8",
    )

    config = quality_gates.QualityGateConfig(
        coverage=quality_gates.CoverageGateConfig(
            global_minimum_percent=80.0,
            critical_domains=(
                quality_gates.CoverageDomainGate(
                    name="queue",
                    minimum_percent=75.0,
                    paths=(
                        "src/application/tts_queue_orchestrator.py",
                        "src/infrastructure/audio_queue.py",
                        "src/bot_runtime/queue_worker.py",
                    ),
                ),
                quality_gates.CoverageDomainGate(
                    name="runtime_observability",
                    minimum_percent=90.0,
                    paths=("src/infrastructure/runtime_observability.py",),
                ),
            ),
        ),
        sli=quality_gates.SLIGateConfig(
            max_error_rate=0.05,
            max_enqueue_to_playback_p95_ms=5000.0,
            max_enqueue_to_playback_p99_ms=15000.0,
        ),
    )

    global_percent, domain_results = quality_gates.evaluate_coverage_gates(coverage_xml, config)

    assert global_percent == 82.0
    assert [(result.name, result.actual_percent) for result in domain_results] == [
        ("queue", 83.33),
        ("runtime_observability", 100.0),
    ]


def test_evaluate_coverage_gates_requires_all_configured_paths(tmp_path: Path):
    coverage_xml = tmp_path / "coverage.xml"
    coverage_xml.write_text(
        """<?xml version="1.0" ?>
<coverage line-rate="0.90">
  <packages>
    <package name="application">
      <classes>
        <class filename="tts_queue_orchestrator.py">
          <lines>
            <line number="1" hits="1"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
""",
        encoding="utf-8",
    )

    config = quality_gates.QualityGateConfig(
        coverage=quality_gates.CoverageGateConfig(
            global_minimum_percent=80.0,
            critical_domains=(
                quality_gates.CoverageDomainGate(
                    name="queue",
                    minimum_percent=80.0,
                    paths=(
                        "src/application/tts_queue_orchestrator.py",
                        "src/infrastructure/audio_queue.py",
                    ),
                ),
            ),
        ),
        sli=quality_gates.SLIGateConfig(
            max_error_rate=0.05,
            max_enqueue_to_playback_p95_ms=5000.0,
            max_enqueue_to_playback_p99_ms=15000.0,
        ),
    )

    try:
        quality_gates.evaluate_coverage_gates(coverage_xml, config)
    except ValueError as exc:
        assert "audio_queue.py" in str(exc)
    else:
        raise AssertionError("Expected missing configured coverage path to raise ValueError")


def test_evaluate_observability_payload_accepts_payload_within_thresholds():
    failures = quality_gates.evaluate_observability_payload(
        {
            "error_rate": 0.02,
            "enqueue_to_playback_sample_count": 12,
            "enqueue_to_playback_p95_ms": 1500.0,
            "enqueue_to_playback_p99_ms": 4000.0,
        },
        quality_gates.SLIGateConfig(
            max_error_rate=0.05,
            max_enqueue_to_playback_p95_ms=5000.0,
            max_enqueue_to_playback_p99_ms=15000.0,
        ),
    )

    assert failures == []


def test_evaluate_observability_payload_reports_sli_regressions():
    failures = quality_gates.evaluate_observability_payload(
        {
            "error_rate": 0.11,
            "enqueue_to_playback_sample_count": 4,
            "enqueue_to_playback_p95_ms": 6000.0,
            "enqueue_to_playback_p99_ms": 20000.0,
        },
        quality_gates.SLIGateConfig(
            max_error_rate=0.05,
            max_enqueue_to_playback_p95_ms=5000.0,
            max_enqueue_to_playback_p99_ms=15000.0,
        ),
    )

    assert failures == [
        "error_rate exceeded: 0.1100 > 0.0500",
        "enqueue_to_playback_p95_ms exceeded: 6000.00 > 5000.00",
        "enqueue_to_playback_p99_ms exceeded: 20000.00 > 15000.00",
    ]
