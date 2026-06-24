import speech_recognition as sr

from microfono.alsa import noalsaerr


reconocedor = sr.Recognizer()

reconocedor.pause_threshold = 1.0
reconocedor.energy_threshold = 300
reconocedor.dynamic_energy_threshold = True


def listar_microfonos():
    print("\n[Micrófonos disponibles]")
    for i, nombre in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{i}: {nombre}")


def calibrar_microfono():
    with noalsaerr():
        try:
            listar_microfonos()

            with sr.Microphone() as origen:
                print("[Sarah] Calibrando micrófono...")
                reconocedor.adjust_for_ambient_noise(origen, duration=1.5)

                print(f"[Sarah] Energy threshold: {reconocedor.energy_threshold}")

        except Exception as e:
            print(f"[!] Error al calibrar micrófono: {e}")


def escuchar(ajustar_ruido=False, timeout=None, phrase_time_limit=8) -> str:
    with noalsaerr():
        try:
            with sr.Microphone() as origen:
                if ajustar_ruido:
                    print("[Sarah] Ajustando ruido ambiente...")
                    reconocedor.adjust_for_ambient_noise(origen, duration=1)

                print("[Sarah] Escuchando...")

                audio = reconocedor.listen(
                    origen,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            print("[Sarah] Procesando audio...")

            texto = reconocedor.recognize_google(audio, language="es-MX")
            texto = texto.lower().strip()

            print(f"[Sarah escuchó] {texto}")

            return texto

        except sr.WaitTimeoutError:
            print("[Sarah] No escuché nada dentro del tiempo límite.")
            return ""

        except sr.UnknownValueError:
            print("[Sarah] Escuché audio, pero no entendí palabras.")
            return ""

        except sr.RequestError as e:
            print(f"[!] Error con Google Speech Recognition: {e}")
            return ""

        except Exception as e:
            print(f"[!] Error general al escuchar: {e}")
            return ""