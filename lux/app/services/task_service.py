from datetime import datetime
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database.models import Task, User

logger = logging.getLogger('lux')

class TaskService:
    def __init__(self, db_session: Session):
        self.session = db_session
    
    def create_task(
        self,
        user_id: int,
        title: str,
        description: str = "",
        due_date: Optional[datetime] = None,
        priority: int = 0
    ) -> Optional[Task]:
        """
        Crea una nueva tarea para un usuario.
        
        Args:
            user_id: ID del usuario
            title: Título de la tarea
            description: Descripción detallada
            due_date: Fecha límite (opcional)
            priority: Prioridad (0=baja, 1=media, 2=alta)
            
        Returns:
            Task: La tarea creada o None si hay error
        """
        try:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority
            )
            
            self.session.add(task)
            self.session.commit()
            
            logger.info(f"Tarea creada: {title} para usuario {user_id}")
            return task
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error al crear tarea: {e}")
            return None
    
    def get_user_tasks(
        self,
        user_id: int,
        include_completed: bool = False,
        sort_by_priority: bool = True
    ) -> List[Task]:
        """
        Obtiene las tareas de un usuario.
        
        Args:
            user_id: ID del usuario
            include_completed: Incluir tareas completadas
            sort_by_priority: Ordenar por prioridad
            
        Returns:
            List[Task]: Lista de tareas
        """
        try:
            query = self.session.query(Task).filter(Task.user_id == user_id)
            
            if not include_completed:
                query = query.filter(Task.completed == False)
            
            if sort_by_priority:
                query = query.order_by(desc(Task.priority), Task.due_date)
            else:
                query = query.order_by(Task.due_date)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error al obtener tareas: {e}")
            return []
    
    def update_task(
        self,
        task_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[int] = None
    ) -> bool:
        """
        Actualiza una tarea existente.
        
        Args:
            task_id: ID de la tarea
            user_id: ID del usuario (para verificación)
            title: Nuevo título (opcional)
            description: Nueva descripción (opcional)
            due_date: Nueva fecha límite (opcional)
            priority: Nueva prioridad (opcional)
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            task = self.session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if not task:
                return False
            
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if due_date is not None:
                task.due_date = due_date
            if priority is not None:
                task.priority = priority
            
            self.session.commit()
            logger.info(f"Tarea {task_id} actualizada")
            return True
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error al actualizar tarea: {e}")
            return False
    
    def mark_completed(self, task_id: int, user_id: int) -> bool:
        """
        Marca una tarea como completada.
        
        Args:
            task_id: ID de la tarea
            user_id: ID del usuario (para verificación)
            
        Returns:
            bool: True si se completó exitosamente
        """
        try:
            task = self.session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if task:
                task.completed = True
                self.session.commit()
                logger.info(f"Tarea {task_id} marcada como completada")
                return True
            return False
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error al marcar tarea como completada: {e}")
            return False
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Elimina una tarea.
        
        Args:
            task_id: ID de la tarea
            user_id: ID del usuario (para verificación)
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            task = self.session.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user_id
            ).first()
            
            if task:
                self.session.delete(task)
                self.session.commit()
                logger.info(f"Tarea {task_id} eliminada")
                return True
            return False
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error al eliminar tarea: {e}")
            return False
