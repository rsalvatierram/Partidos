import streamlit as st
import requests
from bs4 import BeautifulSoup

# ========================
# PARTE 1: Scraping Partidos
# ========================
def obtener_partidos():
    url = "https://www.rojadirectaenvivo.pl/programacion.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
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
        for canal in canales_links[1:]:  # 🔥 omitir el primero que repite el título
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

partidos = obtener_partidos()

# Lista de partidos para selección
partido_nombres = [p["partido"] for p in partidos]
partido_seleccionado = st.selectbox("Selecciona un partido:", partido_nombres)

# Buscar el partido elegido
partido = next(p for p in partidos if p["partido"] == partido_seleccionado)

st.subheader(partido["partido"])

if not partido["canales"]:
    st.write("⚠️ No hay canales disponibles.")
else:
    canal_seleccionado = st.radio(
        "Elige un canal:",
        options=[c["nombre"] for c in partido["canales"]],
        key=f"canales_{partido['partido']}"
    )

    if canal_seleccionado:
        canal_url = next(c["url"] for c in partido["canales"] if c["nombre"] == canal_seleccionado)
        
        # Scraping del enlace del canal
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(canal_url, headers=headers)
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
