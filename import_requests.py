import streamlit as st
import requests
from bs4 import BeautifulSoup

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
        titulo = li.find("a").get_text(" ", strip=True)
        partido_info["partido"] = titulo

        canales = []
        for canal in li.select("ul li a"):
            canales.append({
                "nombre": canal.get_text(strip=True),
                "url": canal.get("href")
            })

        partido_info["canales"] = canales
        partidos.append(partido_info)

    return partidos


# === INTERFAZ STREAMLIT ===
st.title("📺 Partidos y Canales")

partidos = obtener_partidos()

for p in partidos:
    st.subheader(p["partido"])
    for c in p["canales"]:
        st.markdown(f"[{c['nombre']}]({c['url']})")
