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
        for canal in canales_links[1:]:  # omitir el primero (repite el título)
            # Detectar si tiene HD o LIVE en el nombre
            nombre = canal.get_text(strip=True)
            badge = ""
            if "HD" in nombre.upper():
                badge = "HD"
            elif "LIVE" in nombre.upper():
                badge = "LIVE"

            partido_info["canales"].append({
                "nombre": nombre,
                "url": canal.get("href"),
                "badge": badge
            })

        partidos.append(partido_info)

    return partidos

# ========================
# INTERFAZ STREAMLIT
# ========================
st.set_page_config(page_title="📺 Partidos en Vivo", layout="wide")
st.markdown("<h1 style='text-align:center; color:#FF5733;'>📺 Partidos y Canales en Vivo</h1>", unsafe_allow_html=True)

if "partido_abierto" not in st.session_state:
    st.session_state.partido_abierto = None
if "canal_abierto" not in st.session_state:
    st.session_state.canal_abierto = None

partidos = obtener_partidos()

# CSS para estilos llamativos
st.markdown("""
<style>
.partido-btn {
    width: 100%;
    text-align: left;
    font-size: 18px;
    background-color: #FFC300;
    color: #000;
    border: none;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 5px;
    cursor: pointer;
}
.canal-btn {
    width: 95%;
    text-align: left;
    font-size: 16px;
    background-color: #DAF7A6;
    color: #000;
    border: none;
    border-radius: 6px;
    padding: 8px;
    margin-bottom: 3px;
    cursor: pointer;
}
.badge {
    display: inline-block;
    padding: 2px 6px;
    font-size: 12px;
    color: white;
    border-radius: 4px;
    margin-left: 5px;
}
.badge-hd { background-color: #28a745; }
.badge-live { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Mostrar partidos y canales
for p in partidos:
    if st.button(f"⚽ {p['partido']}", key=f"partido_{p['partido']}"):
        if st.session_state.partido_abierto == p["partido"]:
            st.session_state.partido_abierto = None
            st.session_state.canal_abierto = None
        else:
            st.session_state.partido_abierto = p["partido"]
            st.session_state.canal_abierto = None

    if st.session_state.partido_abierto == p["partido"]:
        st.markdown(f"<div style='background-color:#f0f0f0; padding:10px; border-radius:10px; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#FF5733;'>Canales de {p['partido']}</h4>", unsafe_allow_html=True)

        if not p["canales"]:
            st.write("⚠️ No hay canales disponibles.")
        else:
            for c in p["canales"]:
                badge_html = ""
                if c["badge"] == "HD":
                    badge_html = '<span class="badge badge-hd">HD</span>'
                elif c["badge"] == "LIVE":
                    badge_html = '<span class="badge badge-live">LIVE</span>'

                if st.button(f"▶️ {c['nombre']} {badge_html}", key=f"canal_{p['partido']}_{c['nombre']}", unsafe_allow_html=True):
                    st.session_state.canal_abierto = c

            if st.session_state.canal_abierto:
                canal = st.session_state.canal_abierto
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(canal["url"], headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                iframe = soup.find("iframe")
                if iframe:
                    video_url = iframe.get("src")
                    st.markdown(f"""
                        <iframe src="{video_url}" width="100%" height="600"
                            allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
                            allowfullscreen style="border:2px solid #FF5733; border-radius:10px;"></iframe>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No se encontró iframe con el video.")
        st.markdown("</div>", unsafe_allow_html=True)
