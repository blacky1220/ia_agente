import speech_recognition as sr

from microfono.alsa import noalsaerr


reconocedor = sr.Recognizer()
reconocedor.pause_threshold = 0.8
reconocedor.energy_threshold = 300
reconocedor.dynamic_energy_threshold = True


def calibrar_microfono():
    with noalsaerr():
        try:
            with sr.Microphone() as origen:
                print("[Sarah] Calibrando micrófono...")
                reconocedor.adjust_for_ambient_noise(origen, duration=1)
        except Exception as e:
            print(f"[!] Error al calibrar micrófono: {e}")


def escuchar(ajustar_ruido=False, timeout=None, phrase_time_limit=8) -> str:
    with noalsaerr():
        try:
            with sr.Microphone() as origen:
                if ajustar_ruido:
                    reconocedor.adjust_for_ambient_noise(origen, duration=1)

                audio = reconocedor.listen(
                    origen,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            texto = reconocedor.recognize_google(audio, language="es-MX")
            return texto.lower().strip()

        except Exception:
            return ""