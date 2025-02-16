import pyttsx3
import logging
from typing import Optional
from pathlib import Path
import os

logger = logging.getLogger('lux')

class SimpleTTSService:
    def __init__(self):
        self.engine = pyttsx3.init()
        
        # Configurar voz en español si está disponible
        voices = self.engine.getProperty('voices')
        spanish_voice = next((v for v in voices if 'spanish' in v.name.lower()), None)
        if spanish_voice:
            self.engine.setProperty('voice', spanish_voice.id)
        
        # Ajustar velocidad y volumen
        self.engine.setProperty('rate', 150)    # Velocidad más natural
        self.engine.setProperty('volume', 1.0)  # Volumen al máximo
        
        # Configurar driver de audio
        try:
            self.engine.setProperty('driver', 'sapi5')  # Windows
        except:
            try:
                self.engine.setProperty('driver', 'espeak')  # Linux
            except:
                pass  # Usar driver por defecto
        
        logger.info("SimpleTTS inicializado")
    
    def synthesize(self, text: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Sintetiza texto a voz
        Args:
            text: Texto a sintetizar
            output_dir: Directorio para guardar el audio
        Returns:
            str: Ruta del archivo de audio o None si hay error
        """
        try:
            # Crear directorio si no existe
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("resources/audio/tts")
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo
            filename = output_path / f"speech_{os.urandom(4).hex()}.mp3"
            
            # Guardar audio
            self.engine.save_to_file(text, str(filename))
            self.engine.runAndWait()
            
            logger.info(f"Audio generado: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            return None
    
    def speak(self, text: str):
        """Reproduce el texto directamente"""
        try:
            if not text:
                logger.warning("Texto vacío, no hay nada que reproducir")
                return
                
            logger.debug(f"Iniciando reproducción TTS: '{text}'")
            
            # Verificar estado del motor
            logger.debug("Verificando estado del motor TTS...")
            voices = self.engine.getProperty('voices')
            current_voice = self.engine.getProperty('voice')
            logger.debug(f"Motor TTS: {len(voices)} voces disponibles, usando voz ID: {current_voice}")
            
            # Intentar reproducir
            self.engine.say(text)
            logger.debug("Texto enviado al motor, esperando reproducción...")
            self.engine.runAndWait()
            logger.debug("Reproducción completada")
            
        except Exception as e:
            logger.error(f"Error al reproducir voz: {e}", exc_info=True)
            logger.info("Intentando reinicializar el motor TTS...")
            try:
                self.engine = pyttsx3.init()
                logger.debug("Motor TTS reinicializado, reintentando reproducción...")
                self.engine.say(text)
                self.engine.runAndWait()
                logger.info("Reproducción exitosa después de reiniciar")
            except Exception as e2:
                logger.error(f"Error fatal al reintentar reproducción: {e2}", exc_info=True) 