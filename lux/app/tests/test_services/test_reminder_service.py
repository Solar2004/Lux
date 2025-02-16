import pytest
from datetime import datetime, timedelta
from app.services.reminder_service import ReminderService
from app.database.models import Reminder, User

@pytest.fixture
def test_user(db_session):
    user = User(username="test_user")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def reminder_service(db_session):
    return ReminderService(db_session)

def test_create_reminder(db_session, test_user, reminder_service):
    # Test crear recordatorio
    due_date = datetime.now() + timedelta(days=1)
    reminder = reminder_service.create_reminder(
        user_id=test_user.id,
        title="Test Reminder",
        description="Test Description",
        due_date=due_date,
        repeat_type="daily"
    )
    
    assert reminder.id is not None
    assert reminder.title == "Test Reminder"
    assert reminder.user_id == test_user.id
    assert reminder.repeat_type == "daily"
    assert not reminder.completed

def test_get_active_reminders(db_session, test_user, reminder_service):
    # Crear recordatorios de prueba
    due_date = datetime.now() + timedelta(days=1)
    reminder1 = reminder_service.create_reminder(test_user.id, "Active 1", "Test", due_date)
    reminder2 = reminder_service.create_reminder(test_user.id, "Active 2", "Test", due_date)
    reminder3 = reminder_service.create_reminder(test_user.id, "Completed", "Test", due_date)
    
    # Marcar uno como completado
    reminder_service.mark_completed(reminder3.id, test_user.id)
    
    # Obtener recordatorios activos
    active_reminders = reminder_service.get_active_reminders(test_user.id)
    
    assert len(active_reminders) == 2
    assert all(not r.completed for r in active_reminders)
    assert "Active 1" in [r.title for r in active_reminders]
    assert "Active 2" in [r.title for r in active_reminders]

def test_mark_completed(db_session, test_user, reminder_service):
    # Crear recordatorio
    due_date = datetime.now() + timedelta(days=1)
    reminder = reminder_service.create_reminder(
        test_user.id, "Test Reminder", "Test", due_date
    )
    
    # Marcar como completado
    success = reminder_service.mark_completed(reminder.id, test_user.id)
    assert success
    
    # Verificar que está completado
    updated_reminder = db_session.query(Reminder).get(reminder.id)
    assert updated_reminder.completed
    
    # Intentar marcar un recordatorio inexistente
    success = reminder_service.mark_completed(999, test_user.id)
    assert not success

def test_delete_reminder(db_session, test_user, reminder_service):
    # Crear recordatorio
    due_date = datetime.now() + timedelta(days=1)
    reminder = reminder_service.create_reminder(
        test_user.id, "Test Reminder", "Test", due_date
    )
    
    # Eliminar recordatorio
    success = reminder_service.delete_reminder(reminder.id, test_user.id)
    assert success
    
    # Verificar que fue eliminado
    deleted_reminder = db_session.query(Reminder).get(reminder.id)
    assert deleted_reminder is None
    
    # Intentar eliminar un recordatorio inexistente
    success = reminder_service.delete_reminder(999, test_user.id)
    assert not success

def test_reminder_invalid_user(db_session, test_user, reminder_service):
    # Intentar operaciones con un usuario inválido
    due_date = datetime.now() + timedelta(days=1)
    reminder = reminder_service.create_reminder(
        test_user.id, "Test Reminder", "Test", due_date
    )
    
    invalid_user_id = 999
    
    # Intentar marcar como completado
    success = reminder_service.mark_completed(reminder.id, invalid_user_id)
    assert not success
    
    # Intentar eliminar
    success = reminder_service.delete_reminder(reminder.id, invalid_user_id)
    assert not success 