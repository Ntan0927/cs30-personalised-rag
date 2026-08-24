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
from cs30.errors import CS30Error
from cs30.fixtures import load_fixture


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
    with pytest.raises(CS30Error, match="unknown citation"):
        validate_citations(answer, retrieval)


def test_chunk_text_keeps_boundary_whitespace() -> None:
    """Chunk text is bound to a span, so it must never be normalised."""

    raw = "  boundary whitespace matters  "
    chunk = Chunk(
        chunk_id="chunk_ws",
        document_id="doc",
        chapter_id="ch01",
        text=raw,
        source="fixture://openstax/physics#ch01",
        char_start=10,
        char_end=10 + len(raw),
        token_count=4,
    )
    assert chunk.text == raw


def test_chunk_rejects_span_length_mismatch() -> None:
    with pytest.raises(ValidationError, match="does not match span"):
        Chunk(
            chunk_id="chunk_bad",
            document_id="doc",
            chapter_id="ch01",
            text="four",
            source="fixture://openstax/physics#ch01",
            char_start=0,
            char_end=99,
            token_count=1,
        )


def test_chunk_identifier_fields_are_normalised() -> None:
    chunk = Chunk(
        chunk_id="  chunk_ws_id  ",
        document_id="doc",
        chapter_id="ch01",
        text="exact",
        source="fixture://openstax/physics#ch01",
        char_start=0,
        char_end=5,
        token_count=1,
    )
    assert chunk.chunk_id == "chunk_ws_id"


def test_retrieval_result_allows_no_hits() -> None:
    """Finding nothing is a valid outcome, not a failure."""

    result = RetrievalResult(query="unrelated question")
    assert result.hits == []


def test_generated_answer_allows_abstention() -> None:
    answer = GeneratedAnswer(
        explanation="The retrieved evidence does not support an answer.",
        abstained=True,
    )
    assert answer.citations == []
    assert answer.final_choice is None


def test_abstained_answer_must_not_select_a_choice() -> None:
    with pytest.raises(ValidationError, match="must not select a final_choice"):
        GeneratedAnswer(
            final_choice="B",
            explanation="Cannot answer, yet picked one anyway.",
            abstained=True,
        )


def test_abstained_answer_must_not_cite_evidence() -> None:
    with pytest.raises(ValidationError, match="must not cite evidence"):
        GeneratedAnswer(
            explanation="Cannot answer, yet cited something.",
            citations=["chunk_ch01_0001"],
            abstained=True,
        )


def test_non_abstained_answer_requires_a_citation() -> None:
    with pytest.raises(ValidationError, match="must cite at least one chunk"):
        GeneratedAnswer(explanation="Ungrounded claim with no evidence.")


def test_abstained_answer_passes_citation_integrity() -> None:
    retrieval = RetrievalResult(query="unrelated question")
    answer = GeneratedAnswer(
        explanation="The retrieved evidence does not support an answer.",
        abstained=True,
    )
    validate_citations(answer, retrieval)


def test_packaged_answer_fixture_still_validates() -> None:
    """Reference payload for member 7; kept valid so it cannot rot."""

    answer = GeneratedAnswer.model_validate(load_fixture("generated_answer.json"))
    assert answer.abstained is False
    assert answer.citations
