import logging
from typing import Optional, Callable
import wave
import threading
from pathlib import Path
from datetime import datetime
import pyaudio
import numpy as np
from google.cloud import speech
from google.cloud import texttospeech
import os
import audioop
from .speech.web_stt import WebSTTService
from .speech.deepgram_tts import DeepgramTTSService
import time
from .speech.simple_stt import SimpleSTTService
from .speech.simple_tts import SimpleTTSService
from .speech.elevenlabs_tts import ElevenLabsTTSService
from .function_manager import FunctionManager

logger = logging.getLogger('lux')

class VoiceManager:
    def __init__(self, command_handler=None, ai_manager=None, task_service=None, 
                 media_player=None, reminder_service=None, file_service=None):
        """
        Inicializa el gestor de voz
        Args:
            command_handler: Manejador de comandos
            ai_manager: Gestor de IA
            task_service: Servicio de tareas
            media_player: Reproductor de música
            reminder_service: Servicio de recordatorios
            file_service: Servicio de archivos
        """
        # Servicios TTS disponibles
        self.tts_services = {
            'simple': SimpleTTSService(),
            'deepgram': DeepgramTTSService(),
            'elevenlabs': ElevenLabsTTSService()
        }
        self.current_tts = 'simple'
        
        # Servicios STT disponibles
        self.stt_services = {
            'simple': SimpleSTTService(language="es-ES"),
            'web': WebSTTService(language="es-ES")
        }
        self.current_stt = 'simple'
        
        self.is_listening = False
        self.callback = self._on_voice_command
        
        # Dependencias
        self.command_handler = command_handler
        self.ai_manager = ai_manager
        
        # Inicializar FunctionManager con servicios
        self.function_manager = FunctionManager(
            task_service=task_service,
            media_player=media_player,
            reminder_service=reminder_service,
            file_service=file_service
        )
        
        logger.info("VoiceManager inicializado")
    
    def set_tts_service(self, service_name: str):
        """Cambia el servicio TTS activo"""
        if service_name in self.tts_services:
            logger.info(f"Cambiando servicio TTS de {self.current_tts} a {service_name}")
            self.current_tts = service_name
            logger.info(f"Servicio TTS cambiado a: {service_name}")
            # Verificar que el servicio está disponible
            try:
                service = self.tts_services[service_name]
                service.speak("Servicio de voz cambiado correctamente")
            except Exception as e:
                logger.error(f"Error al probar nuevo servicio TTS: {e}")
    
    def set_stt_service(self, service_name: str):
        """Cambia el servicio STT activo"""
        if service_name in self.stt_services:
            was_listening = self.is_listening
            if was_listening:
                self.stop_listening()
            
            self.current_stt = service_name
            logger.info(f"Servicio STT cambiado a: {service_name}")
            
            if was_listening:
                self.start_listening()
    
    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """Inicia la escucha de audio"""
        if callback:
            self.callback = callback
        self.stt_services[self.current_stt].start_listening(self.callback)
        self.is_listening = True
        logger.info("Iniciada escucha de voz")
    
    def stop_listening(self):
        """Detiene la escucha"""
        self.stt_services[self.current_stt].stop_listening()
        self.is_listening = False
    
    def speak(self, text: str):
        """Reproduce texto directamente"""
        service = self.tts_services[self.current_tts]
        service.speak(text)
    
    def text_to_speech(self, text: str) -> Optional[str]:
        """Convierte texto a voz"""
        service = self.tts_services[self.current_tts]
        return service.synthesize(text)
    
    def cleanup(self):
        """Limpia recursos"""
        self.stop_listening()

    def _on_voice_command(self, text: str) -> str:
        """
        Maneja comandos de voz y retorna la respuesta
        Returns:
            str: Respuesta para TTS
        """
        try:
            logger.info(f"Procesando comando de voz: '{text}'")
            
            # Verificar si es una solicitud de función
            function_request = self.ai_manager.verify_function_request(text)
            logger.debug(f"Resultado de verificación de función: {function_request}")
            
            if function_request["type"] == "YES":
                # Ejecutar función existente
                logger.info(f"Ejecutando función: {function_request['function_name']}")
                result = self.function_manager.execute_function(
                    function_request['function_name'],
                    function_request['extra_info']
                )
                if result:
                    self.speak(result)
                    return result
                return "Hubo un error al ejecutar la función"
                
            elif function_request["type"] == "NEW":
                # Solicitud de nueva función
                logger.info(f"Solicitud de nueva función: {function_request['function_name']}")
                
                # Crear nueva función
                result = self.ai_manager.create_new_function(
                    function_request['function_name'],
                    function_request['description']
                )
                
                if result["success"]:
                    # Ejecutar la función recién creada
                    response = self.function_manager.execute_function(result["function"])
                    if response:
                        return f"He creado y ejecutado la función. {response}"
                    return "He creado la función pero hubo un error al ejecutarla."
                else:
                    return f"Lo siento, no pude crear la función: {result['error']}"
            
            # Si no es comando, procesar como chat
            logger.debug("No es comando, procesando como chat...")
            chat_response = self.ai_manager.chat(text)
            
            if chat_response:
                logger.info(f"Chat procesado. Respuesta: '{chat_response}'")
                try:
                    logger.debug(f"Iniciando TTS para respuesta de chat usando servicio: {self.current_tts}")
                    self.speak(chat_response)
                    logger.info("TTS completado exitosamente")
                except Exception as e:
                    logger.error(f"Error en TTS para chat: {e}", exc_info=True)
                return chat_response
            
            logger.warning("No se pudo procesar ni como comando ni como chat")
            return "No pude entender el comando."
            
        except Exception as e:
            logger.error(f"Error procesando comando de voz: {e}", exc_info=True)
            return "Lo siento, ocurrió un error al procesar tu comando."

    def set_command_handler(self, command_handler):
        """Actualiza el manejador de comandos"""
        self.command_handler = command_handler
        logger.debug("CommandHandler actualizado")
    
    def set_ai_manager(self, ai_manager):
        """Actualiza el gestor de IA"""
        self.ai_manager = ai_manager
        logger.debug("AIManager actualizado")
