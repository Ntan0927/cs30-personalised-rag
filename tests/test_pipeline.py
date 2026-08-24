from cs30.contracts import StudentLevel
from cs30.pipeline import run_mock_pipeline


def test_mock_pipeline_runs_end_to_end() -> None:
    result = run_mock_pipeline("What is acceleration?", StudentLevel.BEGINNER)

    assert result["mode"] == "fixture"
    assert result["profile"]["level"] == "beginner"
    assert result["retrieval"]["hits"][0]["chunk_id"] == "chunk_ch01_0001"
    assert result["answer"]["citations"] == ["chunk_ch01_0001"]
    assert result["citation_integrity"] == "passed"

