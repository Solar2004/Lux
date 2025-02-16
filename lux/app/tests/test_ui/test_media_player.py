import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import tempfile
import wave
import numpy as np
from pathlib import Path
from app.ui.components.media_player import MediaPlayer
from app.services.file_service import FileService

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def media_player(app, tmp_path):
    file_service = FileService(base_dir=str(tmp_path))
    return MediaPlayer(file_service)

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

def test_media_player_initialization(media_player):
    assert not media_player.is_playing
    assert media_player.volume == 0.5
    assert media_player.current_file is None

def test_load_file(media_player, test_audio_file):
    assert media_player.load_file(test_audio_file)
    assert media_player.current_file == Path(test_audio_file)
    assert not media_player.is_playing

def test_play_pause(media_player, test_audio_file):
    media_player.load_file(test_audio_file)
    
    # Iniciar reproducción
    media_player.play_pause()
    assert media_player.is_playing
    
    # Pausar
    media_player.play_pause()
    assert not media_player.is_playing

def test_stop(media_player, test_audio_file):
    media_player.load_file(test_audio_file)
    media_player.play_pause()
    
    media_player.stop()
    assert not media_player.is_playing
    assert media_player.position_slider.value() == 0

def test_volume_control(media_player):
    # Probar cambio de volumen
    media_player._set_volume(75)
    assert media_player.volume == 0.75
    
    media_player._set_volume(0)
    assert media_player.volume == 0
    
    media_player._set_volume(100)
    assert media_player.volume == 1.0

def test_cleanup(media_player, test_audio_file):
    media_player.load_file(test_audio_file)
    media_player.play_pause()
    
    media_player.cleanup()
    assert not media_player.is_playing 