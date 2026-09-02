"""Packaged SciQ question used while the real demo set is prepared."""

from cs30.contracts import SciQQuestion
from cs30.fixtures import load_fixture


class FixtureQuestionProvider:
    """Return the packaged SciQ question by its stable identifier."""

    def get(self, question_id: str) -> SciQQuestion:
        question = SciQQuestion.model_validate(load_fixture("sciq_question.json"))
        if question.question_id != question_id.strip():
            raise KeyError(f"unknown fixture question_id: {question_id}")
        return question
