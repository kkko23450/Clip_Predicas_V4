#!/usr/bin/env python3
"""
verificar.py - Revisa que todo lo necesario esté instalado y funcionando, y te dice cómo arreglar lo que falle.

    python verificar.py
"""
import importlib
import os
import shutil
import subprocess
import sys

OK, MAL, AVISO = "✅", "❌", "⚠️ "
problemas = 0


def linea(estado, texto, arreglo=None):
    global problemas
    print(f"{estado} {texto}")
    if arreglo:
        print("     Cómo arreglarlo:")
        for a in arreglo.strip().splitlines():
            print(f"       {a}")
    if estado == MAL:
        problemas += 1


def correr(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return ""


print(f"Python {sys.version.split()[0]}\n")

# ---- ffmpeg ----
if shutil.which("ffmpeg") and shutil.which("ffprobe"):
    filtros = correr(["ffmpeg", "-hide_banner", "-filters"])
    if " ass " in filtros and " select " in filtros and " sidechaincompress " in filtros:
        linea(OK, "ffmpeg (con subtítulos, cortes y ducking de música)")
    else:
        linea(MAL, "ffmpeg está instalado pero le faltan filtros (subtítulos 'ass', 'select' o 'sidechaincompress')",
              "sudo apt-get update && sudo apt-get install -y ffmpeg")
else:
    linea(MAL, "No encuentro ffmpeg", "sudo apt-get update && sudo apt-get install -y ffmpeg")

# ---- OpenCV (detección de cara para el zoom y las portadas) ----
ARREGLO_CV = ("python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless "
              "opencv-contrib-python-headless\n"
              "python -m pip install --no-cache-dir opencv-python-headless")
try:
    import cv2
    if not hasattr(cv2, "CascadeClassifier"):
        linea(MAL, f"OpenCV está roto (hay dos versiones instaladas a la vez). cv2 en: {getattr(cv2, '__file__', None)}",
              ARREGLO_CV)
    else:
        c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if c.empty():
            linea(MAL, "OpenCV no pudo cargar el detector de caras", ARREGLO_CV)
        else:
            linea(OK, f"OpenCV {cv2.__version__} (detección de cara)")
except ImportError:
    linea(MAL, "OpenCV no está instalado", "python -m pip install opencv-python-headless")

# ---- librerías de Python ----
for mod, pip_name, para in [
    ("numpy", "numpy", "audio y análisis"),
    ("faster_whisper", "faster-whisper", "transcribir"),
    ("google.genai", "google-genai", "Gemini"),
    ("gradio", "gradio", "el panel"),
    ("yt_dlp", "yt-dlp", "bajar videos de links"),
    ("gdown", "gdown", "bajar de Google Drive"),
    ("requests", "requests", "redes"),
]:
    try:
        importlib.import_module(mod)
        linea(OK, f"{pip_name} ({para})")
    except Exception as e:
        linea(MAL, f"{pip_name} no se puede usar ({para}): {type(e).__name__}",
              f"python -m pip install -U {pip_name}")

# ---- clave de Gemini ----
if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
    linea(OK, "Clave de Gemini (GEMINI_API_KEY) cargada")
else:
    linea(MAL, "Falta la clave de Gemini (GEMINI_API_KEY)",
          "En GitHub: Settings > Secrets and variables > Codespaces > New secret, nombre GEMINI_API_KEY.\n"
          "Después reiniciá el Codespace. Clave gratis en https://aistudio.google.com/apikey")

# ---- fuente de los subtítulos (no es grave si falta) ----
if shutil.which("fc-list") and "montserrat" in correr(["fc-list"]).lower():
    linea(OK, "Fuente Montserrat (subtítulos)")
else:
    linea(AVISO, "No encuentro la fuente Montserrat: los subtítulos saldrán con otra letra (no es grave)",
          "sudo apt-get install -y fonts-montserrat")

# ---- archivos del proyecto ----
aqui = os.path.dirname(os.path.abspath(__file__))
faltan = [f for f in ("clipper.py", "auto_clips.py", "panel.py", "portadas.py", "redes.py", "guia_contenido.md")
          if not os.path.exists(os.path.join(aqui, f))]
if faltan:
    linea(MAL, f"Faltan archivos del proyecto: {', '.join(faltan)}")
else:
    linea(OK, "Archivos del proyecto completos")

print()
if problemas:
    print(f"Hay {problemas} problema(s) para arreglar (mirá las líneas con {MAL}). Después volvé a correr: python verificar.py")
else:
    print("Todo en orden. Ya podés generar clips.")
sys.exit(0)
