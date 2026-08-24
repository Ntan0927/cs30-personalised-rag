"""Typed errors so a failing module reports a cause instead of a stack trace.

Week 1 requires that a missing index, an empty question, or a generation
failure produce a clear error rather than terminating the whole system.
"""


class CS30Error(Exception):
    """Base class for every expected CS-30 failure."""


class ConfigError(CS30Error):
    """Configuration is missing, unreadable, or invalid."""


class EmptyQueryError(CS30Error):
    """The question was empty or whitespace only."""


class IndexUnavailableError(CS30Error):
    """The index could not be built, found, or loaded."""


class RetrievalError(CS30Error):
    """Retrieval failed. Finding no evidence is NOT this error: an empty
    ``RetrievalResult.hits`` is a valid result."""


class GenerationError(CS30Error):
    """The generator failed, timed out, or returned unparseable output."""


class CitationIntegrityError(CS30Error):
    """The generated answer cites evidence that retrieval did not supply."""
