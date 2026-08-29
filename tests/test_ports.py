"""Fixture modules expose Protocol methods and are exercised by behaviour tests."""

from pathlib import Path

from cs30.chunking import FixtureChunker
from cs30.config import load_config
from cs30.generation import FixtureAnswerGenerator, MockJsonLLMClient, PersonalisedAnswerGenerator
from cs30.indexing import FixtureIndexBuilder
from cs30.ingest import FixtureDocumentParser
from cs30.pipeline import build_real_deps
from cs30.ports import (
    AnswerGenerator,
    Chunker,
    DocumentParser,
    IndexBuilder,
    ProfileProvider,
    QuestionProvider,
    Retriever,
)
from cs30.profile import FixtureProfileProvider, Week1ProfileProvider
from cs30.questions import DemoQuestionProvider
from cs30.retrieval import FixtureRetriever


def test_fixture_modules_satisfy_their_protocols() -> None:
    assert isinstance(FixtureDocumentParser(), DocumentParser)
    assert isinstance(DemoQuestionProvider(), QuestionProvider)
    assert isinstance(FixtureChunker(), Chunker)
    assert isinstance(FixtureIndexBuilder(), IndexBuilder)
    assert isinstance(FixtureRetriever(), Retriever)
    assert isinstance(FixtureProfileProvider(), ProfileProvider)
    assert isinstance(FixtureAnswerGenerator(), AnswerGenerator)


def test_member7_real_modules_satisfy_their_protocols() -> None:
    assert isinstance(Week1ProfileProvider(), ProfileProvider)
    assert isinstance(PersonalisedAnswerGenerator(MockJsonLLMClient()), AnswerGenerator)


def test_local_rag_dependencies_keep_frozen_team_protocols() -> None:
    deps = build_real_deps(load_config("development"))

    assert isinstance(deps.profile_provider, ProfileProvider)
    assert isinstance(deps.retriever, Retriever)
    assert isinstance(deps.generator, AnswerGenerator)


def test_fixture_parser_and_chunker_agree_on_spans() -> None:
    document = FixtureDocumentParser().parse(Path("unused-openstax-source"))
    chunks = FixtureChunker().chunk(document)

    assert chunks
    for chunk in chunks:
        assert document.text[chunk.char_start : chunk.char_end] == chunk.text


def test_demo_question_provider_returns_the_requested_sciq_contract() -> None:
    provider = DemoQuestionProvider()

    question = provider.get("sciq-train-00226")

    assert isinstance(provider, QuestionProvider)
    assert question.question_id == "sciq-train-00226"
    assert set(question.choices) == {"A", "B", "C", "D"}
