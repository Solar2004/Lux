import os
import subprocess
import webbrowser
from typing import Dict

def abrir_aplicacion(nombre: str) -> str:
    """
    Abre una aplicación o sitio web
    Args:
        nombre: Nombre de la aplicación o sitio web
    Returns:
        str: Mensaje de resultado
    """
    # Normalizar el nombre
    nombre = nombre.lower().replace("_", " ").strip()
    
    # Diccionario de aplicaciones comunes y sus comandos
    apps: Dict[str, str] = {
        "notepad": "notepad.exe",
        "bloc de notas": "notepad.exe",
        "calculadora": "calc.exe",
        "paint": "mspaint.exe",
        "explorador": "explorer.exe",
        "cmd": "cmd.exe",
        "terminal": "cmd.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
    }
    
    # Diccionario de sitios web comunes
    websites: Dict[str, str] = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
    }
    
    try:
        # Verificar si es un sitio web
        if nombre in websites:
            webbrowser.open(websites[nombre])
            return f"Abriendo {nombre} en el navegador"
        
        # Verificar si es una aplicación conocida
        if nombre in apps:
            try:
                subprocess.Popen(apps[nombre])
                return f"Abriendo {nombre}"
            except Exception as e:
                return f"Error al abrir {nombre}: {e}"
        
        # Si no está en las listas, intentar como comando directo
        try:
            subprocess.Popen(nombre)
            return f"Intentando abrir {nombre}"
        except Exception as e:
            return f"No pude encontrar la aplicación: {nombre}"
            
    except Exception as e:
        return f"Error al abrir {nombre}: {e}" 