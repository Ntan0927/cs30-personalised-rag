import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from cs30.citation import validate_citations
from cs30.contracts import (
    Chunk,
    GeneratedAnswer,
    OpenStaxDocument,
    RetrievalResult,
    SciQQuestion,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_openstax_document_fixture_is_valid() -> None:
    document = OpenStaxDocument.model_validate(load_fixture("openstax_document.json"))
    assert document.chapters[0].char_end == len(document.text)

    chunks = TypeAdapter(list[Chunk]).validate_python(load_fixture("chunks.json"))
    for chunk in chunks:
        assert document.text[chunk.char_start : chunk.char_end] == chunk.text


def test_sciq_question_requires_exactly_four_choices() -> None:
    payload = load_fixture("sciq_question.json")
    SciQQuestion.model_validate(payload)
    payload["choices"].pop("D")
    with pytest.raises(ValidationError):
        SciQQuestion.model_validate(payload)


def test_generated_answer_rejects_unknown_citation() -> None:
    retrieval = RetrievalResult.model_validate(load_fixture("retrieval_result.json"))
    answer = GeneratedAnswer(
        final_choice="B",
        explanation="Fixture explanation",
        citations=["chunk_missing"],
    )
    with pytest.raises(ValueError, match="unknown citation"):
        validate_citations(answer, retrieval)
