"""Minimal profile provider covering the three Week 1 levels."""

from cs30.contracts import StudentLevel, StudentProfile


class FixtureProfileProvider:
    """Build a profile straight from the requested level."""

    def get(self, level: StudentLevel) -> StudentProfile:
        return StudentProfile(
            profile_id=f"fixture-{level.value}",
            level=level,
            confidence=1.0,
        )
