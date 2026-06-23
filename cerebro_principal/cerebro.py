import threading

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from herramientas.tools import herramientas
from cerebro_principal.prompts import construir_system_prompt


historial_lock = threading.Lock()


llm = ChatGroq(
    model_name="llama-3.1-8b-instant", 
    temperature=0.7
)

llm_agente = llm.bind_tools(herramientas)


historial_mensajes = [
    SystemMessage(content=construir_system_prompt())
]


def refrescar_prompt_sistema():
    global historial_mensajes
    
    # Obtenemos el nuevo prompt (esto lee los JSONs frescos del disco)
    nuevo_prompt_texto = construir_system_prompt()
    
    with historial_lock:
        # Actualizamos solo la parte del sistema
        historial_mensajes[0] = SystemMessage(content=nuevo_prompt_texto)
        print("[Sistema] Memoria recargada en historial de chat.")