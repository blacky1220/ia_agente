import os
import re
import time
import threading
from typing import List

import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro

from config import (
    NOMBRE_IA,
    KOKORO_MODEL_PATH,
    KOKORO_VOICES_PATH
)


# ==========================================
# CONFIGURACIÓN DE VOZ
# ==========================================

SAMPLE_RATE = 24000

VOZ_DEFAULT = "ef_dora"
VELOCIDAD_DEFAULT = 1.0

hablando_lock = threading.Lock()


# ==========================================
# CARGA GLOBAL DE KOKORO ONNX
# ==========================================

try:
    motor_kokoro = Kokoro(
        KOKORO_MODEL_PATH,
        KOKORO_VOICES_PATH
    )
except Exception as e:
    print("[!] Error al cargar Kokoro ONNX.")
    print("Verifica que existan estos archivos:")
    print(f" - {KOKORO_MODEL_PATH}")
    print(f" - {KOKORO_VOICES_PATH}")
    print(f"Detalle: {e}")
    raise SystemExit


# ==========================================
# LIMPIEZA Y HUMANIZACIÓN
# ==========================================

def limpiar_texto(texto: str) -> str:
    """
    Limpia etiquetas, markdown y contenido que Sarah no debe decir en voz alta.
    """

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

    texto = re.sub(r"^\s*[-•]\s*", "", texto, flags=re.MULTILINE)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def humanizar_fonetica(texto: str) -> str:
    """
    Ajusta muletillas para que suenen más naturales.
    """

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
        texto = re.sub(
            patron,
            nuevo,
            texto,
            flags=re.IGNORECASE
        )

    return texto


def separar_frases(texto: str) -> List[str]:
    """
    Divide el texto en frases pequeñas para insertar pausas humanas.
    """

    frases = re.split(r"(?<=[.!?,;:…])\s+", texto)
    frases_limpias = []

    for frase in frases:
        frase = frase.strip()

        if not frase:
            continue

        if len(frase) > 220:
            subfrases = re.split(r"(?<=,)\s+", frase)
            frases_limpias.extend([s.strip() for s in subfrases if s.strip()])
        else:
            frases_limpias.append(frase)

    return frases_limpias


def pausa_humana(frase: str):
    """
    Pausas según intención de la frase.
    """

    frase = frase.strip()

    if frase.endswith("...") or frase.endswith("…"):
        time.sleep(0.65)

    elif frase.endswith("?"):
        time.sleep(0.45)

    elif frase.endswith("!"):
        time.sleep(0.32)

    elif frase.endswith("."):
        time.sleep(0.28)

    elif frase.endswith(","):
        time.sleep(0.12)

    elif frase.endswith(";") or frase.endswith(":"):
        time.sleep(0.18)

    else:
        time.sleep(0.15)


def velocidad_por_modo(modo: str) -> float:
    """
    Ajusta velocidad según el modo de Sarah.
    """

    modo = (modo or "normal").lower().strip()

    if modo == "soporte":
        return 0.96

    if modo == "maestra":
        return 0.94

    if modo == "compañera":
        return 1.0

    if modo == "introspectiva":
        return 0.92

    if modo == "alerta":
        return 0.95

    return VELOCIDAD_DEFAULT


def voz_por_modo(modo: str) -> str:
    """
    Por ahora conserva una voz estable para mantener identidad.
    """

    return VOZ_DEFAULT


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

def hablar(
    texto: str,
    voz: str | None = None,
    velocidad: float | None = None,
    modo: str = "normal"
):
    """
    Genera y reproduce voz con Kokoro ONNX y pausas humanas.
    """

    texto = limpiar_texto(texto)
    texto = humanizar_fonetica(texto)

    if not texto:
        return

    if voz is None:
        voz = voz_por_modo(modo)

    if velocidad is None:
        velocidad = velocidad_por_modo(modo)

    with hablando_lock:
        print(f"\n[{NOMBRE_IA}] {texto}")

        frases = separar_frases(texto)

        for frase in frases:
            try:
                muestras, sample_rate = motor_kokoro.create(
                    frase,
                    voice=voz,
                    speed=velocidad,
                    lang="es"
                )

                audio = np.asarray(muestras, dtype=np.float32)

                sd.play(audio, sample_rate)
                sd.wait()

                pausa_humana(frase)

            except Exception as e:
                print("[!] Error al generar voz en frase:")
                print(frase)
                print(f"Detalle: {e}")


# ==========================================
# PRUEBA DIRECTA
# ==========================================

if __name__ == "__main__":
    hablar(
        "Mmm... estoy lista, Rafael. Podemos revisar el código, separar módulos, o pensar en cómo debería evolucionar Sarah.",
        modo="compañera"
    )

    hablar(
        "Alto. Aquí hay un problema: estás mezclando demasiadas responsabilidades en un solo archivo.",
        modo="soporte"
    )

    hablar(
        "Pregunta rápida: si Sarah tuviera que aprender contigo hoy, ¿qué debería practicar primero?",
        modo="maestra"
    )