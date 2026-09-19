import streamlit as st
import os
import random
from io import BytesIO
import urllib.request

# Intentar importar openai
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("❌ La librería 'openai' no está instalada. Verifica requirements.txt")

# Modelos Shineray
SHINERAY_MODELS = [
    {"nombre": "Shineray T30", "enfoque": "Mini Truck económica", "busqueda": "mini truck"},
    {"nombre": "Shineray T32", "enfoque": "Doble cabina", "busqueda": "pickup truck"},
    {"nombre": "Shineray T50", "enfoque": "Truck capacidad", "busqueda": "cargo truck"},
    {"nombre": "Shineray X30", "enfoque": "Van carga", "busqueda": "cargo van"},
    {"nombre": "Shineray G03F", "enfoque": "Cargo Van", "busqueda": "delivery van"},
    {"nombre": "Shineray G05 Pro", "enfoque": "SUV comercial", "busqueda": "commercial SUV"}
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

def obtener_imagen(busqueda):
    url = f"https://source.unsplash.com/1024x1024/?{busqueda.replace(' ', ',')}&sig={random.randint(1,9999)}"
    try:
        response = urllib.request.urlopen(url, timeout=30)
        return BytesIO(response.read())
    except:
        return None

# Interfaz
st.set_page_config(page_title="Shineray AutoPost", layout="wide")
st.title(" Shineray AutoPost")

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    st.sidebar.success("✅ OpenAI OK")
else:
    st.sidebar.error("❌ OpenAI no configurado")

modelo = st.selectbox("Modelo:", [m["nombre"] for m in SHINERAY_MODELS])

if st.button("✨ Generar", type="primary"):
    modelo_data = next(m for m in SHINERAY_MODELS if m["nombre"] == modelo)
    
    with st.spinner("Generando..."):
        texto = generar_texto(modelo_data)
        imagen = obtener_imagen(modelo_data["busqueda"])
        
        st.session_state['texto'] = texto
        st.session_state['imagen'] = imagen

if 'texto' in st.session_state:
    st.text_area("Texto:", value=st.session_state['texto'], height=200)
    
    if st.session_state.get('imagen'):
        st.image(st.session_state['imagen'], caption=modelo)
    else:
        st.warning("No se pudo cargar la imagen")
