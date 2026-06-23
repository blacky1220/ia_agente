from dotenv import load_dotenv

load_dotenv()

NOMBRE_IA = "Sarah"

ARCHIVO_MEMORIA = "memoria/memoria_sarah.json"
ARCHIVO_VOZ_TEMP = "respuesta_sarah.wav"

KOKORO_MODEL_PATH = "kokoro/kokoro-v1.0.onnx"
KOKORO_VOICES_PATH = "kokoro/voices-v1.0.bin"

PALABRA_ACTIVACION = "sara"
COMANDO_APAGADO = "apagar sistema"

MINUTOS_ENTRE_MENSAJES_AUTONOMOS = 20
SEGUNDOS_REFLEXION = 300