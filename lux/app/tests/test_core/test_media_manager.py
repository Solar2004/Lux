import pytest
import time
from pathlib import Path
import tempfile
import wave
import numpy as np
from app.core.media_manager import MediaManager

@pytest.fixture
def media_manager():
    manager = MediaManager()
    yield manager
    manager.cleanup()

@pytest.fixture
def test_audio_file():
    # Crear un archivo de audio WAV de prueba
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        # Crear un archivo WAV simple
        with wave.open(tmp.name, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            # Generar 1 segundo de silencio
            samples = np.zeros(44100, dtype=np.int16)
            wav.writeframes(samples.tobytes())
        
        yield tmp.name
    
    # Limpiar archivo temporal
    Path(tmp.name).unlink()

def test_play_audio(media_manager, test_audio_file):
    # Test reproducción básica
    assert media_manager.play_audio(test_audio_file)
    assert media_manager.is_playing
    
    # Esperar un momento y detener
    time.sleep(0.1)
    media_manager.stop()
    assert not media_manager.is_playing

def test_volume_control(media_manager, test_audio_file):
    # Test control de volumen
    media_manager.play_audio(test_audio_file, volume=0.5)
    assert media_manager.volume == 0.5
    
    # Ajustar volumen
    media_manager.set_volume(0.8)
    assert media_manager.volume == 0.8
    
    # Probar límites
    media_manager.set_volume(1.5)  # Debería limitarse a 1.0
    assert media_manager.volume == 1.0
    
    media_manager.set_volume(-0.5)  # Debería limitarse a 0.0
    assert media_manager.volume == 0.0

def test_queue_functionality(media_manager, test_audio_file):
    # Test cola de reproducción
    assert media_manager.queue_audio(test_audio_file)
    assert media_manager.queue_audio(test_audio_file)
    
    # Iniciar reproducción de cola
    media_manager.play_queue()
    assert media_manager.is_playing
    
    # Esperar un momento y detener
    time.sleep(0.1)
    media_manager.stop()

def test_pause_resume(media_manager, test_audio_file):
    # Test pausa/resumen
    media_manager.play_audio(test_audio_file)
    assert media_manager.is_playing
    
    media_manager.pause()
    assert not media_manager.is_playing
    
    media_manager.resume()
    assert media_manager.is_playing
    
    media_manager.stop()

def test_invalid_file(media_manager):
    # Test archivo inválido
    assert not media_manager.play_audio("nonexistent.wav")
    assert not media_manager.queue_audio("nonexistent.wav")

def test_completion_callback(media_manager, test_audio_file):
    # Test callback de finalización
    callback_called = False
    
    def on_complete():
        nonlocal callback_called
        callback_called = True
    
    media_manager.play_audio(test_audio_file, on_complete=on_complete)
    
    # Esperar a que termine la reproducción
    time.sleep(1.1)  # Esperar más que la duración del audio
    
    assert callback_called 