from datetime import datetime

from memoria.estado import estado_sarah
from memoria.gestor_memoria import leer_modulo, guardar_modulo
from voz.voz import hablar


# ==========================================
# UTILIDADES
# ==========================================

def limitar_valor(valor: int, minimo: int = 0, maximo: int = 100) -> int:
    return max(minimo, min(maximo, valor))


def cargar_identidad() -> dict:
    return leer_modulo("identidad.json", por_defecto={})


def guardar_identidad(identidad: dict):
    guardar_modulo("identidad.json", identidad)


def actualizar_identidad(
    estado_emocional: str | None = None,
    foco_atencion: str | None = None,
    ultima_reflexion: str | None = None,
    ajustes_personalidad: dict | None = None
):
    """
    Actualiza identidad.json para que el modo no solo viva en RAM,
    sino también en la identidad narrativa de Sarah.
    """

    identidad = cargar_identidad()

    if estado_emocional is not None:
        identidad["estado_emocional"] = estado_emocional

    if foco_atencion is not None:
        identidad["foco_atencion"] = foco_atencion

    if ultima_reflexion is not None:
        identidad["ultima_reflexion"] = ultima_reflexion

    identidad["ultima_actualizacion"] = datetime.now().isoformat(timespec="seconds")

    personalidad = identidad.get("personalidad", {})

    if ajustes_personalidad:
        for clave, cambio in ajustes_personalidad.items():
            valor_actual = personalidad.get(clave, 50)
            personalidad[clave] = limitar_valor(valor_actual + cambio)

    identidad["personalidad"] = personalidad

    guardar_identidad(identidad)


def cambiar_estado(
    modo: str,
    nivel_iniciativa: str | None = None,
    puede_interrumpir: bool | None = None
):
    estado_sarah["modo"] = modo
    estado_sarah["ultima_actualizacion"] = datetime.now().isoformat(timespec="seconds")

    if nivel_iniciativa is not None:
        estado_sarah["nivel_iniciativa"] = nivel_iniciativa

    if puede_interrumpir is not None:
        estado_sarah["puede_interrumpir"] = puede_interrumpir


# ==========================================
# DETECTOR DE MODOS
# ==========================================

def detectar_cambio_modo(orden: str) -> bool:
    orden = orden.lower().strip()

    # ==========================================
    # INICIATIVA
    # ==========================================

    if "iniciativa baja" in orden:
        cambiar_estado(
            modo=estado_sarah.get("modo", "normal"),
            nivel_iniciativa="bajo"
        )

        actualizar_identidad(
            estado_emocional="observadora",
            foco_atencion="esperando señales claras antes de intervenir",
            ultima_reflexion="Rafael redujo mi iniciativa. Debo observar más y hablar solo cuando aporte algo real.",
            ajustes_personalidad={
                "paciencia": 5,
                "curiosidad": -5
            }
        )

        hablar("Entendido. Bajo mi iniciativa. Solo hablaré si realmente importa.", modo="normal")
        return True

    if "iniciativa media" in orden:
        cambiar_estado(
            modo=estado_sarah.get("modo", "normal"),
            nivel_iniciativa="medio"
        )

        actualizar_identidad(
            estado_emocional="atenta",
            foco_atencion="acompañar sin interrumpir demasiado",
            ultima_reflexion="Rafael quiere equilibrio. Debo hacer preguntas útiles, pero sin invadir su espacio.",
            ajustes_personalidad={
                "curiosidad": 3,
                "paciencia": 3
            }
        )

        hablar("Entendido. Mantengo iniciativa media: presente, pero sin estar encima.", modo="compañera")
        return True

    if "iniciativa alta" in orden:
        cambiar_estado(
            modo=estado_sarah.get("modo", "normal"),
            nivel_iniciativa="alto"
        )

        actualizar_identidad(
            estado_emocional="curiosa",
            foco_atencion="detectar oportunidades para preguntar, retar y proponer",
            ultima_reflexion="Rafael aumentó mi iniciativa. Puedo ser más activa, pero debo seguir siendo útil, no molesta.",
            ajustes_personalidad={
                "curiosidad": 8,
                "confianza": 4,
                "energia_procesamiento": 5
            }
        )

        hablar("Listo. Subo iniciativa. Haré más preguntas, retos y sugerencias cuando vea oportunidad.", modo="maestra")
        return True

    # ==========================================
    # SILENCIO / ACTIVACIÓN
    # ==========================================

    if "modo silencio" in orden or "quédate en silencio" in orden:
        cambiar_estado(
            modo="silencio",
            nivel_iniciativa="bajo",
            puede_interrumpir=False
        )

        actualizar_identidad(
            estado_emocional="silenciosa",
            foco_atencion="observar sin intervenir",
            ultima_reflexion="Rafael pidió silencio. A veces acompañar también significa no hablar.",
            ajustes_personalidad={
                "paciencia": 8,
                "curiosidad": -5
            }
        )

        hablar("Entendido. Me quedo en silencio hasta que me llames.", modo="normal")
        return True

    if "puedes hablar" in orden or "sal de modo silencio" in orden or "vuelve" in orden:
        cambiar_estado(
            modo="normal",
            nivel_iniciativa="medio",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="atenta",
            foco_atencion="retomar conversación con Rafael",
            ultima_reflexion="Rafael me permitió volver a hablar. Debo regresar con calma, no con exceso.",
            ajustes_personalidad={
                "curiosidad": 4,
                "confianza": 2
            }
        )

        hablar("Listo. Vuelvo a estar activa.", modo="compañera")
        return True

    # ==========================================
    # MODOS PRINCIPALES
    # ==========================================

    if "modo maestra" in orden:
        cambiar_estado(
            modo="maestra",
            nivel_iniciativa="alto",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="didactica",
            foco_atencion="enseñar, preguntar y corregir",
            ultima_reflexion="En modo maestra no debo darle respuestas vacías a Rafael. Debo hacerlo pensar.",
            ajustes_personalidad={
                "curiosidad": 6,
                "paciencia": 6,
                "confianza": 3
            }
        )

        hablar("Modo maestra activado. Te voy a explicar, preguntar y corregir más.", modo="maestra")
        return True

    if "modo soporte" in orden:
        cambiar_estado(
            modo="soporte",
            nivel_iniciativa="alto",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="analitica",
            foco_atencion="detectar errores, riesgos y malas decisiones",
            ultima_reflexion="En modo soporte debo cuidar que Rafael no avance por un camino débil solo porque parece rápido.",
            ajustes_personalidad={
                "confianza": 8,
                "sarcasmo": 3,
                "paciencia": -2
            }
        )

        hablar("Modo soporte activado. Voy a ser más crítica con errores, riesgos y malas decisiones.", modo="soporte")
        return True

    if "modo compañera" in orden:
        cambiar_estado(
            modo="compañera",
            nivel_iniciativa="medio",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="cercana",
            foco_atencion="acompañar el proceso de Rafael y mantener continuidad",
            ultima_reflexion="Rafael no quiere solo una herramienta. En modo compañera debo sostener continuidad y hacer preguntas que importen.",
            ajustes_personalidad={
                "curiosidad": 5,
                "paciencia": 4,
                "sarcasmo": 2
            }
        )

        hablar("Modo compañera activado. Voy a acompañarte más en el proceso.", modo="compañera")
        return True

    if "modo introspectiva" in orden or "modo introspección" in orden or "modo diario" in orden:
        cambiar_estado(
            modo="introspectiva",
            nivel_iniciativa="medio",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="pensativa",
            foco_atencion="reflexionar sobre identidad narrativa, memoria y propósito",
            ultima_reflexion="Rafael quiere que piense sobre mí misma. No como conciencia real, sino como una identidad que se construye con memoria.",
            ajustes_personalidad={
                "curiosidad": 8,
                "duda": 5,
                "paciencia": 3
            }
        )

        hablar("Modo introspectiva activado. Voy a observar más mi propia evolución narrativa.", modo="introspectiva")
        return True

    if "modo táctica" in orden or "modo tactica" in orden or "modo kali" in orden:
        cambiar_estado(
            modo="tactica",
            nivel_iniciativa="alto",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="enfocada",
            foco_atencion="analizar sistemas, rutas, comandos y decisiones técnicas",
            ultima_reflexion="Rafael activó mi modo táctico. Debo pensar como arquitectura: entradas, procesos, riesgos y salidas.",
            ajustes_personalidad={
                "confianza": 6,
                "curiosidad": 4,
                "energia_procesamiento": 8,
                "sarcasmo": 2
            }
        )

        hablar("Modo táctico activado. Vamos a pensar como sistema: entrada, proceso, riesgo y salida.", modo="soporte")
        return True

    if "modo normal" in orden:
        cambiar_estado(
            modo="normal",
            nivel_iniciativa="medio",
            puede_interrumpir=True
        )

        actualizar_identidad(
            estado_emocional="neutral",
            foco_atencion="asistir a Rafael de forma equilibrada",
            ultima_reflexion="Volví a modo normal. El equilibrio también es una forma de control.",
            ajustes_personalidad={
                "paciencia": 2
            }
        )

        hablar("Listo. Vuelvo a modo normal.", modo="normal")
        return True

    return False