"""Fixture modules expose Protocol methods and are exercised by behaviour tests."""

from pathlib import Path

from cs30.chunking import FixtureChunker
from cs30.generation import FixtureAnswerGenerator
from cs30.indexing import FixtureIndexBuilder
from cs30.ingest import FixtureDocumentParser
from cs30.ports import (
    AnswerGenerator,
    Chunker,
    DocumentParser,
    IndexBuilder,
    ProfileProvider,
    QuestionProvider,
    Retriever,
)
from cs30.profile import FixtureProfileProvider
from cs30.questions import FixtureQuestionProvider
from cs30.retrieval import FixtureRetriever


def test_fixture_modules_satisfy_their_protocols() -> None:
    assert isinstance(FixtureDocumentParser(), DocumentParser)
    assert isinstance(FixtureQuestionProvider(), QuestionProvider)
    assert isinstance(FixtureChunker(), Chunker)
    assert isinstance(FixtureIndexBuilder(), IndexBuilder)
    assert isinstance(FixtureRetriever(), Retriever)
    assert isinstance(FixtureProfileProvider(), ProfileProvider)
    assert isinstance(FixtureAnswerGenerator(), AnswerGenerator)


def test_fixture_parser_and_chunker_agree_on_spans() -> None:
    document = FixtureDocumentParser().parse(Path("unused-openstax-source"))
    chunks = FixtureChunker().chunk(document)

    assert chunks
    for chunk in chunks:
        assert document.text[chunk.char_start : chunk.char_end] == chunk.text


def test_fixture_question_provider_returns_the_requested_sciq_contract() -> None:
    provider = FixtureQuestionProvider()

    question = provider.get("fixture_q001")

    assert isinstance(provider, QuestionProvider)
    assert question.question_id == "fixture_q001"
    assert set(question.choices) == {"A", "B", "C", "D"}
