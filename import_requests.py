import streamlit as st
import requests
from bs4 import BeautifulSoup

# ========================
# PARTE 1: Scraping Partidos
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
        partido_info = {}

        # El primer enlace es el título del partido
        titulo_link = li.find("a", recursive=False)  # <- solo el primer <a> directo, no los hijos
        if not titulo_link:
            continue
        partido_info["partido"] = titulo_link.get_text(" ", strip=True)

        # Los demás <a> son los canales
        canales = []
        for canal in li.select("ul li "):
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
st.title("📺 Partidos y Canales")

partidos = obtener_partidos()

for p in partidos:
    st.subheader(p["partido"])
    for c in p["canales"]:
        if st.button(f"▶️ {c['nombre']}", key=f"{p['partido']}_{c['nombre']}"):
            # Obtener el enlace del canal al hacer clic
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(c["url"], headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            iframe = soup.find("iframe")

            if iframe:
                video_url = iframe.get("src")

                # Insertar el iframe del video en Streamlit
                st.markdown(f"""
                    <iframe src="{video_url}" width="100%" height="600" 
                        allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
                        allowfullscreen></iframe>
                """, unsafe_allow_html=True)

             

            else:
                st.warning("⚠️ No se encontró iframe con el video.")



