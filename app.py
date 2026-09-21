import streamlit as st
import os

# Intentar importar openai
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ La librería 'openai' no está instalada. Verifica requirements.txt")

# Modelos Shineray
# "imagen" apunta a un archivo local en la carpeta images/ del repo.
# Si un modelo todavía no tiene foto local, se muestra un aviso en vez de romper la app.
SHINERAY_MODELS = [
    {"nombre": "Shineray T30", "enfoque": "Mini Truck económica", "imagen": "/t30.jpg"},
    {"nombre": "Shineray T32", "enfoque": "Doble cabina", "imagen": "/t32.jpg"},
    {"nombre": "Shineray T50", "enfoque": "Truck capacidad", "imagen": "/t50.jpg"},
    {"nombre": "Shineray X30", "enfoque": "Van carga", "imagen": "/x30.jpg"},
    {"nombre": "Shineray G03F", "enfoque": "Cargo Van", "imagen": None},
    {"nombre": "Shineray G05 Pro", "enfoque": "SUV comercial", "imagen": None},
]

def generar_texto(modelo):
    if not OPENAI_AVAILABLE:
        return "Error: OpenAI no disponible"

    prompt = f"Crea un post de Facebook para {modelo['nombre']}: {modelo['enfoque']}. Usa emojis y hashtags."

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def obtener_imagen(modelo_data):
    """Usa la foto real local del modelo en vez de buscar una foto random en internet
    (source.unsplash.com dejó de funcionar por completo desde junio de 2024)."""
    ruta = modelo_data.get("imagen")
    if ruta and os.path.exists(ruta):
        return ruta
    return None

# Interfaz
st.set_page_config(page_title="Shineray AutoPost", layout="wide")
st.title("Shineray AutoPost")

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    st.sidebar.success("✅ OpenAI OK")
else:
    st.sidebar.error("❌ OpenAI no configurado")

modelo = st.selectbox("Modelo:", [m["nombre"] for m in SHINERAY_MODELS])

if st.button("✨ Generar", type="primary"):
    modelo_data = next(m for m in SHINERAY_MODELS if m["nombre"] == modelo)

    with st.spinner("Generando..."):
        texto = generar_texto(modelo_data)
        imagen = obtener_imagen(modelo_data)

        st.session_state['texto'] = texto
        st.session_state['imagen'] = imagen
        st.session_state['modelo_sel'] = modelo

if 'texto' in st.session_state:
    st.text_area("Texto:", value=st.session_state['texto'], height=200)

    if st.session_state.get('imagen'):
        st.image(st.session_state['imagen'], caption=st.session_state.get('modelo_sel'))
    else:
        st.warning("Este modelo todavía no tiene foto cargada en images/. Sube la foto real y agrégala en SHINERAY_MODELS.")
