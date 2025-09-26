import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

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
        titulo = li.find("a").get_text(" ", strip=True)
        partido_info["partido"] = titulo

        canales = []
        for canal in li.select("ul li a"):
            # ⚡ en lugar del link directo, lo mandamos a nuestro endpoint
            proxy_url = f"/obtenerenlace?url={canal.get('href')}"
            canales.append({
                "nombre": canal.get_text(strip=True),
                "url": proxy_url
            })

        partido_info["canales"] = canales
        partidos.append(partido_info)

    return partidos


# ========================
# PARTE 2: Página principal
# ========================
template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Partidos y Canales</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
        .partido { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
        h2 { margin: 0 0 10px 0; font-size: 18px; color: #333; }
        ul { list-style: none; padding: 0; }
        li { margin: 5px 0; }
        a { text-decoration: none; color: #007bff; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>📺 Partidos y Canales</h1>
    {% for p in partidos %}
        <div class="partido">
            <h2>{{ p.partido }}</h2>
            <ul>
                {% for c in p.canales %}
                    <li><a href="{{ c.url }}" target="_blank">{{ c.nombre }}</a></li>
                {% endfor %}
            </ul>
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/partidos")
def index():
    return render_template_string(template, partidos=obtener_partidos())





@app.route("/obtenerenlace", methods=["GET"])
def obtener_enlace():
    url = request.args.get("url")
    if not url:
        return "<h3>❌ Se requiere el parámetro 'url'.</h3>", 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"<h3>❌ Error al acceder a la página: {response.status_code}</h3>", 500

    soup = BeautifulSoup(response.text, "html.parser")
    iframe = soup.find("iframe")

    if not iframe:
        return "<h3>❌ No se encontró ningún iframe con el video.</h3>", 404


    video_url = iframe.get("src")


    # Plantilla con hack de audio
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Reproductor</title>
        <style>
            body { margin: 0; background: black; display: flex; justify-content: center; align-items: center; height: 100vh; }
            iframe { width: 90%; height: 90%; border: none; }
        </style>
        <script>
            // Bloqueamos WSUnmute
            window.WSUnmute = function(){ console.log("WSUnmute() bloqueado ✔"); };

            // Intento forzar audio en el iframe
            window.addEventListener("load", () => {
                const frame = document.querySelector("iframe");
                try {
                    frame.contentWindow.postMessage("unmute", "*");
                } catch (e) {
                    console.log("No se pudo acceder al iframe directamente:", e);
                }
            });

            // Listener para cuando el iframe soporte mensajes
            window.addEventListener("message", (e) => {
                console.log("Mensaje recibido del iframe:", e.data);
            });
        </script>
    </head>
    <body>
        <iframe 
            src="{{ video_url }}" 
            allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
            allowfullscreen>
        </iframe>
    </body>
    </html>
    """

    return render_template_string(template, video_url=video_url)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
