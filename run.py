#SE CORRE LA APP (BACKEND+ FRONTEND)
import subprocess
import webbrowser
import time
import os

# Ruta a tu entorno virtual (ajusta si estás en Linux o Mac)
VENV_PYTHON = os.path.join("backend", "venv", "Scripts", "python.exe")
APP_PATH = os.path.join("backend", "app.py")
FRONTEND_HTML = os.path.abspath(os.path.join("frontend", "index.html"))

# Comando para correr el backend
backend_process = subprocess.Popen([VENV_PYTHON, APP_PATH])

# Esperar unos segundos a que Flask se inicie
time.sleep(2)

# Abrir el frontend en el navegador
webbrowser.open(f"file:///{FRONTEND_HTML.replace(os.sep, '/')}")

print("Backend iniciado y frontend abierto en el navegador.")

try:
    backend_process.wait()
except KeyboardInterrupt:
    print("Cerrando servidor...")
    backend_process.terminate()
