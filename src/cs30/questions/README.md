# Member 3 - validated SciQ demo questions

Implement `cs30.ports.QuestionProvider`:

    `get(question_id: str) -> SciQQuestion`

Drop the real loader next to `fixture.py`. The UI or evaluation harness asks for
a stable question id and passes the validated `SciQQuestion.question` into the
online pipeline.

## Week 1 acceptance

- Every item validates against `SciQQuestion` and has exactly four choices.
- Question ids are stable and unique.
- Unsupported or out-of-scope items are explicitly marked, not silently removed.
- The demo set is not reported as a formal evaluation set.
