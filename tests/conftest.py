"""
conftest.py - Shared fixtures for the test suite
=================================================
Fixtures defined here are automatically available to all test files
inside the tests/ directory.

Key fixtures:
  - reset_rag_singleton: autouse, clears the lazy-loaded resources
    in rag._recursos between tests so they don't leak state.
  - mock_recursos: provides a fully mocked Recursos object so tests
    never touch the real Chroma DB, the real embedding model, or
    the real Anthropic API.
  - sample_markdown: a small synthetic markdown document used by the
    chunking tests, independent of the real metodologia.md.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


# ============================================================
# Autouse: reset the lazy singleton between tests
# ============================================================

@pytest.fixture(autouse=True)
def reset_rag_singleton():
    """Clear rag._recursos before and after every test."""
    import rag
    rag._recursos = None
    yield
    rag._recursos = None


# ============================================================
# Mocked resources (Chroma, embeddings, Anthropic)
# ============================================================

@pytest.fixture
def mock_recursos(monkeypatch):
    """
    Returns a fake Recursos object and patches rag.cargar_recursos
    to return it. The mock is configured to behave like the real
    components without making any network or disk calls.
    """
    import rag

    # --- Fake Chroma collection ---
    fake_collection = MagicMock()
    fake_collection.query.return_value = {
        "documents": [[
            "## 9. Risk management\n- Max risk per trade: 300 USD",
            "## 3. Top priority\nCapital protection is the absolute priority.",
        ]],
        "metadatas": [[
            {"seccion": "9. Risk management", "subseccion": "", "chunk_index": 0, "fuente": "test.md"},
            {"seccion": "3. Top priority", "subseccion": "", "chunk_index": 0, "fuente": "test.md"},
        ]],
        "distances": [[0.15, 0.40]],
    }

    # --- Fake embedding model ---
    fake_embedding_array = MagicMock()
    fake_embedding_array.tolist.return_value = [0.1] * 768

    fake_model = MagicMock()
    fake_model.encode.return_value = fake_embedding_array

    # --- Fake Anthropic client ---
    fake_response = MagicMock()
    text_block = MagicMock()
    text_block.text = (
        "The maximum risk per trade is 300 USD.\n\n"
        "Fuentes consultadas:\n- Seccion 9. Risk management"
    )
    fake_response.content = [text_block]
    fake_response.usage = MagicMock(input_tokens=150, output_tokens=42)

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    # --- Assemble the fake Recursos object ---
    fake_recursos = rag.Recursos(
        coleccion=fake_collection,
        modelo_embeddings=fake_model,
        cliente_claude=fake_client,
    )

    # Patch the loader so any call returns our fake
    monkeypatch.setattr("rag.cargar_recursos", lambda: fake_recursos)

    return fake_recursos


# ============================================================
# Synthetic markdown document for chunking tests
# ============================================================

@pytest.fixture
def sample_markdown() -> str:
    """A small but structurally complete markdown document."""
    return """# Test Methodology

## 1. Vision
This is the vision section. It explains the overall approach.

## 2. Edge
The edge consists of identifying patterns with three confirmations.

### Detection
Detection uses indicator A combined with indicator B.

### Filters
Three quality filters are applied to validate signals.

## 3. Risk
Maximum risk per trade is fixed at 300 units.
"""


@pytest.fixture
def long_section_markdown() -> str:
    """A markdown document with one section large enough to force sub-splitting."""
    # Generate a single long section that exceeds the default chunk size
    long_text = " ".join(["Lorem ipsum dolor sit amet consectetur adipiscing elit."] * 80)
    return f"""# Long Doc

## 1. Long section
{long_text}

## 2. Short section
Just a short closing section.
"""
