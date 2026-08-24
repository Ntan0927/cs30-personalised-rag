"""Version 1 contracts shared by all Week 1 modules.

Character spans use Python slicing semantics: ``char_start`` is inclusive and
``char_end`` is exclusive. Unknown fields are rejected so interface drift is
detected during integration rather than silently ignored.
"""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ChoiceLabel = Literal["A", "B", "C", "D"]
NonEmptyText = Annotated[str, Field(min_length=1)]


class ContractModel(BaseModel):
    """Strict base model for frozen cross-module contracts."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class StudentLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class OpenStaxChapter(ContractModel):
    chapter_id: NonEmptyText
    title: NonEmptyText
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_span(self) -> "OpenStaxChapter":
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        if self.page_start and self.page_end and self.page_end < self.page_start:
            raise ValueError("page_end must not precede page_start")
        return self


class OpenStaxDocument(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    document_id: NonEmptyText
    title: NonEmptyText
    version: NonEmptyText
    source: NonEmptyText
    document_hash: NonEmptyText
    parser_version: NonEmptyText
    text: NonEmptyText
    chapters: list[OpenStaxChapter] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_chapter_spans(self) -> "OpenStaxDocument":
        seen: set[str] = set()
        previous_end = 0
        for chapter in self.chapters:
            if chapter.chapter_id in seen:
                raise ValueError(f"duplicate chapter_id: {chapter.chapter_id}")
            if chapter.char_end > len(self.text):
                raise ValueError(f"chapter span exceeds document text: {chapter.chapter_id}")
            if chapter.char_start < previous_end:
                raise ValueError("chapter spans must be ordered and non-overlapping")
            seen.add(chapter.chapter_id)
            previous_end = chapter.char_end
        return self


class Chunk(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    chunk_id: NonEmptyText
    document_id: NonEmptyText
    chapter_id: NonEmptyText
    text: NonEmptyText
    source: NonEmptyText
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    token_count: int = Field(gt=0)
    metadata: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_span(self) -> "Chunk":
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        return self


class SciQQuestion(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    question_id: NonEmptyText
    question: NonEmptyText
    choices: dict[ChoiceLabel, NonEmptyText]
    correct_choice: ChoiceLabel
    support: NonEmptyText
    in_scope: bool = True
    source: NonEmptyText = "SciQ"

    @model_validator(mode="after")
    def validate_choices(self) -> "SciQQuestion":
        if set(self.choices) != {"A", "B", "C", "D"}:
            raise ValueError("choices must contain exactly A, B, C, and D")
        return self


class RetrievalHit(ContractModel):
    chunk_id: NonEmptyText
    text: NonEmptyText
    chapter_id: NonEmptyText
    source: NonEmptyText
    score: float
    rank: int = Field(ge=1)


class RetrievalResult(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    query: NonEmptyText
    hits: list[RetrievalHit] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_ranks(self) -> "RetrievalResult":
        ranks = [hit.rank for hit in self.hits]
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError("retrieval ranks must be consecutive and start at 1")
        if len({hit.chunk_id for hit in self.hits}) != len(self.hits):
            raise ValueError("retrieval hits must have unique chunk_id values")
        return self


class StudentProfile(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    profile_id: NonEmptyText
    level: StudentLevel
    topic_levels: dict[str, StudentLevel] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class GeneratedAnswer(ContractModel):
    schema_version: Literal["1.0"] = "1.0"
    final_choice: ChoiceLabel | None = None
    explanation: NonEmptyText
    citations: list[NonEmptyText] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_citations(self) -> "GeneratedAnswer":
        if len(set(self.citations)) != len(self.citations):
            raise ValueError("citations must be unique")
        return self

