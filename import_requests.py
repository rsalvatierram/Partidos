import streamlit as st
import requests
from bs4 import BeautifulSoup

# ========================
# Scraping Partidos
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

st.markdown("""
<h1 style='text-align:center; color:#1E90FF; font-family: "Segoe UI", sans-serif;'>📺 Programacion Partidos y Canales en Vivo</h1>
<hr style='border:2px solid #1E90FF; margin-bottom:20px;'>
""", unsafe_allow_html=True)

# Estados
if "partido_abierto" not in st.session_state:
    st.session_state.partido_abierto = None
if "canal_abierto" not in st.session_state:
    st.session_state.canal_abierto = None  # Estado único global para un canal abierto

partidos = obtener_partidos()

# CSS
st.markdown("""
<style>
.partido-btn { width: 100%; text-align: left; font-size: 18px; background-color: #1E90FF; color: #fff; border: none; border-radius: 10px; padding: 12px; margin-bottom: 8px; cursor: pointer; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease; }
.partido-btn:hover { background-color: #1C86EE; transform: translateY(-2px); }
.canal-btn { width: 95%; text-align: left; font-size: 16px; background-color: #87CEFA; color: #000; border: none; border-radius: 8px; padding: 10px; margin-bottom: 5px; cursor: pointer; box-shadow: 0px 2px 4px rgba(0,0,0,0.1); transition: all 0.2s ease; }
.canal-btn:hover { background-color: #00BFFF; color: #fff; }
.iframe-container { width: 100%; height: 500px; margin-top: 10px; border-radius: 12px; overflow: hidden; box-shadow: 0px 4px 8px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

# Mostrar partidos y canales
for p in partidos:
    # Botón partido
    if st.button(f"⚽ {p['partido']}", key=f"partido_{p['partido']}"):
        # Alternar partido abierto
        if st.session_state.partido_abierto == p["partido"]:
            st.session_state.partido_abierto = None
            st.session_state.canal_abierto = None
        else:
            st.session_state.partido_abierto = p["partido"]
            st.session_state.canal_abierto = None  # cerrar canal abierto anterior

    # Desplegar solo si es el partido abierto
    if st.session_state.partido_abierto == p["partido"]:
        st.markdown(f"<div style='background-color:#fff; padding:15px; border-radius:15px; margin-bottom:20px;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#1E90FF;'>Canales de {p['partido']}</h4>", unsafe_allow_html=True)

        if not p["canales"]:
            st.write("⚠️ No hay canales disponibles.")
        else:
            for c in p["canales"]:
                badge = ""
                if c["badge"] == "HD": badge = "🟢HD"
                elif c["badge"] == "LIVE": badge = "🔴LIVE"

                # Botón canal
                if st.button(f"▶️ {c['nombre']} {badge}", key=f"canal_{p['partido']}_{c['nombre']}"):
                    # Al hacer click, reemplaza el canal abierto global
                    st.session_state.canal_abierto = {"partido": p["partido"], "nombre": c["nombre"], "url": c["url"]}

                # Mostrar video solo si coincide con el canal abierto global
                if st.session_state.canal_abierto:
                    canal = st.session_state.canal_abierto
                    if canal["partido"] == p["partido"] and canal["nombre"] == c["nombre"]:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        response = requests.get(canal["url"], headers=headers)
                        soup = BeautifulSoup(response.text, "html.parser")
                        iframe = soup.find("iframe")
                        if iframe:
                            video_url = iframe.get("src")
                            st.markdown(f"""
                                <div class="iframe-container">
                                    <iframe src="{video_url}" width="100%" height="100%"
                                        allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
                                        allowfullscreen></iframe>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ No se encontró iframe con el video.")
        st.markdown("</div>", unsafe_allow_html=True)

