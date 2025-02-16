import requests
import base64
from pathlib import Path
import os
import logging
from typing import Optional
import pygame

logger = logging.getLogger('lux')

class DeepgramTTSService:
    """Servicio de síntesis de voz usando Deepgram"""
    
    def __init__(self):
        self.headers = {
            "authority": "deepgram.com",
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://deepgram.com",
            "referer": "https://deepgram.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        pygame.mixer.init()
        self.voice = "aura-orion-en"  # Voz por defecto
    
    def synthesize(self, text: str, model: str = "aura-orion-en", 
                  output_dir: Optional[str] = None) -> Optional[str]:
        """
        Sintetiza texto a voz
        Args:
            text: Texto a sintetizar
            model: Modelo de voz a usar
            output_dir: Directorio para guardar el audio
        Returns:
            str: Ruta del archivo de audio o None si hay error
        """
        try:
            url = "https://deepgram.com/api/ttsAudioGeneration"
            payload = {"text": text, "model": model}
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Crear directorio si no existe
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("resources/audio/tts")
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            filename = output_path / f"speech_{os.urandom(4).hex()}.mp3"
            with open(filename, 'wb') as audio_file:
                audio_file.write(base64.b64decode(response.json()['data']))
            
            logger.info(f"Audio generado: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            return None
    
    def play_audio(self, file_path: str):
        """Reproduce el archivo de audio"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            logger.error(f"Error al reproducir audio: {e}")
        finally:
            try:
                os.remove(file_path)
            except:
                pass
    
    def speak(self, text: str):
        """Reproduce el texto directamente"""
        try:
            audio_file = self.synthesize(text)
            if audio_file:
                self.play_audio(audio_file)
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}") 