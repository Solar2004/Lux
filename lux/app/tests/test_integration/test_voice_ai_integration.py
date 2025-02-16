import pytest
from unittest.mock import MagicMock, patch
from ...core.voice_manager import VoiceManager
from ...core.ai_manager import AIManager
from ...services.task_service import TaskService
from ...core.command_handler import CommandHandler

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def voice_manager():
    with patch('google.cloud.speech.SpeechClient'):
        with patch('google.cloud.texttospeech.TextToSpeechClient'):
            return VoiceManager()

@pytest.fixture
def ai_manager():
    with patch('google.generativeai.GenerativeModel'):
        return AIManager()

@pytest.fixture
def task_service(mock_db_session):
    return TaskService(mock_db_session)

@pytest.fixture
def command_handler(ai_manager, task_service):
    return CommandHandler(ai_manager, task_service, None)

def test_voice_to_command_flow(voice_manager, command_handler):
    """Prueba el flujo completo desde voz hasta comando"""
    # Simular callback de voz
    received_command = None
    def command_callback(text):
        nonlocal received_command
        received_command = text
    
    # Iniciar escucha
    voice_manager.start_listening(command_callback)
    
    # Simular reconocimiento de voz
    voice_manager.callback("crear tarea comprar leche")
    
    # Verificar que se recibió el comando
    assert received_command == "crear tarea comprar leche"
    
    # Limpiar
    voice_manager.cleanup() 