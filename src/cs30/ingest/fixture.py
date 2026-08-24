"""Fixture parser used until real OpenStax parsing lands."""

from pathlib import Path

from cs30.contracts import OpenStaxDocument
from cs30.fixtures import load_fixture


class FixtureDocumentParser:
    """Return one packaged document, ignoring the requested source."""

    def parse(self, source: Path) -> OpenStaxDocument:
        return OpenStaxDocument.model_validate(load_fixture("openstax_document.json"))
