"""
app.py — Trading Knowledge RAG · Streamlit Chat UI
===================================================
Interfaz web sobre el motor rag.py.

Lanzar:
    streamlit run app.py

Se abre automaticamente en http://localhost:8501

Autor: jmgindicators
"""

import streamlit as st

from rag import (
    cargar_recursos,
    consultar_conversacional,
    coste_aproximado,
)


# ============================================================
# CONFIGURACION DE LA PAGINA
# ============================================================

st.set_page_config(
    page_title="Trading Knowledge RAG",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Trading Knowledge RAG · Asistente sobre metodología de Jose Gonzalez · jmgindicators",
    },
)


# ============================================================
# CACHE DE RECURSOS PESADOS
# ============================================================

@st.cache_resource(show_spinner="Cargando motor RAG (primera vez)...")
def init_recursos():
    """Carga modelo embeddings + Chroma + cliente Anthropic. Una vez por sesion."""
    return cargar_recursos()


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    .footer-note {
        color: #9ca3af;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INIT DE SESION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "coste_total" not in st.session_state:
    st.session_state.coste_total = 0.0
if "tokens_total_in" not in st.session_state:
    st.session_state.tokens_total_in = 0
if "tokens_total_out" not in st.session_state:
    st.session_state.tokens_total_out = 0
if "ultima_respuesta_chunks" not in st.session_state:
    st.session_state.ultima_respuesta_chunks = []


# ============================================================
# CARGA DE RECURSOS (cacheada)
# ============================================================

try:
    init_recursos()
except Exception as e:
    st.error(f"Error al inicializar el motor RAG: {e}")
    st.stop()


# ============================================================
# TITULO PRINCIPAL
# ============================================================

st.markdown('<div class="main-title">Trading Knowledge RAG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Metodología de Jose Gonzalez</div>',
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### Sobre el sistema")
    st.markdown("""
**Trading Knowledge RAG** es un asistente conversacional construido sobre
la metodología documentada de **Jose Gonzalez**, trader profesional de
futuros MNQ.

**Stack técnico:**
- Embeddings: paraphrase-multilingual-mpnet-base-v2 (768d)
- Base vectorial: ChromaDB (cosine similarity)
- LLM: Claude Haiku 4.5
- Top-K: 5 fragmentos por consulta
    """)

    st.divider()

    st.markdown("### Sesión actual")
    n_consultas = len([m for m in st.session_state.messages if m["role"] == "user"])
    col1, col2 = st.columns(2)
    col1.metric("Consultas", n_consultas)
    col2.metric("Coste", f"${st.session_state.coste_total:.5f}")

    if n_consultas > 0:
        st.caption(
            f"Tokens acumulados: {st.session_state.tokens_total_in:,} entrada / "
            f"{st.session_state.tokens_total_out:,} salida"
        )

    st.divider()

    if st.session_state.ultima_respuesta_chunks:
        st.markdown("### Fragmentos recuperados")
        st.caption("Última consulta procesada:")
        for i, chunk in enumerate(st.session_state.ultima_respuesta_chunks, 1):
            label = f"{i}. {chunk['seccion'][:40]}  ({chunk['similitud']:.3f})"
            with st.expander(label):
                st.text(chunk["texto"])

    st.divider()

    if st.button("Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.coste_total = 0.0
        st.session_state.tokens_total_in = 0
        st.session_state.tokens_total_out = 0
        st.session_state.ultima_respuesta_chunks = []
        st.rerun()


# ============================================================
# SUGERENCIAS INICIALES (solo si no hay conversacion)
# ============================================================

SUGERENCIAS = [
    "¿Cuál es la gestión del riesgo de Jose?",
    "¿Qué indicadores propios utiliza?",
    "¿Cómo gestiona las salidas de operaciones?",
]

if not st.session_state.messages:
    st.markdown("##### Para empezar, puedes preguntar:")
    cols = st.columns(3)
    for i, sug in enumerate(SUGERENCIAS):
        if cols[i].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": sug})
            st.rerun()


# ============================================================
# HISTORIAL DE CHAT
# ============================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ============================================================
# INPUT DEL USUARIO
# ============================================================

pregunta = st.chat_input("Escribe una pregunta sobre la metodología...")
if pregunta:
    st.session_state.messages.append({"role": "user", "content": pregunta})
    st.rerun()


# ============================================================
# PROCESAR ULTIMO MENSAJE SI ES DEL USUARIO
# ============================================================

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            try:
                respuesta = consultar_conversacional(st.session_state.messages.copy())

                st.markdown(respuesta.texto)

                st.session_state.messages.append({"role": "assistant", "content": respuesta.texto})

                coste = coste_aproximado(respuesta.tokens_input, respuesta.tokens_output)
                st.session_state.coste_total += coste
                st.session_state.tokens_total_in += respuesta.tokens_input
                st.session_state.tokens_total_out += respuesta.tokens_output

                st.session_state.ultima_respuesta_chunks = [
                    {
                        "seccion": c.seccion,
                        "similitud": c.similitud,
                        "texto": c.texto,
                    }
                    for c in respuesta.chunks
                ]

                st.rerun()

            except Exception as e:
                st.error(f"Error en la consulta: {e}")
                st.session_state.messages.pop()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer-note">'
    "Asistente experimental sobre metodología documentada. Las respuestas se "
    "generan a partir del documento de referencia y pueden contener imprecisiones. "
    "Verificar siempre con la fuente original."
    '</div>',
    unsafe_allow_html=True,
)
