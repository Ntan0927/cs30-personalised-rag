"""Unified Week 1 pipeline entry point.

The initial implementation deliberately uses fixtures. Real parser, retriever,
and generator adapters can replace each fixture boundary without changing the
public contracts or CLI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from cs30.citation import validate_citations
from cs30.contracts import (
    Chunk,
    GeneratedAnswer,
    RetrievalResult,
    StudentLevel,
    StudentProfile,
)

DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_mock_pipeline(
    question: str,
    level: StudentLevel,
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
) -> dict[str, Any]:
    """Run the contract-complete fixture pipeline used before GPU access."""

    if not question.strip():
        raise ValueError("question must not be empty")

    chunks = TypeAdapter(list[Chunk]).validate_python(_read_json(fixture_dir / "chunks.json"))
    retrieval_payload = _read_json(fixture_dir / "retrieval_result.json")
    retrieval_payload["query"] = question.strip()
    retrieval = RetrievalResult.model_validate(retrieval_payload)
    answer = GeneratedAnswer.model_validate(_read_json(fixture_dir / "generated_answer.json"))
    profile = StudentProfile(
        profile_id=f"fixture-{level.value}",
        level=level,
        confidence=1.0,
    )

    available_chunks = {chunk.chunk_id for chunk in chunks}
    missing_hits = sorted({hit.chunk_id for hit in retrieval.hits} - available_chunks)
    if missing_hits:
        raise ValueError(f"retrieval references missing fixture chunks: {', '.join(missing_hits)}")

    validate_citations(answer, retrieval)

    return {
        "mode": "fixture",
        "question": question.strip(),
        "profile": profile.model_dump(mode="json"),
        "retrieval": retrieval.model_dump(mode="json"),
        "answer": answer.model_dump(mode="json"),
        "citation_integrity": "passed",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the CS-30 Week 1 thin-slice pipeline")
    parser.add_argument("--question", required=True, help="Question to send through the pipeline")
    parser.add_argument(
        "--level",
        choices=[level.value for level in StudentLevel],
        default=StudentLevel.INTERMEDIATE.value,
        help="Student explanation level",
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing integration fixtures",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_mock_pipeline(
        question=args.question,
        level=StudentLevel(args.level),
        fixture_dir=args.fixture_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

