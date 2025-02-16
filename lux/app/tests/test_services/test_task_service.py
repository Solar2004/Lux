import pytest
from datetime import datetime, timedelta
from app.services.task_service import TaskService
from app.database.models import Task, User

@pytest.fixture
def test_user(db_session):
    user = User(username="test_user")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def task_service(db_session):
    return TaskService(db_session)

def test_create_task(db_session, test_user, task_service):
    # Test crear tarea
    due_date = datetime.now() + timedelta(days=1)
    task = task_service.create_task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        due_date=due_date,
        priority=2
    )
    
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.user_id == test_user.id
    assert task.priority == 2
    assert not task.completed

def test_get_user_tasks(db_session, test_user, task_service):
    # Crear tareas de prueba
    task_service.create_task(test_user.id, "High Priority", priority=2)
    task_service.create_task(test_user.id, "Medium Priority", priority=1)
    task_service.create_task(test_user.id, "Low Priority", priority=0)
    
    # Obtener tareas ordenadas por prioridad
    tasks = task_service.get_user_tasks(test_user.id, sort_by_priority=True)
    
    assert len(tasks) == 3
    assert tasks[0].title == "High Priority"
    assert tasks[1].title == "Medium Priority"
    assert tasks[2].title == "Low Priority"

def test_update_task(db_session, test_user, task_service):
    # Crear tarea
    task = task_service.create_task(test_user.id, "Original Title")
    
    # Actualizar tarea
    success = task_service.update_task(
        task.id,
        test_user.id,
        title="Updated Title",
        priority=2
    )
    
    assert success
    updated_task = db_session.query(Task).get(task.id)
    assert updated_task.title == "Updated Title"
    assert updated_task.priority == 2

def test_mark_completed(db_session, test_user, task_service):
    # Crear tarea
    task = task_service.create_task(test_user.id, "Test Task")
    
    # Marcar como completada
    success = task_service.mark_completed(task.id, test_user.id)
    assert success
    
    # Verificar que está completada
    completed_task = db_session.query(Task).get(task.id)
    assert completed_task.completed
    
    # Verificar que no aparece en tareas activas
    active_tasks = task_service.get_user_tasks(test_user.id)
    assert len(active_tasks) == 0

def test_delete_task(db_session, test_user, task_service):
    # Crear tarea
    task = task_service.create_task(test_user.id, "Test Task")
    
    # Eliminar tarea
    success = task_service.delete_task(task.id, test_user.id)
    assert success
    
    # Verificar que fue eliminada
    deleted_task = db_session.query(Task).get(task.id)
    assert deleted_task is None

def test_invalid_operations(db_session, test_user, task_service):
    # Intentar operaciones con IDs inválidos
    invalid_task_id = 999
    invalid_user_id = 999
    
    assert not task_service.update_task(invalid_task_id, test_user.id)
    assert not task_service.mark_completed(invalid_task_id, test_user.id)
    assert not task_service.delete_task(invalid_task_id, test_user.id)
    
    # Crear tarea y probar con usuario inválido
    task = task_service.create_task(test_user.id, "Test Task")
    assert not task_service.update_task(task.id, invalid_user_id)
    assert not task_service.mark_completed(task.id, invalid_user_id)
    assert not task_service.delete_task(task.id, invalid_user_id) 