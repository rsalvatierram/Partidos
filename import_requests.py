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

for p in partidos:
    with st.expander(p["partido"]):  # 🔥 desplegable por partido
        if not p["canales"]:
            st.write("⚠️ No hay canales disponibles.")
            continue

        # Menú de selección de canal
        canal_seleccionado = st.radio(
            f"Canales disponibles para {p['partido']}:",
            options=[c["nombre"] for c in p["canales"]],
            key=p["partido"]
        )

        if canal_seleccionado:
            canal_url = next(c["url"] for c in p["canales"] if c["nombre"] == canal_seleccionado)
            
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
