import os
import subprocess
import requests
import zipfile
import time

# --- CONFIGURACIÓN ---
# URL del servidor oficial de Minecraft Bedrock para Linux
MINECRAFT_SERVER_URL = "https://minecraft.azureedge.net/bin-linux/bedrock-server-1.20.1.02.zip"
SERVER_ZIP_NAME = "bedrock-server.zip"
SERVER_DIR = "minecraft_server"

# --- FUNCIONES ---

def print_con_color(mensaje, color="verde"):
    """Imprime mensajes con colores para que se vean mejor."""
    colores = {
        "verde": "\033[92m",
        "amarillo": "\033[93m",
        "rojo": "\033[91m",
        "fin": "\033[0m"
    }
    print(f"{colores.get(color, '')}{mensaje}{colores['fin']}")

def descargar_servidor():
    """Descarga el archivo del servidor si no existe."""
    if os.path.exists(SERVER_ZIP_NAME):
        print_con_color(f"El archivo {SERVER_ZIP_NAME} ya existe. Saltando descarga.", "amarillo")
        return

    print_con_color(f"Descargando el servidor de Minecraft desde {MINECRAFT_SERVER_URL}...")
    try:
        with requests.get(MINECRAFT_SERVER_URL, stream=True) as r:
            r.raise_for_status()
            with open(SERVER_ZIP_NAME, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print_con_color("¡Descarga completada!", "verde")
    except requests.exceptions.RequestException as e:
        print_con_color(f"Error al descargar el servidor: {e}", "rojo")
        exit() # Salir si no se puede descargar

def descomprimir_servidor():
    """Descomprime el servidor si el directorio no existe."""
    if os.path.exists(SERVER_DIR):
        print_con_color(f"El directorio del servidor {SERVER_DIR} ya existe. Saltando descompresión.", "amarillo")
        return

    print_con_color(f"Descomprimiendo {SERVER_ZIP_NAME}...")
    try:
        with zipfile.ZipFile(SERVER_ZIP_NAME, 'r') as zip_ref:
            zip_ref.extractall(SERVER_DIR)
        print_con_color("¡Descompresión completada!", "verde")
    except zipfile.BadZipFile:
        print_con_color(f"Error: El archivo {SERVER_ZIP_NAME} no es un ZIP válido o está corrupto.", "rojo")
        exit()

def iniciar_servidor():
    """Inicia el servidor de Minecraft."""
    server_executable = os.path.join(SERVER_DIR, "bedrock_server")

    # Dar permisos de ejecución al archivo del servidor (muy importante en Linux/Render)
    print_con_color(f"Dando permisos de ejecución a {server_executable}...")
    os.chmod(server_executable, 0o755)

    # Configurar la variable de entorno para las librerías
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f'./{SERVER_DIR}'

    print_con_color("===========================================", "verde")
    print_con_color("==  INICIANDO SERVIDOR MINECRAFT BEDROCK  ==", "verde")
    print_con_color("===========================================", "verde")
    print_con_color("Para detener el servidor, cierra este programa.", "amarillo")
    
    # Ejecutar el servidor
    subprocess.run([server_executable], cwd=SERVER_DIR, env=env)


# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    print_con_color("Iniciando script de configuración del servidor...")
    descargar_servidor()
    descomprimir_servidor()
    
    # Damos un pequeño respiro al sistema antes de iniciar
    time.sleep(2)
    
    iniciar_servidor()
