import pytest
from PyQt6.QtWidgets import QApplication
from unittest.mock import MagicMock, patch
from ...ui.main_window import MainWindow
from ...core.voice_manager import VoiceManager
from ...core.ai_manager import AIManager

@pytest.fixture
def app():
    return QApplication([])

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
def main_window(app, mock_db_session, voice_manager, ai_manager):
    return MainWindow(mock_db_session, voice_manager, ai_manager)

def test_ui_voice_integration(main_window):
    """Prueba la integración entre UI y reconocimiento de voz"""
    # Verificar estado inicial
    assert not main_window.voice_manager.is_listening
    
    # Simular click en botón de escucha
    main_window.listen_button.click()
    assert main_window.voice_manager.is_listening
    
    # Simular comando de voz
    main_window.voice_manager.callback("hola")
    assert main_window.status_label.text() != "Listo"
    
    # Detener escucha
    main_window.listen_button.click()
    assert not main_window.voice_manager.is_listening

def test_ui_notification_integration(main_window):
    """Prueba la integración entre UI y notificaciones"""
    # Simular completar tarea
    main_window._on_task_completed(1)
    
    # Verificar que se creó la notificación
    assert len(main_window.notification_service.notification_queue) > 0
    notification = main_window.notification_service.notification_queue[0]
    assert notification['type'] == 'task'
    assert 'completada' in notification['title'].lower()

def test_ui_chat_integration(main_window):
    """Prueba la integración del chat"""
    # Simular abrir ventana de chat
    with patch('PyQt6.QtWidgets.QDialog.exec') as mock_exec:
        main_window._show_chat()
        assert mock_exec.called 