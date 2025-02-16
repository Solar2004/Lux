import os
import requests
import logging
import pygame
from typing import Optional, Dict
from pathlib import Path
from ...services.proxy_service import ProxyService

logger = logging.getLogger('lux')

class ElevenLabsTTSService:
    def __init__(self):
        self.model_id = "eleven_multilingual_v2"
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.headers = {
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Content-Type': 'application/json',
            'Dnt': '1',
            'Origin': 'https://elevenlabs.io',
            'Priority': 'u=1, i',
            'Referer': 'https://elevenlabs.io/',
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        
        # Lista completa de voces
        self.voice_ids = {
            "charlottee": "XB0fDUnXU5powFXDhCwa",
            "daniel": "onwK4e9ZLuTAKqWW03F9",
            "callum": "N2lVS1w4EtoT3dr4eOWO",
            "charlie": "IKne3meq5aSn9XLyUdCD",
            "clyde": "2EiwWnXFnvU5JabPnv8n",
            "dave": "CYw3kZ02Hs0563khs1Fj",
            "emily": "LcfcDJNUP1GQjkzn1xUU",
            "ethan": "g5CIjZEefAph4nQFvHAz",
            "fin": "D38z5RcWu1voky8WS1ja",
            "freya": "jsCqWAovK2LkecY7zXl4",
            "gigi": "jBpfuIE2acCO8z3wKNLl",
            "giovanni": "zcAOhNBS3c14rBihAFp1",
            "glinda": "z9fAnlkpzviPz146aGWa",
            "grace": "oWAxZDx7w5VEj9dCyTzz",
            "harry": "SOYHLrjzK2X1ezoPC6cr",
            "james": "ZQe5CZNOzWyzPSCn5a3c",
            "jeremy": "bVMeCyTHy58xNoL34h3p"
        }
        
        self.session = requests.Session()
        self.current_voice = "daniel"  # Voz por defecto
        pygame.mixer.init()
        self.proxy_service = ProxyService()
        logger.info("ElevenLabs TTS inicializado")
    
    def synthesize(self, text: str, output_dir: Optional[str] = None) -> Optional[str]:
        try:
            voice_id = self.voice_ids[self.current_voice]
            url = f"{self.base_url}/{voice_id}/stream"
            
            payload = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            # Obtener proxy
            proxy = self.proxy_service.get_proxy()
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
            
            logger.debug(f"Solicitando síntesis para voz: {self.current_voice} usando proxy: {proxy}")
            response = self.session.post(
                url, 
                headers=self.headers, 
                json=payload,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                if output_dir:
                    output_path = Path(output_dir)
                else:
                    output_path = Path("resources/audio/tts")
                output_path.mkdir(parents=True, exist_ok=True)
                
                filename = output_path / f"speech_{os.urandom(4).hex()}.mp3"
                with open(filename, "wb") as file:
                    file.write(response.content)
                
                logger.info(f"Audio generado: {filename}")
                return str(filename)
            else:
                logger.error(f"Error en respuesta ElevenLabs: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            return None
    
    def speak(self, text: str):
        """Reproduce el texto directamente"""
        try:
            logger.debug(f"Iniciando síntesis para texto: '{text}'")
            audio_file = self.synthesize(text)
            if audio_file:
                logger.debug(f"Reproduciendo archivo: {audio_file}")
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                logger.debug("Reproducción completada")
                os.remove(audio_file)
            else:
                logger.error("No se pudo generar el audio")
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}", exc_info=True) 