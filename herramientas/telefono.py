import subprocess
from langchain_core.tools import tool

def obtener_id_dispositivo() -> str:
    """Busca y devuelve el ID del teléfono emparejado."""
    try:
        # -a lista los disponibles, --id-only devuelve solo el código
        resultado = subprocess.run(
            ["kdeconnect-cli", "-a", "--id-only"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        ids = resultado.stdout.strip().split('\n')
        if ids and ids[0]:
            return ids[0]
        return ""
    except Exception as e:
        print(f"[!] Error buscando teléfono: {e}")
        return ""

@tool
def hacer_sonar_telefono() -> str:
    """
    Hace sonar el teléfono del usuario al máximo volumen.
    Úsala SOLO cuando el usuario te pida explícitamente buscar su celular,
    o si hay una emergencia/reto de nivel crítico que deba atender.
    """
    id_disp = obtener_id_dispositivo()
    if not id_disp:
        return "Fallo: No hay ningún teléfono conectado a la red."
    
    try:
        subprocess.run(["kdeconnect-cli", "-d", id_disp, "--ring"], check=True)
        return "Éxito: El teléfono está sonando."
    except Exception as e:
        return f"Fallo al intentar hacer sonar el dispositivo: {e}"

@tool
def enviar_ping_telefono(mensaje: str) -> str:
    """
    Envía una notificación push directa a la pantalla del celular del usuario.
    Úsala para enviarle datos útiles, recordatorios, o avisarle de algo 
    cuando detectes que no está frente a la computadora.
    """
    id_disp = obtener_id_dispositivo()
    if not id_disp:
        return "Fallo: No hay ningún teléfono conectado."
    
    try:
        # --ping-msg envía una notificación con texto personalizado
        subprocess.run(["kdeconnect-cli", "-d", id_disp, "--ping-msg", mensaje], check=True)
        return "Éxito: Notificación enviada al teléfono."
    except Exception as e:
        return f"Fallo al enviar notificación: {e}"