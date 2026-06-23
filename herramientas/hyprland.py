import subprocess
from langchain_core.tools import tool

def ejecutar_hyprctl(argumentos: list) -> str:
    """Función base para comunicarse con el socket de Hyprland."""
    comando_base = ["hyprctl", "dispatch"] + argumentos
    try:
        resultado = subprocess.run(comando_base, capture_output=True, text=True, check=True)
        return "Ejecución exitosa."
    except subprocess.CalledProcessError as e:
        return f"Falló la ejecución en Hyprland: {e.stderr}"

@tool
def abrir_aplicacion(nombre_app: str) -> str:
    """
    Abre una aplicación gráfica en la pantalla actual. 
    Ejemplos válidos: 'kitty', 'firefox', 'code'.
    Úsala cuando propongas un reto técnico o necesites mostrarle código al usuario.
    """
    return ejecutar_hyprctl(["exec", nombre_app])

@tool
def cambiar_workspace(numero_workspace: int) -> str:
    """
    Mueve la vista de la pantalla a otro espacio de trabajo (1 al 10).
    Útil para organizar el entorno si la pantalla actual está muy llena.
    """
    return ejecutar_hyprctl(["workspace", str(numero_workspace)])

@tool
def notificacion_silenciosa(mensaje: str) -> str:
    """
    Envía una notificación visual a la pantalla (estilo elegante y oscuro).
    Úsala para avisos discretos cuando el usuario esté escuchando música
    o concentrado, en lugar de interrumpir con la voz.
    """
    try:
        # Usamos notify-send. Si el demonio (como dunst) está configurado en negro/estilo kali,
        # esto respetará la estética del entorno.
        subprocess.run([
            "notify-send",
            "-a", "Sarah (IA)",
            "-u", "normal",
            "Mensaje del Sistema",
            mensaje
        ], check=True)
        return "Notificación entregada con éxito."
    except Exception as e:
        return f"No se pudo enviar la notificación: {e}"