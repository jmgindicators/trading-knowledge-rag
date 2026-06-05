"""
test_rag.py - Tests for the retrieval + generation pipeline
============================================================
Validates the building blocks of rag.py: data classes, prompt
construction, cost calculation, and input validation.
"""

from __future__ import annotations

import pytest

from rag import (
    ChunkRecuperado,
    construir_mensaje_usuario,
    coste_aproximado,
    consultar_conversacional,
)


# ============================================================
# Data class
# ============================================================

class TestChunkRecuperado:

    def test_fields_populated_correctly(self):
        """ChunkRecuperado exposes texto, seccion, similitud."""
        chunk = ChunkRecuperado(
            texto="Sample text",
            seccion="9. Risk management",
            similitud=0.85,
        )
        assert chunk.texto == "Sample text"
        assert chunk.seccion == "9. Risk management"
        assert chunk.similitud == 0.85


# ============================================================
# Prompt construction
# ============================================================

class TestConstruirMensajeUsuario:

    def test_includes_fragment_markers(self):
        """Each chunk appears as '[Fragmento N - Seccion: X]'."""
        chunks = [
            ChunkRecuperado(texto="Content A", seccion="1. Vision", similitud=0.9),
            ChunkRecuperado(texto="Content B", seccion="2. Edge", similitud=0.8),
        ]
        msg = construir_mensaje_usuario("What is the vision?", chunks)

        assert "Fragmento 1" in msg
        assert "Fragmento 2" in msg
        assert "1. Vision" in msg
        assert "2. Edge" in msg
        assert "Content A" in msg
        assert "Content B" in msg

    def test_user_question_appears_at_end(self):
        """The user's question is appended at the bottom of the message."""
        chunks = [ChunkRecuperado(texto="X", seccion="S1", similitud=0.5)]
        question = "What is the maximum risk?"
        msg = construir_mensaje_usuario(question, chunks)

        assert msg.rstrip().endswith(question)

    def test_handles_empty_chunks(self):
        """If no chunks are provided the message is still valid."""
        msg = construir_mensaje_usuario("Question?", [])

        # The header section markers must still be present
        assert "Contexto recuperado" in msg
        assert "Pregunta del usuario" in msg
        assert "Question?" in msg


# ============================================================
# Cost calculation
# ============================================================

class TestCosteAproximado:

    def test_one_million_tokens_each_way(self):
        """1M input + 1M output = $1 + $5 = $6 per Haiku 4.5 pricing."""
        cost = coste_aproximado(1_000_000, 1_000_000)
        assert cost == pytest.approx(6.0)

    def test_zero_tokens_zero_cost(self):
        """No tokens means no cost."""
        assert coste_aproximado(0, 0) == 0.0

    def test_realistic_query_cost(self):
        """A realistic query (1500 in, 300 out) costs roughly $0.003."""
        cost = coste_aproximado(1500, 300)
        # 1500 * 1e-6 * 1 + 300 * 1e-6 * 5 = 0.0015 + 0.0015 = 0.003
        assert cost == pytest.approx(0.003, abs=1e-6)


# ============================================================
# Input validation
# ============================================================

class TestConsultarConversacionalValidation:

    def test_rejects_empty_history(self):
        """Empty message list raises ValueError."""
        with pytest.raises(ValueError):
            consultar_conversacional([])

    def test_rejects_history_ending_with_assistant(self, mock_recursos):
        """If the last message is from the assistant, raise ValueError."""
        history = [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
        ]
        with pytest.raises(ValueError):
            consultar_conversacional(history)
