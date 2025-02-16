import speech_recognition as sr
import logging
from typing import Optional, Callable
import threading
import time

logger = logging.getLogger('lux')

class SimpleSTTService:
    def __init__(self, language: str = "es-ES"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.callback = None
        self.listen_thread = None
        
        # Ajustar para ambiente
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        logger.info("SimpleSTT inicializado")
    
    def start_listening(self, callback: Callable[[str], None]):
        """Inicia la escucha continua"""
        if self.is_listening:
            return
            
        self.callback = callback
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        logger.info("Iniciada escucha de audio")
    
    def _listen_loop(self):
        """Loop principal de escucha"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    logger.debug("Escuchando...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                try:
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    if text and self.callback:
                        logger.info(f"Texto reconocido: {text}")
                        self.callback(text)
                except sr.UnknownValueError:
                    logger.debug("No se pudo entender el audio")
                except sr.RequestError as e:
                    logger.error(f"Error en el servicio de reconocimiento: {e}")
                    
            except Exception as e:
                logger.error(f"Error en escucha: {e}")
                time.sleep(1)
    
    def stop_listening(self):
        """Detiene la escucha"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread = None 