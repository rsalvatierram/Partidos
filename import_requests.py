import streamlit as st
import requests
from bs4 import BeautifulSoup

# ========================
# PARTE 1: Scraping Partidos
# ========================
def obtener_partidos():
    url = "https://www.rojadirectaenvivo.pl/programacion.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    partidos = []
    for li in soup.select("ul.menu > li"):
        titulo_link = li.find("a", recursive=False)
        if not titulo_link:
            continue

        partido_info = {"partido": titulo_link.get_text(" ", strip=True), "canales": []}

        canales_links = li.select("ul li a")
        for canal in canales_links[1:]:  # 🔥 omitir el primero (repite el título)
            partido_info["canales"].append({
                "nombre": canal.get_text(strip=True),
                "url": canal.get("href")
            })

        partidos.append(partido_info)

    return partidos

# ========================
# INTERFAZ STREAMLIT
# ========================

st.title("📺 Partidos y Canales")

# Inicializar estado
if "partido_abierto" not in st.session_state:
    st.session_state.partido_abierto = None
if "canal_abierto" not in st.session_state:
    st.session_state.canal_abierto = None

partidos = obtener_partidos()

for p in partidos:
    # Botón del partido
    if st.button(f"⚽ {p['partido']}", key=f"partido_{p['partido']}"):
        # Si ya estaba abierto, cerrar todo; si no, abrir este partido
        if st.session_state.partido_abierto == p["partido"]:
            st.session_state.partido_abierto = None
            st.session_state.canal_abierto = None
        else:
            st.session_state.partido_abierto = p["partido"]
            st.session_state.canal_abierto = None  # cerrar canal anterior

    # Mostrar los canales SOLO si este partido está abierto
    if st.session_state.partido_abierto == p["partido"]:
        st.subheader(f"Canales de {p['partido']}")

        if not p["canales"]:
            st.write("⚠️ No hay canales disponibles.")
        else:
            for c in p["canales"]:
                if st.button(f"▶️ {c['nombre']}", key=f"canal_{p['partido']}_{c['nombre']}"):
                    st.session_state.canal_abierto = c  # guardar canal abierto

            # Mostrar iframe del canal abierto
            if st.session_state.canal_abierto:
                canal = st.session_state.canal_abierto
                # Obtener el iframe del canal
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(canal["url"], headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                iframe = soup.find("iframe")
                if iframe:
                    video_url = iframe.get("src")
                    st.markdown(f"""
                        <iframe src="{video_url}" width="100%" height="600"
                            allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
                            allowfullscreen></iframe>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No se encontró iframe con el video.")
