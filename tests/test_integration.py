"""
test_integration.py - End-to-end smoke tests with mocked dependencies
======================================================================
Verifies that the full pipeline (embed -> retrieve -> prompt -> Claude)
wires together correctly. All external dependencies are mocked, so
these tests are fast, deterministic, and free.
"""

from __future__ import annotations

from rag import consultar, consultar_conversacional


class TestFullPipeline:

    def test_simple_query_returns_complete_response(self, mock_recursos):
        """A single-question call returns a structured Respuesta with all fields."""
        result = consultar("Cual es el riesgo maximo?")

        # Text from the mocked Claude response
        assert "300 USD" in result.texto

        # Chunks were retrieved from the mocked collection
        assert len(result.chunks) == 2
        assert result.chunks[0].seccion == "9. Risk management"
        assert result.chunks[1].seccion == "3. Top priority"

        # Cost tracking comes back populated
        assert result.tokens_input == 150
        assert result.tokens_output == 42

        # Sources list is deduplicated and ordered
        assert "9. Risk management" in result.fuentes
        assert "3. Top priority" in result.fuentes

    def test_conversational_history_passed_to_claude(self, mock_recursos):
        """Multi-turn history reaches the Anthropic client correctly."""
        history = [
            {"role": "user", "content": "What is the methodology about?"},
            {"role": "assistant", "content": "It's about MNQ futures trading."},
            {"role": "user", "content": "Tell me more about risk."},
        ]
        consultar_conversacional(history)

        # Verify the client was called once
        assert mock_recursos.cliente_claude.messages.create.call_count == 1

        # Verify all three turns reached Claude (the last one enriched with context)
        call_kwargs = mock_recursos.cliente_claude.messages.create.call_args.kwargs
        sent_messages = call_kwargs["messages"]
        assert len(sent_messages) == 3
        assert sent_messages[0]["role"] == "user"
        assert sent_messages[1]["role"] == "assistant"
        assert sent_messages[2]["role"] == "user"

    def test_retrieval_uses_last_user_message(self, mock_recursos):
        """The embedding model receives the last user question, not the whole history."""
        history = [
            {"role": "user", "content": "Original question"},
            {"role": "assistant", "content": "Previous answer"},
            {"role": "user", "content": "Follow-up about filters"},
        ]
        consultar_conversacional(history)

        # The encode call should have been made with the latest user message
        encode_args = mock_recursos.modelo_embeddings.encode.call_args
        question_passed = encode_args.args[0] if encode_args.args else encode_args.kwargs.get("sentences")
        assert "Follow-up about filters" in str(question_passed)
