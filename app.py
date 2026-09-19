import streamlit as st
import openai
import requests
import os
import random
from io import BytesIO

# Configuración de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Modelos Shineray
SHINERAY_MODELS = [
    {"nombre": "Shineray T30", "enfoque": "Mini Truck económica, ideal para repartos urbanos y emprendedores. Chasis reforzado."},
    {"nombre": "Shineray T32", "enfoque": "Doble cabina, perfecta para llevar equipo de trabajo y personal con comodidad."},
    {"nombre": "Shineray T50", "enfoque": "Truck de mayor capacidad, resistencia extrema para trabajos pesados y flotillas."},
    {"nombre": "Shineray X30", "enfoque": "Van de carga cerrada, seguridad para tu mercancía y puertas traseras dobles."},
    {"nombre": "Shineray G03F", "enfoque": "Cargo Van moderna, tecnología y eficiencia de combustible para la ciudad."},
    {"nombre": "Shineray G05 Pro", "enfoque": "SUV comercial versátil, combina confort para pasajeros con capacidad de carga."}
]

def generar_texto_facebook(modelo):
    prompt = f"""
    Actúa como un experto en marketing digital para una agencia de vehículos comerciales en Guadalajara, México.
    Crea una publicación de Facebook corta, atractiva y profesional (máximo 150 palabras) sobre el siguiente vehículo:
    Vehículo: {modelo['nombre']}
    Características clave: {modelo['enfoque']}
    
    Requisitos:
    - Usa emojis relevantes (🚛, ✅, 💰, ).
    - Incluye un llamado a la acción claro.
    - Incluye 3 hashtags relevantes al final.
    - Tono: Profesional, confiable y entusiasta.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al generar texto: {e}"

def generar_imagen_dalle(modelo_nombre):
    """Genera imagen usando DALL-E 3"""
    prompt = f"Professional commercial photography of a {modelo_nombre} white utility truck, working in Guadalajara Mexico, sunny day, realistic, high resolution, automotive advertisement style, clean background"
    
    try:
        response = openai.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1,
        )
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        return BytesIO(image_response.content)
    except Exception as e:
        st.error(f"Error generando imagen: {e}")
        return None

# INTERFAZ STREAMLIT
st.set_page_config(page_title="Shineray AutoPost", page_icon="🚛", layout="wide")

st.title("🚛 Shineray AutoPost")
st.markdown("### Genera publicaciones con IA para Facebook")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Configuración")

if os.getenv("OPENAI_API_KEY"):
    st.sidebar.success("✅ OpenAI Configurado")
else:
    st.sidebar.error(" Falta OPENAI_API_KEY en Secrets")

# Contenido principal
st.subheader("🎨 Crear Nueva Publicación")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Paso 1: Selecciona el vehículo")
    modelo_seleccionado = st.selectbox("Modelo Shineray:", [m["nombre"] for m in SHINERAY_MODELS])
    
    if st.button("✨ Generar Contenido con IA", type="primary", use_container_width=True):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("❌ Falta la clave de OpenAI. Ve a 'Manage app' → 'Secrets'")
        else:
            with st.spinner("La IA está trabajando (esto puede tomar 20-30 segundos)..."):
                modelo_data = next(m for m in SHINERAY_MODELS if m["nombre"] == modelo_seleccionado)
                texto_generado = generar_texto_facebook(modelo_data)
                imagen_bytes = generar_imagen_dalle(modelo_data["nombre"])
                
                st.session_state['texto'] = texto_generado
                st.session_state['imagen_bytes'] = imagen_bytes
                st.session_state['modelo'] = modelo_seleccionado

with col2:
    if 'texto' in st.session_state and 'imagen_bytes' in st.session_state:
        st.markdown("### Paso 2: Copia y publica")
        
        if st.session_state['imagen_bytes']:
            st.image(st.session_state['imagen_bytes'], caption=f"Imagen para {st.session_state['modelo']}", use_container_width=True)
        else:
            st.warning("⚠️ No se pudo generar la imagen. Intenta de nuevo.")
        
        st.markdown("**💡 Tip:** Haz clic derecho en la imagen y selecciona 'Copiar imagen' para pegarla en Facebook")
        
        st.markdown("---")
        
        st.markdown("### 📝 Texto del post:")
        st.text_area(
            "Copia este texto:", 
            value=st.session_state['texto'], 
            height=200,
            key="texto_final"
        )
        
        st.markdown("""
        ### 📋 Instrucciones para publicar:
        1. **Copia el texto** de arriba (selecciónalo y Ctrl+C)
        2. **Copia la imagen** (clic derecho sobre la imagen → Copiar imagen)
        3. Ve a tu **Facebook personal**
        4. Crea una **nueva publicación**
        5. **Pega el texto** y **pega la imagen**
        6. ¡Publica! 
        """)
