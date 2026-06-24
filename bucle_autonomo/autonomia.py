import json
import time
import random
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
import cerebro_principal.cerebro as cerebro

from config import (
    MINUTOS_ENTRE_MENSAJES_AUTONOMOS,
    SEGUNDOS_REFLEXION
)
from voz.voz import hablar
from memoria.estado import estado_sarah

# Importamos las nuevas funciones modulares
from memoria.gestor_memoria import leer_modulo, agregar_recuerdo, agregar_al_diario

from bucle_autonomo.mentora import evaluar_lanzar_reto

# Definimos el prompt de autonomía directamente aquí para evitar ImportErrors
PROMPT_REFLEXION_AUTONOMA = """
Eres el subconsciente lógico de Sarah. Tu tarea es decidir si debes hablar por iniciativa propia.
Analiza el estado del sistema, la memoria y los últimos mensajes de la conversación.
Responde ÚNICAMENTE con un JSON válido con esta estructura:
{
  "accion": "hablar" o "silencio",
  "mensaje": "Lo que Sarah dirá en voz alta (vacío si es silencio)",
  "guardar_en_memoria": "Alguna deducción interna para guardar (vacío si no hay nada nuevo)",
  "razon": "Por qué tomaste esta decisión"
}
"""

def puede_hablar_autonomamente() -> bool:
    if not estado_sarah.get("puede_interrumpir", True):
        return False

    ultimo = estado_sarah.get("ultimo_mensaje_autonomo")

    if not ultimo:
        return True

    try:
        ultima_fecha = datetime.fromisoformat(ultimo)
        minutos = (datetime.now() - ultima_fecha).total_seconds() / 60
        return minutos >= MINUTOS_ENTRE_MENSAJES_AUTONOMOS
    except Exception:
        return True



def bucle_autonomo():
    aburrimiento = 0
    while True:
        time.sleep(SEGUNDOS_REFLEXION)
        aburrimiento += 10 # Sube 10 puntos en cada ciclo de silencio
        
        # Primero revisa si quiere lanzar un reto técnico
        reto_lanzado = evaluar_lanzar_reto(aburrimiento)
        
        if reto_lanzado:
            aburrimiento = 0 # Se le quita el aburrimiento porque ya te puso a trabajar
        else:
            # Si no lanza reto, hace su reflexión normal
            reflexion_autonoma()


def reflexion_autonoma():
    if not puede_hablar_autonomamente():
        return

    nivel = estado_sarah.get("nivel_iniciativa", "alto")

    if nivel == "bajo":
        probabilidad_hablar = 0.15
    elif nivel == "alto":
        probabilidad_hablar = 0.75
    else:
        probabilidad_hablar = 0.4

    if random.random() > probabilidad_hablar:
        return

    # Extraemos los últimos mensajes
    with cerebro.historial_lock:
        ultimos = [
            str(m.content)
            for m in cerebro.historial_mensajes[-8:]
            if hasattr(m, "content")
        ]

    # Leemos la memoria bajo demanda en lugar de usar la variable global vieja
    memoria_resumen = {
        "proyectos": leer_modulo("proyectos.json"),
        "preferencias": leer_modulo("preferencias.json")
    }

    contexto = f"""
Estado:
{json.dumps(estado_sarah, ensure_ascii=False, indent=2)}

Memoria Contextual:
{json.dumps(memoria_resumen, ensure_ascii=False, indent=2)}

Últimos mensajes:
{json.dumps(ultimos, ensure_ascii=False, indent=2)}

Decide si Sarah debe decir algo ahora.
"""

    try:
        respuesta = cerebro.llm.invoke([
            SystemMessage(content=PROMPT_REFLEXION_AUTONOMA),
            HumanMessage(content=contexto)
        ])

        contenido = respuesta.content.strip()
        contenido = contenido.replace("```json", "").replace("```", "").strip()

        decision = json.loads(contenido)

        accion = decision.get("accion", "silencio")
        mensaje = decision.get("mensaje", "").strip()
        guardar = decision.get("guardar_en_memoria", "").strip()
        razon = decision.get("razon", "")

        print(f"\n[Reflexión autónoma] {accion}: {razon}")

        if guardar:
            # Usamos la nueva función para guardar la reflexión
            agregar_recuerdo("reflexion", guardar)
            cerebro.refrescar_prompt_sistema()

        if accion != "silencio" and mensaje:
            hablar(mensaje)
            estado_sarah["ultimo_mensaje_autonomo"] = datetime.now().isoformat(timespec="seconds")
            # Agregamos la iniciativa al diario del día
            agregar_al_diario(mensaje, rol="sarah_autonoma")
            cerebro.refrescar_prompt_sistema()

    except Exception as e:
        print(f"[!] Error en reflexión autónoma: {e}")
