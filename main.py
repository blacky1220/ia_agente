import os
import random
import threading

from config import (
    PALABRA_ACTIVACION,
    COMANDO_APAGADO
)

from voz.voz import hablar
from microfono.escucha import escuchar, calibrar_microfono
from bucle_autonomo.autonomia import bucle_autonomo
from bucle_conversacion.procesador import procesar_orden


def respuesta_activacion():
    hablar(random.choice([
        "¿Dime?",
        "Te escucho.",
        "Aquí estoy.",
        "Dime, Rafael.",
        "Adelante."
    ]))


if __name__ == "__main__":
    os.system("clear")

    print("Sarah está despertando...")

    calibrar_microfono()

    hilo_autonomo = threading.Thread(
        target=bucle_autonomo,
        daemon=True
    )
    hilo_autonomo.start()

    hablar("Sistemas listos. Estoy contigo, Rafa. ¿En qué vamos a trabajar hoy?")

    while True:
        comando = escuchar(timeout=None, phrase_time_limit=5)

        if not comando:
            continue

        print(f"\n[Escuchado] {comando}")

        if COMANDO_APAGADO in comando:
            hablar("Entendido. Me quedo en espera. Hasta pronto.")
            break

        if PALABRA_ACTIVACION in comando:
            orden_directa = comando.split(PALABRA_ACTIVACION, 1)[-1].strip()

            if not orden_directa:
                respuesta_activacion()
                orden_directa = escuchar(timeout=8, phrase_time_limit=14)

            if orden_directa:
                print(f"\n[Tú] {orden_directa}")
                procesar_orden(orden_directa)
            else:
                hablar("No alcancé a escucharte bien.")