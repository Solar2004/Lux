import logging
from typing import Optional, Callable
from pathlib import Path
import pygame
import threading
import time
from queue import Queue

logger = logging.getLogger('lux')

class MediaManager:
    def __init__(self):
        """Inicializa el gestor de medios"""
        pygame.mixer.init()
        self.current_sound: Optional[pygame.mixer.Sound] = None
        self.is_playing = False
        self.volume = 1.0
        self.audio_queue = Queue()
        self._play_thread = None
        self._should_stop = False
        self._on_complete_callback = None
    
    def play_audio(
        self,
        file_path: str,
        volume: float = 1.0,
        on_complete: Optional[Callable] = None
    ) -> bool:
        """
        Reproduce un archivo de audio.
        
        Args:
            file_path: Ruta al archivo de audio
            volume: Volumen de reproducción (0.0 a 1.0)
            on_complete: Callback a ejecutar al terminar
            
        Returns:
            bool: True si se inició la reproducción
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"Archivo de audio no encontrado: {file_path}")
                return False
            
            self.stop()  # Detener reproducción actual
            
            self.current_sound = pygame.mixer.Sound(str(path))
            self.volume = max(0.0, min(1.0, volume))
            self.current_sound.set_volume(self.volume)
            self._on_complete_callback = on_complete
            
            self.current_sound.play()
            self.is_playing = True
            
            # Iniciar thread de monitoreo
            self._play_thread = threading.Thread(target=self._monitor_playback)
            self._play_thread.start()
            
            logger.info(f"Reproduciendo audio: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al reproducir audio: {e}")
            return False
    
    def queue_audio(self, file_path: str) -> bool:
        """
        Añade un archivo de audio a la cola de reproducción.
        
        Args:
            file_path: Ruta al archivo de audio
            
        Returns:
            bool: True si se añadió a la cola
        """
        try:
            if Path(file_path).exists():
                self.audio_queue.put(file_path)
                logger.info(f"Audio añadido a la cola: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error al añadir audio a la cola: {e}")
            return False
    
    def play_queue(self) -> None:
        """Inicia la reproducción de la cola de audio"""
        if not self.is_playing and not self.audio_queue.empty():
            next_audio = self.audio_queue.get()
            self.play_audio(next_audio, on_complete=self.play_queue)
    
    def stop(self) -> None:
        """Detiene la reproducción actual"""
        if self.is_playing:
            self._should_stop = True
            if self.current_sound:
                self.current_sound.stop()
            self.is_playing = False
            logger.info("Reproducción detenida")
    
    def pause(self) -> None:
        """Pausa la reproducción actual"""
        if self.is_playing:
            pygame.mixer.pause()
            self.is_playing = False
            logger.info("Reproducción pausada")
    
    def resume(self) -> None:
        """Reanuda la reproducción pausada"""
        if not self.is_playing:
            pygame.mixer.unpause()
            self.is_playing = True
            logger.info("Reproducción reanudada")
    
    def set_volume(self, volume: float) -> None:
        """
        Ajusta el volumen de reproducción.
        
        Args:
            volume: Nivel de volumen (0.0 a 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.current_sound:
            self.current_sound.set_volume(self.volume)
        logger.info(f"Volumen ajustado a: {self.volume}")
    
    def _monitor_playback(self) -> None:
        """Monitorea la reproducción actual y ejecuta callbacks"""
        while self.is_playing and not self._should_stop:
            if not pygame.mixer.get_busy():
                self.is_playing = False
                if self._on_complete_callback:
                    self._on_complete_callback()
                break
            time.sleep(0.1)
        
        self._should_stop = False
    
    def cleanup(self) -> None:
        """Limpia recursos y detiene la reproducción"""
        self.stop()
        pygame.mixer.quit()
        logger.info("MediaManager limpiado")
