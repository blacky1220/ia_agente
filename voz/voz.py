import os
import re
import uuid
import threading
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

from config import NOMBRE_IA


# ==========================================
# RUTAS Y .ENV
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=True)

ELEVENLABS_API_KEY = (
    os.getenv("ELEVENLABS_API_KEY")
    or os.getenv("ELEVEN_API_KEY")
    or ""
).strip().strip('"').strip("'")

# Puedes cambiar esta voz desde tu .env
ELEVENLABS_VOICE_ID = (
    os.getenv("ELEVENLABS_VOICE_ID")
    or "EXAVITQu4vr4xnSDxMaL"
).strip()

MODEL_ID = "eleven_multilingual_v2"

AUDIO_DIR = BASE_DIR / "temp_audio"
AUDIO_DIR.mkdir(exist_ok=True)

hablando_lock = threading.Lock()

client = None

if ELEVENLABS_API_KEY:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


# ==========================================
# LIMPIEZA
# ==========================================

def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""

    texto = re.sub(
        r"\[PENSAMIENTO\].*?\[/PENSAMIENTO\]",
        "",
        texto,
        flags=re.DOTALL | re.IGNORECASE
    )

    texto = re.sub(
        r"```.*?```",
        "",
        texto,
        flags=re.DOTALL
    )

    texto = texto.replace("**", "")
    texto = texto.replace("*", "")
    texto = texto.replace("#", "")
    texto = texto.replace("`", "")

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def humanizar_texto(texto: str) -> str:
    reemplazos = {
        r"\bhmm\b": "mmm...",
        r"\bmmm\b": "mmm...",
        r"\beh\b": "ehhh...",
        r"\bah\b": "ahhh...",
        r"\bok\b": "okey...",
        r"\bokay\b": "okey...",
        r"\bvale\b": "vale..."
    }

    for patron, nuevo in reemplazos.items():
        texto = re.sub(patron, nuevo, texto, flags=re.IGNORECASE)

    return texto


# ==========================================
# REPRODUCCIÓN
# ==========================================

def guardar_audio_stream(audio_stream, ruta_audio: Path):
    with open(ruta_audio, "wb") as f:
        if isinstance(audio_stream, bytes):
            f.write(audio_stream)
            return

        for chunk in audio_stream:
            if isinstance(chunk, bytes):
                f.write(chunk)
            else:
                f.write(bytes(chunk))


def reproducir_audio(ruta_audio: Path):
    subprocess.run(
        ["mpv", "--no-terminal", "--really-quiet", str(ruta_audio)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# ==========================================
# FALLBACK LOCAL
# ==========================================

def hablar_fallback(texto: str):
    """
    Fallback simple usando espeak-ng.
    No suena tan realista, pero evita que Sarah se caiga.
    Instala con:
    sudo pacman -S espeak-ng
    """
    print("[Sarah] Usando voz fallback local.")

    subprocess.run(
        ["espeak-ng", "-v", "es-mx", texto],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# ==========================================
# VOZ PRINCIPAL
# ==========================================

def hablar(texto: str, velocidad: float = 1.0, modo: str = "normal"):
    texto = limpiar_texto(texto)
    texto = humanizar_texto(texto)

    if not texto:
        return

    with hablando_lock:
        print(f"\n[{NOMBRE_IA}] {texto}")

        if client is None:
            print("[!] No hay ELEVENLABS_API_KEY. Usando fallback.")
            hablar_fallback(texto)
            return

        ruta_audio = AUDIO_DIR / f"sarah_{uuid.uuid4().hex}.mp3"

        try:
            audio_stream = client.text_to_speech.convert(
                text=texto,
                voice_id=ELEVENLABS_VOICE_ID,
                model_id=MODEL_ID,
                output_format="mp3_44100_128"
            )

            guardar_audio_stream(audio_stream, ruta_audio)
            reproducir_audio(ruta_audio)

        except Exception as e:
            error = str(e)

            if "paid_plan_required" in error or "Free users cannot use library voices" in error:
                print("[!] Esa voz de ElevenLabs requiere plan pagado.")
                print("[!] Cambia ELEVENLABS_VOICE_ID por una voz permitida o usa Kokoro.")
            else:
                print(f"[!] Error con ElevenLabs: {e}")

            hablar_fallback(texto)

        finally:
            if ruta_audio.exists():
                try:
                    ruta_audio.unlink()
                except Exception:
                    pass


if __name__ == "__main__":
    hablar("Sistemas listos. Estoy contigo, Rafael. ¿En qué vamos a trabajar hoy?")