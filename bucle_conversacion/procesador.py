import random
from datetime import datetime

from langchain_core.messages import HumanMessage, ToolMessage

import cerebro_principal.cerebro as cerebro

from memoria.estado import estado_sarah
from voz.voz import hablar
from herramientas.tools import tools_by_name
from bucle_conversacion.modos import detectar_cambio_modo


def recortar_historial(max_mensajes=35):
    with cerebro.historial_lock:
        if len(cerebro.historial_mensajes) <= max_mensajes:
            return

        system = cerebro.historial_mensajes[0]
        resto = cerebro.historial_mensajes[1:]

        cerebro.historial_mensajes = [system] + resto[-max_mensajes:]


def ejecutar_tool_call(llamada):
    nombre = llamada["name"]
    argumentos = llamada.get("args", {})
    tool_call_id = llamada.get("id", nombre)

    if nombre not in tools_by_name:
        return ToolMessage(
            content=f"No existe la herramienta {nombre}.",
            tool_call_id=tool_call_id
        )

    try:
        print(f"      > Ejecutando herramienta: {nombre}")
        resultado = tools_by_name[nombre].invoke(argumentos)

        if nombre == "guardar_recuerdo":
            cerebro.refrescar_prompt_sistema()

        return ToolMessage(
            content=str(resultado),
            tool_call_id=tool_call_id
        )

    except Exception as e:
        return ToolMessage(
            content=f"Error ejecutando {nombre}: {e}",
            tool_call_id=tool_call_id
        )


def procesar_orden(orden: str):
    estado_sarah["ultima_interaccion"] = datetime.now().isoformat(timespec="seconds")

    muletilla = random.choice(["A ver...", "Mmm...", "Déjame ver...", "Pensando..."])
    print(f"\n[Sarah murmura] {muletilla}")

    if detectar_cambio_modo(orden):
        cerebro.refrescar_prompt_sistema()
        return

    cerebro.refrescar_prompt_sistema()

    with cerebro.historial_lock:
        cerebro.historial_mensajes.append(HumanMessage(content=orden))

    ciclos = 0

    while ciclos < 5:
        ciclos += 1

        respuesta = cerebro.llm_agente.invoke(cerebro.historial_mensajes)

        with cerebro.historial_lock:
            cerebro.historial_mensajes.append(respuesta)

        if respuesta.tool_calls:
            for llamada in respuesta.tool_calls:
                tool_msg = ejecutar_tool_call(llamada)

                with cerebro.historial_lock:
                    cerebro.historial_mensajes.append(tool_msg)

            continue

        contenido = respuesta.content.strip()
        hablar(contenido)
        recortar_historial()
        return

    hablar("Alto. Me detuve porque entré en demasiados pasos internos. Divide la orden en algo más concreto.")
    recortar_historial()