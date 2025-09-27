import streamlit as st
import requests
from bs4 import BeautifulSoup
from streamlit_webrtc import webrtc_streamer

# ========================
# FUNCIONES DE SCRAPING
# ========================
def obtener_partidos():
    url = "https://www.rojadirectaenvivo.pl/programacion.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    partidos = []
    for li in soup.select("ul.menu > li"):
        titulo_link = li.find("a", recursive=False)
        if not titulo_link:
            continue
        partido_info = {"partido": titulo_link.get_text(" ", strip=True)}

        canales = []
        canales_links = li.select("ul li a")
        for canal in canales_links[1:]:  # Saltar el primer link si es redundante
            canales.append({
                "nombre": canal.get_text(strip=True),
                "url": canal.get("href")
            })

        partido_info["canales"] = canales
        partidos.append(partido_info)
    return partidos

# ========================
# INTERFAZ STREAMLIT
# ========================
st.set_page_config(page_title="Partidos en Vivo", layout="wide")
st.markdown("<h1 style='text-align:center;'>📺 Partidos y Canales</h1>", unsafe_allow_html=True)

partidos = obtener_partidos()

# Mantenemos estado para solo desplegar un partido
if "partido_desplegado" not in st.session_state:
    st.session_state.partido_desplegado = None

for p in partidos:
    # Botón estilo tarjeta
    if st.button(f"⚽ {p['partido']}", key=p['partido']):
        st.session_state.partido_desplegado = p["partido"]

    # Mostrar canales solo si es el partido seleccionado
    if st.session_state.partido_desplegado == p["partido"]:
        for c in p["canales"]:
            st.markdown(f"**▶️ Canal:** {c['nombre']}")
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(c["url"], headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                iframe = soup.find("iframe")
                if iframe:
                    video_url = iframe.get("src")
                    st.markdown(f"""
                        <iframe src="{video_url}" width="100%" height="400" 
                            allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                            allowfullscreen></iframe>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No se encontró iframe con el video.")
            except Exception as e:
                st.error(f"Error al cargar canal: {e}")

        # Botón para transmitir pantalla
        st.markdown("<h3>💻 Transmitir Pantalla</h3>", unsafe_allow_html=True)
        webrtc_streamer(key="screen_share", video_processor_factory=None, media_stream_constraints={"video": True, "audio": True})
