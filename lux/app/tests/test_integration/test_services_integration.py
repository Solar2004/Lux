import pytest
from unittest.mock import MagicMock, patch
from ...services.task_service import TaskService
from ...services.notification_service import NotificationService
from ...services.file_service import FileService
from PyQt6.QtWidgets import QSystemTrayIcon

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_tray_icon():
    return MagicMock(spec=QSystemTrayIcon)

@pytest.fixture
def task_service(mock_db_session):
    return TaskService(mock_db_session)

@pytest.fixture
def notification_service(mock_tray_icon):
    return NotificationService(mock_tray_icon)

@pytest.fixture
def file_service():
    return FileService()

def test_task_notification_integration(task_service, notification_service):
    """Prueba la integración entre tareas y notificaciones"""
    # Crear tarea
    task = task_service.create_task(1, "Test task")
    
    # Notificar sobre la tarea
    notification_service.notify(
        "Nueva Tarea",
        f"Tarea creada: {task.title}",
        'task',
        {'task_id': task.id}
    )
    
    # Verificar notificación
    assert len(notification_service.notification_queue) > 0
    notification = notification_service.notification_queue[0]
    assert notification['type'] == 'task'
    assert task.title in notification['message'] 