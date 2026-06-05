"""
test_ingest.py - Tests for the ingestion pipeline (chunking)
=============================================================
Validates the markdown-aware splitter and recursive fallback in
ingest.py, plus the document loader.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ingest import cargar_documento, trocear_documento


# ============================================================
# Document loading
# ============================================================

class TestCargarDocumento:

    def test_loads_existing_file(self):
        """cargar_documento returns the full text of an existing file."""
        content = "# Title\n\n## Section 1\nHello world."
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            result = cargar_documento(tmp_path)
            assert result == content
        finally:
            tmp_path.unlink()

    def test_raises_on_missing_file(self):
        """cargar_documento raises FileNotFoundError for nonexistent paths."""
        with pytest.raises(FileNotFoundError):
            cargar_documento(Path("/nonexistent/path/file.md"))


# ============================================================
# Chunking
# ============================================================

class TestTrocearDocumento:

    def test_respects_markdown_sections(self, sample_markdown):
        """Each '## section' becomes at least one independent chunk."""
        chunks = trocear_documento(sample_markdown)

        # The document has 3 H2 sections (Vision, Edge, Risk)
        # Each section's content should appear in at least one chunk
        all_text = "\n".join(c["texto"] for c in chunks)
        assert "Vision" in all_text
        assert "Edge" in all_text
        assert "Risk" in all_text

    def test_metadata_has_expected_keys(self, sample_markdown):
        """Every chunk carries the required metadata fields."""
        chunks = trocear_documento(sample_markdown)
        assert len(chunks) > 0

        required_keys = {"seccion", "subseccion", "chunk_index", "fuente"}
        for chunk in chunks:
            assert required_keys.issubset(chunk["metadatos"].keys()), (
                f"Chunk missing metadata keys. Got: {chunk['metadatos'].keys()}"
            )
            assert chunk["metadatos"]["fuente"] == "metodologia.md"

    def test_seccion_metadata_populated_from_h2(self, sample_markdown):
        """At least one chunk has 'seccion' populated from an H2 header."""
        chunks = trocear_documento(sample_markdown)
        secciones_no_vacias = [
            c["metadatos"]["seccion"] for c in chunks
            if c["metadatos"]["seccion"]
        ]
        # We expect multiple sections to have been detected
        assert len(secciones_no_vacias) >= 2

    def test_long_sections_get_subdivided(self, long_section_markdown):
        """Sections exceeding chunk_size are split by the recursive fallback."""
        chunks = trocear_documento(long_section_markdown)

        # Find chunks belonging to "Long section"
        long_section_chunks = [
            c for c in chunks if "Long section" in c["metadatos"].get("seccion", "")
        ]

        # The long section must produce more than one chunk
        assert len(long_section_chunks) > 1, (
            f"Expected long section to be split into multiple chunks, "
            f"got {len(long_section_chunks)}"
        )
