import os
import json
from datetime import datetime

# Asumimos que tu config tiene una RUTA_MEMORIA="memoria"
# Si no, puedes dejarlo así:
DIRECTORIO_MEMORIA = "memoria"
DIRECTORIO_DIARIOS = os.path.join(DIRECTORIO_MEMORIA, "diarios")

# Nos aseguramos de que la estructura de carpetas exista desde el inicio
os.makedirs(DIRECTORIO_MEMORIA, exist_ok=True)
os.makedirs(DIRECTORIO_DIARIOS, exist_ok=True)

def normalizar_archivo(tipo: str) -> str:
    """Mapea el tipo de recuerdo al archivo JSON correspondiente."""
    tipo = tipo.lower().strip()
    mapa = {
        "preferencia": "preferencias.json",
        "preferencias": "preferencias.json",
        "proyecto": "proyectos.json",
        "proyectos": "proyectos.json",
        "nota": "notas.json",
        "notas": "notas.json",
        "aprendizaje": "aprendizajes.json",
        "aprendizajes": "aprendizajes.json",
        "correccion": "correcciones.json",
        "correcciones": "correcciones.json",
        "reflexion": "reflexiones.json",
        "reflexiones": "reflexiones.json",
        "objetivo": "objetivos.json",
        "objetivos": "objetivos.json",
        "pregunta": "preguntas_pendientes.json",
        "preguntas": "preguntas_pendientes.json"
    }
    return mapa.get(tipo, "notas.json")

def leer_modulo(nombre_archivo: str, por_defecto=None):
    """Lee un archivo JSON específico de la memoria."""
    if por_defecto is None:
        por_defecto = [] # La mayoría de tus módulos son listas

    ruta = os.path.join(DIRECTORIO_MEMORIA, nombre_archivo)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return por_defecto

def guardar_modulo(nombre_archivo: str, contenido):
    """Sobrescribe un archivo JSON específico con el nuevo contenido."""
    ruta = os.path.join(DIRECTORIO_MEMORIA, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=4)

def agregar_recuerdo(tipo: str, contenido: str) -> str:
    """Agrega un elemento al módulo específico sin cargar toda la memoria global."""
    nombre_archivo = normalizar_archivo(tipo)
    
    # 1. Cargamos solo el módulo que necesitamos
    datos_modulo = leer_modulo(nombre_archivo, por_defecto=[])
    
    # 2. Agregamos el nuevo recuerdo
    datos_modulo.append({
        "contenido": contenido,
        "fecha": datetime.now().isoformat(timespec="seconds")
    })
    
    # 3. Guardamos solo ese módulo
    guardar_modulo(nombre_archivo, datos_modulo)
    
    # Actualizamos un archivo global de "estado" para saber cuándo fue la última actividad
    estado_actual = leer_modulo("estado_actual.json", por_defecto={"usuario": "Rafael"})
    estado_actual["ultima_actualizacion"] = datetime.now().isoformat(timespec="seconds")
    guardar_modulo("estado_actual.json", estado_actual)

    return nombre_archivo.replace('.json', '')

def agregar_al_diario(mensaje: str, rol: str = "sarah"):
    """Guarda un registro conversacional o de evento en el diario del día actual."""
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    archivo_diario = os.path.join("diarios", f"{fecha_hoy}.json")
    
    # Leemos el diario de hoy (o creamos uno vacío si es el primer mensaje)
    diario_hoy = leer_modulo(archivo_diario, por_defecto=[])
    
    diario_hoy.append({
        "hora": datetime.now().strftime("%H:%M:%S"),
        "rol": rol,
        "mensaje": mensaje
    })
    
    guardar_modulo(archivo_diario, diario_hoy)