import os
import subprocess
import requests
import zipfile
import time
import threading
from flask import Flask

# --- CONFIGURACIÓN DEL SERVIDOR DE MINECRAFT ---
MINECRAFT_SERVER_URL = "https://minecraft.azureedge.net/bin-linux/bedrock-server-1.20.1.02.zip"
SERVER_ZIP_NAME = "bedrock-server.zip"
SERVER_DIR = "minecraft_server"

# --- CONFIGURACIÓN DEL SERVIDOR WEB (EL TRUCO PARA RENDER) ---
app = Flask(__name__)

@app.route('/')
def home():
    """Página principal que mantiene vivo el servicio de Render."""
    return "¡El servidor de Minecraft está en funcionamiento!"

def run_flask_app():
    """Inicia el servidor web Flask en el puerto que Render nos asigne."""
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- FUNCIONES DEL SERVIDOR DE MINECRAFT ---
def print_con_color(mensaje, color="verde"):
    colores = {"verde": "\033[92m", "amarillo": "\033[93m", "rojo": "\033[91m", "fin": "\033[0m"}
    print(f"{colores.get(color, '')}{mensaje}{colores['fin']}")

def descargar_servidor():
    if not os.path.exists(SERVER_ZIP_NAME):
        print_con_color(f"Descargando el servidor de Minecraft desde {MINECRAFT_SERVER_URL}...")
        try:
            r = requests.get(MINECRAFT_SERVER_URL, stream=True)
            r.raise_for_status()
            with open(SERVER_ZIP_NAME, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print_con_color("¡Descarga completada!", "verde")
        except requests.exceptions.RequestException as e:
            print_con_color(f"Error al descargar el servidor: {e}", "rojo")
            exit()

def descomprimir_servidor():
    if not os.path.exists(SERVER_DIR):
        print_con_color(f"Descomprimiendo {SERVER_ZIP_NAME}...")
        try:
            with zipfile.ZipFile(SERVER_ZIP_NAME, 'r') as zip_ref:
                zip_ref.extractall(SERVER_DIR)
            print_con_color("¡Descompresión completada!", "verde")
        except zipfile.BadZipFile:
            print_con_color(f"Error: El archivo {SERVER_ZIP_NAME} no es un ZIP válido.", "rojo")
            exit()

def iniciar_servidor_minecraft():
    """Inicia el servidor de Minecraft Bedrock."""
    server_executable = os.path.join(SERVER_DIR, "bedrock_server")
    if not os.path.exists(server_executable):
        print_con_color("El ejecutable del servidor no se encontró después de descomprimir.", "rojo")
        return

    print_con_color(f"Dando permisos de ejecución a {server_executable}...")
    os.chmod(server_executable, 0o755)
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f'./{SERVER_DIR}'
    
    print_con_color("===========================================", "verde")
    print_con_color("==  INICIANDO SERVIDOR MINECRAFT BEDROCK  ==", "verde")
    print_con_color("===========================================", "verde")
    subprocess.run([server_executable], cwd=SERVER_DIR, env=env)

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    # Iniciar el servidor web en un hilo separado (en segundo plano)
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    print_con_color("Servidor web falso iniciado para mantener Render activo.", "amarillo")

    # Ahora, configurar e iniciar el servidor de Minecraft en el hilo principal
    descargar_servidor()
    descomprimir_servidor()
    iniciar_servidor_minecraft()
