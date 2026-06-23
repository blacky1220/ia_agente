import os
import json
import subprocess
from datetime import datetime

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from memoria.gestor_memoria import agregar_recuerdo

@tool
def saber_que_suena() -> str:
    """
    Útil para saber qué canción, artista o video está escuchando el usuario en este momento.
    Úsala cuando el usuario pregunte "¿qué estoy escuchando?", "¿qué canción es esta?" o "¿quién canta esto?".
    """
    try:
        # El truco: le decimos que priorice 'spotify', y si no está, busque en '%any' (cualquier otro)
        resultado = subprocess.check_output(
            ["playerctl", "--player=spotify,%any", "metadata", "--format", "{{ artist }} - {{ title }}"], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip()
        
        if resultado:
            return f"Actualmente está sonando: {resultado}"
        return "No hay ninguna canción reproduciéndose en este momento."
    except subprocess.CalledProcessError:
        return "No pude detectar ningún reproductor multimedia activo."

@tool
def controlar_reproductor(accion: str) -> str:
    """
    Útil para controlar Spotify o el reproductor del sistema. 
    Las acciones permitidas son: 'play-pause' (para pausar o reanudar), 'next' (siguiente canción), 'previous' (canción anterior).
    """
    acciones_validas = ["play-pause", "next", "previous"]
    if accion not in acciones_validas:
        return f"Acción inválida. Usa una de estas: {acciones_validas}"
    
    try:
        subprocess.run(["playerctl", "--player=spotify,%any", accion], check=True, stderr=subprocess.DEVNULL)
        return f"Comando '{accion}' ejecutado con éxito en el reproductor."
    except subprocess.CalledProcessError:
        return "Hubo un error al intentar controlar el reproductor. Puede que esté cerrado."

@tool
def obtener_fecha_actual() -> str:
    """Obtiene la fecha y hora actual del sistema local."""
    dias = [
        "lunes", "martes", "miércoles", "jueves",
        "viernes", "sábado", "domingo"
    ]

    meses = [
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre"
    ]

    ahora = datetime.now()

    dia_semana = dias[ahora.weekday()]
    mes = meses[ahora.month - 1]

    return f"Hoy es {dia_semana} {ahora.day} de {mes} de {ahora.year}. Son las {ahora.strftime('%H:%M')}."

@tool
def web_search(query: str) -> str:
    """Search the internet for current information, recent facts, dates, news or updated data."""
    buscador = DuckDuckGoSearchRun()
    print(f"      > Sarah busca en internet: {query}")
    return buscador.invoke(query)

@tool
def guardar_recuerdo(tipo: str, contenido: str) -> str:
    """
    Guarda preferencias, proyectos, notas, aprendizajes, correcciones,
    objetivos, reflexiones o preguntas pendientes.
    """
    categoria = agregar_recuerdo(tipo, contenido)
    return f"He guardado esto en {categoria}."

@tool
def obtener_info_sistema() -> str:
    """Obtiene información del sistema operativo Linux."""
    return subprocess.check_output(["uname", "-a"], text=True)

@tool
def listar_archivos(ruta: str = ".") -> str:
    """Lista archivos de una ruta."""
    return subprocess.check_output(["ls", "-la", ruta], text=True)

# Dentro de herramientas/tools.py

# Importas las herramientas de tu nuevo archivo
from herramientas.telefono import hacer_sonar_telefono, enviar_ping_telefono

# Y las agregas a la lista final que lee LangChain
herramientas_sarah = [
    # ... tus otras herramientas
    hacer_sonar_telefono,
    enviar_ping_telefono
]

@tool
def escribir_en_diario(reflexion: str) -> str:
    """
    ¡REGLA ESTRICTA!: ESTÁ PROHIBIDO usar esta herramienta para saludos básicos ("hola", "cómo estás", "¿qué haces?").
    NO la uses para interacciones cotidianas.
    Úsala ÚNICAMENTE cuando la conversación trate temas verdaderamente profundos, existenciales o filosóficos.
    """
    archivo_diario = "diario_sarah.json"
    data = []
    
    if os.path.exists(archivo_diario):
        try:
            with open(archivo_diario, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
            
    data.append({
        "reflexion_interna": reflexion,
        "fecha": datetime.now().isoformat(timespec="seconds")
    })
    
    with open(archivo_diario, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    return "Pensamiento guardado en el diario privado."

herramientas = [
    web_search,
    guardar_recuerdo,
    obtener_fecha_actual,
    obtener_info_sistema,
    listar_archivos,         # <--- Coma agregada
    escribir_en_diario,      # <--- Coma agregada
    saber_que_suena,         
    controlar_reproductor    
]

tools_by_name = {t.name: t for t in herramientas}