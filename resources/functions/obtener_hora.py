from datetime import datetime

def obtener_hora() -> str:
    """Obtiene la hora actual del sistema"""
    try:
        ahora = datetime.now()
        return f"Son las {ahora.strftime('%H:%M')}"
    except Exception as e:
        return f"Error al obtener la hora: {e}" 