import os
import random
import threading
import unicodedata
import traceback
from datetime import datetime

from config import (
    PALABRA_ACTIVACION,
    COMANDO_APAGADO
)

from voz.voz import hablar
from microfono.escucha import escuchar, calibrar_microfono
from bucle_autonomo.autonomia import bucle_autonomo
from bucle_conversacion.procesador import procesar_orden


# ==========================================
# CONFIG MAIN
# ==========================================

DEBUG = True
INICIAR_AUTONOMIA = True

ACTIVADORES = [
    PALABRA_ACTIVACION,
    "sara",
    "sarah",
    "sera",
    "será",
    "zarah"
]

COMANDOS_APAGADO = [
    COMANDO_APAGADO,
    "apaga sistema",
    "apagar",
    "desconectate",
    "desconéctate",
    "terminar programa",
    "salir"
]


# ==========================================
# UTILIDADES
# ==========================================

def log(mensaje: str):
    if DEBUG:
        print(mensaje)


def normalizar(texto: str) -> str:
    """
    Convierte texto a minúsculas, quita acentos y limpia espacios.
    """
    if not texto:
        return ""

    texto = texto.lower().strip()

    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )

    texto = " ".join(texto.split())

    return texto


def safe_hablar(texto: str, **kwargs):
    """
    Evita que Sarah se caiga si falla la voz.
    """
    try:
        hablar(texto, **kwargs)
    except TypeError:
        # Por si tu hablar() no acepta modo/velocidad todavía
        try:
            hablar(texto)
        except Exception as e:
            print(f"[!] Error en voz: {e}")
    except Exception as e:
        print(f"[!] Error en voz: {e}")


def respuesta_activacion():
    safe_hablar(random.choice([
        "¿Dime?",
        "Te escucho.",
        "Aquí estoy.",
        "Dime, Rafael.",
        "Adelante.",
        "Estoy lista."
    ]))


def contiene_activacion(texto: str) -> bool:
    texto_norm = normalizar(texto)

    for activador in ACTIVADORES:
        activador_norm = normalizar(activador)
        if activador_norm and activador_norm in texto_norm:
            return True

    return False


def extraer_orden(texto: str) -> str:
    """
    Extrae lo que viene después de la palabra de activación.

    Ejemplo:
    "sara busca en internet qué día es hoy"
    devuelve:
    "busca en internet qué día es hoy"
    """

    texto_norm = normalizar(texto)

    mejor_pos = None
    mejor_activador = None

    for activador in ACTIVADORES:
        activador_norm = normalizar(activador)

        if not activador_norm:
            continue

        pos = texto_norm.find(activador_norm)

        if pos != -1:
            if mejor_pos is None or pos < mejor_pos:
                mejor_pos = pos
                mejor_activador = activador_norm

    if mejor_pos is None or mejor_activador is None:
        return ""

    inicio_orden = mejor_pos + len(mejor_activador)
    orden = texto_norm[inicio_orden:].strip()

    # Limpieza de conectores comunes
    for basura in ["oye", "por favor", ",", "."]:
        orden = orden.replace(basura, "").strip()

    return orden


def es_comando_apagado(texto: str) -> bool:
    texto_norm = normalizar(texto)

    for comando in COMANDOS_APAGADO:
        if normalizar(comando) in texto_norm:
            return True

    return False


def leer_comando_voz(timeout=None, phrase_time_limit=6) -> str:
    """
    Wrapper para escuchar con manejo de errores.
    """
    try:
        return escuchar(
            timeout=timeout,
            phrase_time_limit=phrase_time_limit
        )
    except Exception as e:
        print(f"[!] Error escuchando: {e}")
        return ""


def modo_texto():
    """
    Fallback por si el micrófono falla.
    Escribes órdenes manualmente en terminal.
    """
    safe_hablar("Activo modo texto. Escribe tus órdenes en la terminal.")

    while True:
        try:
            orden = input("\nTú > ").strip()
        except KeyboardInterrupt:
            print("\n[Sarah] Interrumpido.")
            break

        if not orden:
            continue

        if es_comando_apagado(orden):
            safe_hablar("Entendido. Me quedo en espera. Hasta pronto.")
            break

        try:
            procesar_orden(orden)
        except Exception:
            print("[!] Error procesando orden en modo texto:")
            traceback.print_exc()


def iniciar_autonomia():
    if not INICIAR_AUTONOMIA:
        log("[Sarah] Autonomía desactivada desde main.py")
        return

    try:
        hilo = threading.Thread(
            target=bucle_autonomo,
            daemon=True
        )
        hilo.start()
        log("[Sarah] Bucle autónomo iniciado.")
    except Exception as e:
        print(f"[!] No pude iniciar autonomía: {e}")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    os.system("clear")

    print("Sarah está despertando...")

    try:
        calibrar_microfono()
    except Exception as e:
        print(f"[!] Falló calibración de micrófono: {e}")
        print("[!] Puedes usar modo texto si el micrófono no responde.")

    iniciar_autonomia()

    safe_hablar("Sistemas listos. Estoy contigo, Rafa. ¿En qué vamos a trabajar hoy?")

    print("\n[INFO] Di 'Sara' o 'Sarah' para activarme.")
    print("[INFO] Escribe 'texto' y presiona Enter si quieres modo texto.")
    print("[INFO] Ctrl + C para salir.\n")

    while True:
        try:
            comando = leer_comando_voz(timeout=None, phrase_time_limit=6)

            if not comando:
                continue

            print(f"\n[Escuchado] {comando}")

            comando_norm = normalizar(comando)

            # Fallback manual si dices o escribes "texto"
            if comando_norm in ["texto", "modo texto", "terminal"]:
                modo_texto()
                continue

            if es_comando_apagado(comando):
                safe_hablar("Entendido. Me quedo en espera. Hasta pronto.")
                break

            if not contiene_activacion(comando):
                log("[DEBUG] No detecté palabra de activación.")
                continue

            orden_directa = extraer_orden(comando)

            if not orden_directa:
                respuesta_activacion()
                orden_directa = leer_comando_voz(
                    timeout=10,
                    phrase_time_limit=15
                )

            if orden_directa:
                print(f"\n[Tú] {orden_directa}")

                try:
                    procesar_orden(orden_directa)
                except Exception:
                    print("[!] Error procesando orden:")
                    traceback.print_exc()
                    safe_hablar("Alto. Tuve un error procesando la orden. Revisa la terminal.")
            else:
                safe_hablar("No alcancé a escucharte bien.")

        except KeyboardInterrupt:
            print("\n[Sarah] Interrupción manual.")
            safe_hablar("Me detengo. Hasta pronto.")
            break

        except Exception:
            print("[!] Error inesperado en main:")
            traceback.print_exc()
            safe_hablar("Tuve un error inesperado en el bucle principal.")