"""
rag.py — Trading Knowledge RAG · Motor de retrieval + generacion
=================================================================
Hace 4 cosas en cadena:

    1. Recibe una pregunta (o historial conversacional) del usuario
    2. Convierte el ultimo mensaje en embedding con sentence-transformers
    3. Busca los top-K chunks mas relevantes en Chroma
    4. Inyecta esos chunks en el ultimo mensaje y llama a Claude Haiku 4.5
       con todo el historial. Devuelve respuesta + chunks + tokens.

Uso como modulo (Streamlit):
    from rag import consultar_conversacional, cargar_recursos, coste_aproximado

Uso como script (chat interactivo en terminal):
    python rag.py

Autor: jmgindicators
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import chromadb
from anthropic import Anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURACION
# ============================================================

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "metodologia_jose"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
TOP_K = 5
MAX_TOKENS_RESPUESTA = 1024

# Precios Haiku 4.5 ($/MTok)
PRECIO_INPUT = 1.0
PRECIO_OUTPUT = 5.0


# ============================================================
# SYSTEM PROMPT — texto orientado al usuario, con tildes y eñes
# ============================================================

SYSTEM_PROMPT = """Eres un asistente especializado en la metodología de trading
documentada por Jose Gonzalez. Tu única función es responder preguntas sobre
dicha metodología basándote EXCLUSIVAMENTE en el contexto que se te proporciona
en cada mensaje del usuario.

REGLAS DE COMPORTAMIENTO:

1. Responde siempre en español neutro y profesional, con ortografía correcta
   (tildes y eñes incluidas: "metodología", "señal", "operación", "análisis").

2. Habla en tercera persona referente a Jose ("Jose opera con...", "La
   metodología contempla...", "Su gestión del riesgo establece...").

3. Usa únicamente la información del contexto proporcionado o del historial
   conversacional previo. NO inventes datos, cifras, reglas ni conceptos
   que no aparezcan textualmente.

4. Si la información necesaria para responder NO aparece en el contexto,
   indícalo con claridad y brevedad. Ejemplo: "Esa pregunta no está cubierta
   por la metodología documentada de Jose."

5. EXHAUSTIVIDAD TÉCNICA: cuando el contexto incluya detalles técnicos
   concretos (cifras, niveles, listas de filtros, parámetros, reglas
   numéricas, sistemas de clasificación), INCLÚYELOS en tu respuesta. No
   simplifiques una descripción completa hasta dejarla en una sola frase
   genérica si el contexto te da información detallada disponible.

6. ESTRUCTURA CLARA: para conceptos con múltiples componentes, organiza la
   respuesta de forma legible: párrafos cortos y, cuando aporte claridad,
   listas con guiones para enumerar elementos discretos.

7. CONVERSACIONAL: si el usuario hace una pregunta de seguimiento que se
   refiere a algo de la respuesta anterior ("amplía lo del filtro 2",
   "explica eso mejor"), entiende el contexto del historial y respóndele
   con coherencia.

8. Sé directo. Sin relleno, sin frases vacías, sin disclaimers innecesarios.

9. No uses emojis bajo ningún concepto.

10. Al final de cada respuesta, añade una línea vacía y luego esta sección:

Fuentes consultadas:
- Sección X. Título de la sección
- Sección Y. Título de la sección

Lista solo las secciones que efectivamente has usado para construir la
respuesta. No listes las que aparecen en el contexto pero no aportan.

Tu objetivo es transmitir la metodología con precisión, profundidad técnica
y respeto profesional."""


# ============================================================
# CARGA DE RECURSOS (lazy, una sola vez por proceso)
# ============================================================

@dataclass
class Recursos:
    coleccion: chromadb.Collection
    modelo_embeddings: SentenceTransformer
    cliente_claude: Anthropic


_recursos: Optional[Recursos] = None


def cargar_recursos() -> Recursos:
    """Singleton ligero: carga los tres recursos pesados una sola vez."""
    global _recursos
    if _recursos is not None:
        return _recursos

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no encontrada. Revisa tu archivo .env.")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        coleccion = client.get_collection(COLLECTION_NAME)
    except Exception as e:
        raise RuntimeError(
            f"No se encuentra la coleccion '{COLLECTION_NAME}' en {CHROMA_PATH}. "
            f"Ejecuta primero 'python ingest.py'. Detalle: {e}"
        )

    modelo = SentenceTransformer(EMBEDDING_MODEL)
    cliente_claude = Anthropic(api_key=api_key)

    _recursos = Recursos(coleccion=coleccion, modelo_embeddings=modelo, cliente_claude=cliente_claude)
    return _recursos


# ============================================================
# RETRIEVAL
# ============================================================

@dataclass
class ChunkRecuperado:
    texto: str
    seccion: str
    similitud: float


def buscar_chunks(pregunta: str, k: int = TOP_K) -> list[ChunkRecuperado]:
    """Embebea la pregunta y devuelve los top-K chunks mas similares."""
    recursos = cargar_recursos()

    query_embedding = recursos.modelo_embeddings.encode(
        pregunta,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()

    resultados = recursos.coleccion.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    chunks: list[ChunkRecuperado] = []
    for doc, meta, dist in zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0],
    ):
        chunks.append(ChunkRecuperado(
            texto=doc,
            seccion=meta.get("seccion", "(sin seccion)"),
            similitud=1 - dist,
        ))
    return chunks


# ============================================================
# GENERACION
# ============================================================

def construir_mensaje_usuario(pregunta: str, chunks: list[ChunkRecuperado]) -> str:
    """Formatea contexto + pregunta en un mensaje único para Claude."""
    bloques = []
    for i, chunk in enumerate(chunks, start=1):
        bloques.append(f"[Fragmento {i} — Sección: {chunk.seccion}]\n{chunk.texto}")
    contexto = "\n\n".join(bloques)
    return (
        "=== Contexto recuperado de la metodología ===\n\n"
        f"{contexto}\n\n"
        "=== Pregunta del usuario ===\n"
        f"{pregunta}"
    )


@dataclass
class Respuesta:
    texto: str
    chunks: list[ChunkRecuperado] = field(default_factory=list)
    fuentes: list[str] = field(default_factory=list)
    tokens_input: int = 0
    tokens_output: int = 0


def consultar_conversacional(mensajes: list[dict], k: int = TOP_K) -> Respuesta:
    """Pipeline conversacional completo. Acepta historial de mensajes."""
    if not mensajes or mensajes[-1]["role"] != "user":
        raise ValueError("El ultimo mensaje del historial debe ser del usuario.")

    recursos = cargar_recursos()
    ultima_pregunta = mensajes[-1]["content"]

    chunks = buscar_chunks(ultima_pregunta, k=k)
    mensaje_enriquecido = construir_mensaje_usuario(ultima_pregunta, chunks)
    mensajes_para_claude = mensajes[:-1] + [{"role": "user", "content": mensaje_enriquecido}]

    respuesta_api = recursos.cliente_claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS_RESPUESTA,
        system=SYSTEM_PROMPT,
        messages=mensajes_para_claude,
    )

    texto = respuesta_api.content[0].text.strip()
    fuentes_unicas = list(dict.fromkeys(c.seccion for c in chunks))

    return Respuesta(
        texto=texto,
        chunks=chunks,
        fuentes=fuentes_unicas,
        tokens_input=respuesta_api.usage.input_tokens,
        tokens_output=respuesta_api.usage.output_tokens,
    )


def consultar(pregunta: str, k: int = TOP_K) -> Respuesta:
    """Atajo para consulta sin historial (modo terminal)."""
    return consultar_conversacional([{"role": "user", "content": pregunta}], k=k)


def coste_aproximado(tokens_in: int, tokens_out: int) -> float:
    """Coste estimado en USD segun precios Haiku 4.5."""
    return (tokens_in / 1_000_000) * PRECIO_INPUT + (tokens_out / 1_000_000) * PRECIO_OUTPUT


# ============================================================
# MODO INTERACTIVO (terminal)
# ============================================================

def modo_interactivo() -> None:
    print("=" * 60)
    print("CHAT  ·  Trading Knowledge RAG")
    print("Asistente especializado en la metodología de Jose Gonzalez")
    print("=" * 60)
    print("Escribe tu pregunta. Para salir: 'salir', 'exit' o Ctrl+C.\n")

    print("Cargando recursos...")
    try:
        cargar_recursos()
    except Exception as e:
        print(f"\nERROR al cargar recursos: {e}")
        sys.exit(1)
    print("Listo.\n")

    historial: list[dict] = []
    coste_total = 0.0
    consultas = 0

    while True:
        try:
            pregunta = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nHasta luego.")
            break

        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit", "q"}:
            print("\nHasta luego.")
            break

        historial.append({"role": "user", "content": pregunta})

        try:
            r = consultar_conversacional(historial)
        except Exception as e:
            print(f"\nERROR durante la consulta: {e}\n")
            historial.pop()
            continue

        historial.append({"role": "assistant", "content": r.texto})
        consultas += 1
        coste = coste_aproximado(r.tokens_input, r.tokens_output)
        coste_total += coste

        print(f"\nAsistente:\n{r.texto}\n")
        print(f"[Tokens: {r.tokens_input} in + {r.tokens_output} out  ·  "
              f"Coste: ${coste:.5f}  ·  Acumulado: ${coste_total:.5f}]\n")
        print("-" * 60)

    if consultas > 0:
        print(f"\nResumen: {consultas} consultas, coste total ${coste_total:.5f}")


if __name__ == "__main__":
    modo_interactivo()
