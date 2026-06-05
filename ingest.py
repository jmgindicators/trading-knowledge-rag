"""
ingest.py — Trading Knowledge RAG · Bloque 3
============================================
Pipeline de ingesta del documento de metodologia:

    1. Carga data/metodologia.md
    2. Trocea respetando estructura markdown (headers) con fallback recursivo
    3. Genera embeddings multilingues con sentence-transformers
    4. Persiste todo en Chroma local (carpeta chroma_db/)

Uso:
    python ingest.py

Autor: jmgindicators
Stack: langchain-text-splitters, sentence-transformers, chromadb
"""

from __future__ import annotations

import time
from pathlib import Path

import chromadb
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURACION — todas las decisiones del Bloque 3 viven aqui
# ============================================================

PROJECT_ROOT = Path(__file__).parent
DOC_PATH = PROJECT_ROOT / "data" / "metodologia.md"
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "metodologia_jose"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Headers markdown que detectamos para respetar la estructura del documento.
# Nomenclatura semantica:
#   #   -> documento_titulo (el titulo global del documento)
#   ##  -> seccion          (las 14 secciones reales: Vision, Edge, etc.)
#   ### -> subseccion       (apartados internos como "Como funciona" dentro de una seccion)
HEADERS_TO_SPLIT_ON = [
    ("#", "documento_titulo"),
    ("##", "seccion"),
    ("###", "subseccion"),
]


# ============================================================
# 1. CARGA DEL DOCUMENTO
# ============================================================

def cargar_documento(path: Path) -> str:
    """Lee el archivo markdown completo como texto UTF-8."""
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra el documento: {path}")

    print(f"[1/5] Cargando documento: {path.name}")
    contenido = path.read_text(encoding="utf-8")
    print(f"      -> {len(contenido):,} caracteres leidos")
    return contenido


# ============================================================
# 2. CHUNKING (markdown-aware + recursivo de fallback)
# ============================================================

def trocear_documento(texto: str) -> list[dict]:
    """
    Trocea el documento en dos pasadas:
      a) Por headers markdown -> respeta la estructura semantica
      b) Si una seccion sigue siendo grande, la parte recursivamente
         por parrafos, saltos de linea, frases o espacios.

    Devuelve lista de dicts con 'texto' y 'metadatos'.
    """
    print(f"[2/5] Troceando documento (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    docs_por_seccion = md_splitter.split_text(texto)
    print(f"      -> {len(docs_por_seccion)} bloques detectados por headers")

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks_finales: list[dict] = []
    for doc in docs_por_seccion:
        sub_chunks = char_splitter.split_text(doc.page_content)
        for idx, sub_texto in enumerate(sub_chunks):
            chunks_finales.append({
                "texto": sub_texto,
                "metadatos": {
                    "documento_titulo": doc.metadata.get("documento_titulo", ""),
                    "seccion": doc.metadata.get("seccion", ""),
                    "subseccion": doc.metadata.get("subseccion", ""),
                    "chunk_index": idx,
                    "fuente": "metodologia.md",
                },
            })

    print(f"      -> {len(chunks_finales)} chunks finales generados")

    # Muestra rapida para verificacion visual
    print("\n      Muestra de los 3 primeros chunks:")
    for i, c in enumerate(chunks_finales[:3]):
        preview = c["texto"][:120].replace("\n", " ")
        seccion = c["metadatos"].get("seccion", "(sin seccion)")
        print(f"        [{i}] {seccion[:50]} | {preview}...")
    print()

    return chunks_finales


# ============================================================
# 3. CARGA DEL MODELO DE EMBEDDINGS
# ============================================================

def cargar_modelo_embeddings() -> SentenceTransformer:
    """
    Carga el modelo multilingue. La primera vez descarga ~1.1GB
    desde HuggingFace al cache local de tu usuario.
    """
    print(f"[3/5] Cargando modelo de embeddings: {EMBEDDING_MODEL.split('/')[-1]}")
    print("      (ya cacheado en local, sera instantaneo)")
    inicio = time.time()
    modelo = SentenceTransformer(EMBEDDING_MODEL)
    elapsed = time.time() - inicio
    print(f"      -> Modelo cargado en {elapsed:.1f}s")
    return modelo


# ============================================================
# 4. GENERACION DE EMBEDDINGS
# ============================================================

def generar_embeddings(
    chunks: list[dict],
    modelo: SentenceTransformer,
) -> list[list[float]]:
    """
    Convierte cada chunk en un vector denso de 768 dimensiones.
    Se procesan todos en batch para maxima velocidad.

    normalize_embeddings=True normaliza los vectores a longitud 1,
    lo cual hace que cosine similarity y dot product sean equivalentes
    y mas rapidos de calcular en Chroma.
    """
    print(f"[4/5] Generando embeddings de {len(chunks)} chunks")
    textos = [c["texto"] for c in chunks]

    inicio = time.time()
    embeddings = modelo.encode(
        textos,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    elapsed = time.time() - inicio

    embeddings_list = [emb.tolist() for emb in embeddings]
    dims = len(embeddings_list[0])
    print(f"      -> {len(embeddings_list)} vectores de {dims} dimensiones en {elapsed:.1f}s")
    return embeddings_list


# ============================================================
# 5. ALMACENAMIENTO EN CHROMA
# ============================================================

def almacenar_en_chroma(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> None:
    """
    Crea/abre el PersistentClient e inserta todos los chunks.

    Estrategia: si la coleccion existe, la eliminamos y la creamos
    de nuevo. Asi garantizamos coherencia total con el documento
    actual y evitamos chunks fantasma de versiones anteriores.
    """
    print(f"[5/5] Almacenando en Chroma: {CHROMA_PATH}")

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"      -> Coleccion '{COLLECTION_NAME}' existe. Eliminando para re-ingest limpio.")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # IDs deterministicos basados en seccion (##) + indice
    ids: list[str] = []
    documentos: list[str] = []
    metadatos: list[dict] = []
    for i, chunk in enumerate(chunks):
        seccion = chunk["metadatos"].get("seccion", "") or "sin_seccion"
        seccion_norm = "".join(c if c.isalnum() else "_" for c in seccion)[:30]
        ids.append(f"chunk_{i:03d}_{seccion_norm}")
        documentos.append(chunk["texto"])
        metadatos.append(chunk["metadatos"])

    collection.add(
        ids=ids,
        documents=documentos,
        embeddings=embeddings,
        metadatas=metadatos,
    )

    print(f"      -> {collection.count()} chunks insertados en coleccion '{COLLECTION_NAME}'")


# ============================================================
# ORQUESTACION
# ============================================================

def main() -> None:
    print("=" * 60)
    print("INGEST  ·  Trading Knowledge RAG")
    print("=" * 60)

    t0 = time.time()

    texto = cargar_documento(DOC_PATH)
    chunks = trocear_documento(texto)
    modelo = cargar_modelo_embeddings()
    embeddings = generar_embeddings(chunks, modelo)
    almacenar_en_chroma(chunks, embeddings)

    total = time.time() - t0
    print("=" * 60)
    print(f"INGEST COMPLETADO en {total:.1f}s")
    print(f"Base vectorial lista en: {CHROMA_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
