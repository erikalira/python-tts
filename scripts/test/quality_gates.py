"""Quality gate helpers for coverage and SLI enforcement."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


@dataclass(frozen=True)
class CoverageDomainGate:
    name: str
    minimum_percent: float
    paths: tuple[str, ...]


@dataclass(frozen=True)
class CoverageGateResult:
    name: str
    actual_percent: float
    minimum_percent: float
    matched_paths: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.actual_percent >= self.minimum_percent


@dataclass(frozen=True)
class CoverageGateConfig:
    global_minimum_percent: float
    critical_domains: tuple[CoverageDomainGate, ...]


@dataclass(frozen=True)
class SLIGateConfig:
    max_error_rate: float
    max_enqueue_to_playback_p95_ms: float
    max_enqueue_to_playback_p99_ms: float


@dataclass(frozen=True)
class QualityGateConfig:
    coverage: CoverageGateConfig
    sli: SLIGateConfig


def load_quality_gate_config(config_path: str | Path) -> QualityGateConfig:
    raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
    coverage = raw["coverage"]
    sli = raw["sli"]
    return QualityGateConfig(
        coverage=CoverageGateConfig(
            global_minimum_percent=float(coverage["global_minimum_percent"]),
            critical_domains=tuple(
                CoverageDomainGate(
                    name=str(domain["name"]),
                    minimum_percent=float(domain["minimum_percent"]),
                    paths=tuple(str(path) for path in domain["paths"]),
                )
                for domain in coverage["critical_domains"]
            ),
        ),
        sli=SLIGateConfig(
            max_error_rate=float(sli["max_error_rate"]),
            max_enqueue_to_playback_p95_ms=float(sli["max_enqueue_to_playback_p95_ms"]),
            max_enqueue_to_playback_p99_ms=float(sli["max_enqueue_to_playback_p99_ms"]),
        ),
    )


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./").lower()


def _coverage_line_totals(class_element: ElementTree.Element) -> tuple[int, int]:
    total = 0
    covered = 0
    for line in class_element.findall("./lines/line"):
        total += 1
        if int(line.attrib["hits"]) > 0:
            covered += 1
    return covered, total


def _class_matches_path(filename: str, configured_path: str) -> bool:
    normalized_filename = _normalize_path(filename)
    normalized_configured_path = _normalize_path(configured_path)
    return (
        normalized_filename == normalized_configured_path
        or normalized_configured_path.endswith("/" + normalized_filename)
        or normalized_filename.endswith("/" + normalized_configured_path)
    )


def _evaluate_domain_gate(
    coverage_root: ElementTree.Element,
    domain: CoverageDomainGate,
) -> CoverageGateResult:
    covered_lines = 0
    total_lines = 0
    matched_paths: list[str] = []
    remaining_paths = {_normalize_path(path): path for path in domain.paths}

    for class_element in coverage_root.findall(".//class"):
        filename = class_element.attrib.get("filename", "")
        for normalized_path, original_path in list(remaining_paths.items()):
            if not _class_matches_path(filename, normalized_path):
                continue
            covered, total = _coverage_line_totals(class_element)
            covered_lines += covered
            total_lines += total
            matched_paths.append(original_path)
            del remaining_paths[normalized_path]
            break

    if remaining_paths:
        missing = ", ".join(sorted(remaining_paths.values()))
        raise ValueError(f"Coverage report does not include configured paths for domain '{domain.name}': {missing}")

    if total_lines <= 0:
        raise ValueError(f"Coverage report has no executable lines for domain '{domain.name}'")

    actual_percent = round((covered_lines / total_lines) * 100, 2)
    return CoverageGateResult(
        name=domain.name,
        actual_percent=actual_percent,
        minimum_percent=domain.minimum_percent,
        matched_paths=tuple(sorted(matched_paths)),
    )


def evaluate_coverage_gates(
    coverage_xml_path: str | Path,
    config: QualityGateConfig,
) -> tuple[float, list[CoverageGateResult]]:
    coverage_root = ElementTree.fromstring(Path(coverage_xml_path).read_text(encoding="utf-8"))
    global_percent = round(float(coverage_root.attrib["line-rate"]) * 100, 2)
    domain_results = [
        _evaluate_domain_gate(coverage_root, domain)
        for domain in config.coverage.critical_domains
    ]
    return global_percent, domain_results


def evaluate_observability_payload(
    payload: dict[str, Any],
    sli: SLIGateConfig,
) -> list[str]:
    failures: list[str] = []

    error_rate = float(payload.get("error_rate", 0.0))
    if error_rate > sli.max_error_rate:
        failures.append(
            "error_rate exceeded: "
            f"{error_rate:.4f} > {sli.max_error_rate:.4f}"
        )

    sample_count = int(payload.get("enqueue_to_playback_sample_count", 0))
    if sample_count <= 0:
        failures.append("enqueue_to_playback_sample_count must be greater than zero")
        return failures

    p95 = payload.get("enqueue_to_playback_p95_ms")
    if p95 is None:
        failures.append("enqueue_to_playback_p95_ms is missing")
    elif float(p95) > sli.max_enqueue_to_playback_p95_ms:
        failures.append(
            "enqueue_to_playback_p95_ms exceeded: "
            f"{float(p95):.2f} > {sli.max_enqueue_to_playback_p95_ms:.2f}"
        )

    p99 = payload.get("enqueue_to_playback_p99_ms")
    if p99 is None:
        failures.append("enqueue_to_playback_p99_ms is missing")
    elif float(p99) > sli.max_enqueue_to_playback_p99_ms:
        failures.append(
            "enqueue_to_playback_p99_ms exceeded: "
            f"{float(p99):.2f} > {sli.max_enqueue_to_playback_p99_ms:.2f}"
        )

    return failures


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enforce repository quality gates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    coverage_parser = subparsers.add_parser("coverage", help="Validate coverage gates.")
    coverage_parser.add_argument(
        "--config",
        default="config/quality_gates.json",
        help="Path to the quality gate configuration JSON.",
    )
    coverage_parser.add_argument(
        "--coverage-xml",
        default="coverage.xml",
        help="Path to coverage.xml generated by pytest-cov.",
    )

    observability_parser = subparsers.add_parser("observability", help="Validate an observability payload.")
    observability_parser.add_argument(
        "--config",
        default="config/quality_gates.json",
        help="Path to the quality gate configuration JSON.",
    )
    observability_parser.add_argument(
        "--payload",
        required=True,
        help="Path to a JSON file that contains an observability payload.",
    )
    return parser


def _run_coverage_gate(config: QualityGateConfig, coverage_xml_path: str | Path) -> int:
    global_percent, domain_results = evaluate_coverage_gates(coverage_xml_path, config)
    failures: list[str] = []
    if global_percent < config.coverage.global_minimum_percent:
        failures.append(
            "global coverage below minimum: "
            f"{global_percent:.2f}% < {config.coverage.global_minimum_percent:.2f}%"
        )

    for result in domain_results:
        if result.passed:
            continue
        failures.append(
            f"{result.name} coverage below minimum: "
            f"{result.actual_percent:.2f}% < {result.minimum_percent:.2f}%"
        )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "PASS: global coverage "
        f"{global_percent:.2f}% and {len(domain_results)} critical domain gate(s) satisfied."
    )
    return 0


def _run_observability_gate(config: QualityGateConfig, payload_path: str | Path) -> int:
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    failures = evaluate_observability_payload(payload, config.sli)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: observability payload satisfied configured SLI gates.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = load_quality_gate_config(args.config)

    if args.command == "coverage":
        return _run_coverage_gate(config, args.coverage_xml)
    if args.command == "observability":
        return _run_observability_gate(config, args.payload)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
