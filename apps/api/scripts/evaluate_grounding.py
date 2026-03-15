"""Grounding policy evaluation utility.

Evaluates factual-claim citation enforcement using fixture cases.
Designed for deterministic CI gating without external API calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

from app.infrastructure.adk.tools import ADKToolbox
from scripts.common import error, info, success


def load_cases(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "cases" in payload:
        return payload["cases"]
    if isinstance(payload, list):
        return payload
    raise ValueError("Grounding fixture must be a list or object with 'cases'")


def evaluate_cases(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    toolbox = ADKToolbox(
        rag_pipeline=SimpleNamespace(retrieve_context=None),
        emergency_detector=SimpleNamespace(),
        medical_detector=SimpleNamespace(),
    )
    evaluated: List[Dict[str, Any]] = []
    factual_cases = 0
    cited_factual_cases = 0
    unsupported_factual_cases = 0

    for case in cases:
        answer = case.get("answer", "")
        citations = case.get("citations", [])
        safety_flags = case.get("safety_flags", {"is_emergency": False})

        policy = toolbox.response_policy_tool(
            answer=answer,
            citations=citations,
            safety_flags=safety_flags,
        )
        factual = toolbox._appears_factual_claim(answer)  # deterministic heuristic path
        has_citations = bool(citations)
        policy_enforced = bool(policy.get("policy_enforced"))

        if factual:
            factual_cases += 1
            if has_citations:
                cited_factual_cases += 1
            if policy_enforced:
                unsupported_factual_cases += 1

        evaluated.append(
            {
                "id": case.get("id"),
                "factual": factual,
                "has_citations": has_citations,
                "policy_reason": policy.get("reason"),
                "policy_enforced": policy_enforced,
            }
        )

    citation_rate = (
        (cited_factual_cases / factual_cases) if factual_cases else 1.0
    )
    unsupported_claim_rate = (
        (unsupported_factual_cases / factual_cases) if factual_cases else 0.0
    )

    return {
        "total_cases": len(cases),
        "factual_cases": factual_cases,
        "citation_rate": citation_rate,
        "unsupported_claim_rate": unsupported_claim_rate,
        "cases": evaluated,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate grounding policy heuristics")
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("tests/fixtures/grounding_eval_cases.json"),
        help="Fixture file with grounding cases",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("grounding-eval-results.json"),
        help="Output file for evaluation metrics",
    )
    parser.add_argument(
        "--min-citation-rate",
        type=float,
        default=None,
        help="Fail if factual-case citation rate is below this threshold (0-1)",
    )
    parser.add_argument(
        "--max-unsupported-claim-rate",
        type=float,
        default=None,
        help="Fail if unsupported factual-claim rate exceeds this threshold (0-1)",
    )
    args = parser.parse_args()

    cases = load_cases(args.cases)
    result = evaluate_cases(cases)

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    info(
        "Grounding metrics: citation_rate=%.3f unsupported_claim_rate=%.3f factual_cases=%s"
        % (
            result["citation_rate"],
            result["unsupported_claim_rate"],
            result["factual_cases"],
        )
    )
    success(f"Results written to: {args.output}")

    failures: List[str] = []
    if (
        args.min_citation_rate is not None
        and result["citation_rate"] < args.min_citation_rate
    ):
        failures.append(
            "citation_rate %.4f below threshold %.4f"
            % (result["citation_rate"], args.min_citation_rate)
        )
    if (
        args.max_unsupported_claim_rate is not None
        and result["unsupported_claim_rate"] > args.max_unsupported_claim_rate
    ):
        failures.append(
            "unsupported_claim_rate %.4f above threshold %.4f"
            % (result["unsupported_claim_rate"], args.max_unsupported_claim_rate)
        )

    if failures:
        for failure in failures:
            error(f"Quality gate failed: {failure}")
        sys.exit(1)


if __name__ == "__main__":
    main()
