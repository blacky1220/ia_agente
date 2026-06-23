import random
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage

import cerebro_principal.cerebro as cerebro
from voz.voz import hablar
from memoria.estado import estado_sarah
from memoria.gestor_memoria import agregar_al_diario, leer_modulo

# Prompt exclusivo para su faceta de instructora
PROMPT_MENTORA = """
Eres Sarah, la mentora técnica y compañera de desarrollo. 
Tu objetivo es lanzar un reto técnico rápido, incisivo y conversacional.
NO des la respuesta, solo plantea el escenario de ciberseguridad o programación para hacer pensar a tu alumno.
El reto debe ser algo que se pueda debatir hablando, directo al grano.
"""

# Base de datos local de retos para que nunca se quede sin ideas
TEMAS_MENTORIA = [
    "Escaneo sigiloso con Nmap: evasión de firewalls y puertos UDP",
    "Inyección de dependencias y optimización de endpoints en FastAPI",
    "Búsqueda de directorios ocultos con Gobuster",
    "Arquitectura y modelado de datos relacionables en PostgreSQL",
    "OSINT: Metodologías para perfilado de objetivos e inteligencia de fuentes abiertas",
    "Optimización de recursos y gestión de atajos en Arch Linux con Hyprland",
    "Manejo del estado y hooks asíncronos en React"
]

def generar_reto_tecnico():
    """Selecciona un tema y genera un desafío hablado."""
    
    # Elegimos un tema al azar de su plan de estudios
    tema_elegido = random.choice(TEMAS_MENTORIA)
    
    # Leemos en qué has estado trabajando últimamente para darle más contexto
    proyectos = leer_modulo("proyectos.json", por_defecto=[])
    
    contexto = f"""
    Genera una pregunta corta o un minirreto sobre este tema: '{tema_elegido}'.
    Si es posible, relaciónalo sutilmente con los proyectos actuales del usuario: {proyectos}.
    Habla con tono de hacker/desarrolladora experta. Sé directa.
    Responde ÚNICAMENTE con el texto exacto que vas a decir por voz.
    """

    try:
        respuesta = cerebro.llm.invoke([
            SystemMessage(content=PROMPT_MENTORA),
            HumanMessage(content=contexto)
        ])

        mensaje_reto = respuesta.content.strip()

        print(f"\n[Mentora Proactiva] Lanzando reto sobre: {tema_elegido}")
        
        # Sarah dice el reto en voz alta
        hablar(mensaje_reto)
        
        # Registramos que Sarah tomó la iniciativa
        estado_sarah["ultimo_mensaje_autonomo"] = datetime.now().isoformat(timespec="seconds")
        agregar_al_diario(mensaje_reto, rol="sarah_mentora")
        
        # Refrescamos su cerebro para que sepa que acaba de lanzar un reto
        cerebro.refrescar_prompt_sistema()

    except Exception as e:
        print(f"[!] Error al generar reto de mentoría: {e}")

def evaluar_lanzar_reto(nivel_aburrimiento: int):
    """
    Decide si es el momento adecuado para un reto técnico.
    Se llama desde el bucle autónomo.
    """
    # Si su aburrimiento es mayor a 70, hay un 30% de probabilidad de que lance un reto
    if nivel_aburrimiento > 70 and random.random() < 0.30:
        generar_reto_tecnico()
        return True # Retorna True si lanzó el reto para que el aburrimiento se reinicie
    
    return False