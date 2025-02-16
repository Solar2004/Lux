from datetime import datetime, timedelta
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import Reminder
from .notification_service import NotificationService
import threading
import time

logger = logging.getLogger('lux')

class ReminderService:
    def __init__(self, db_session: Session, notification_service: NotificationService):
        self.db = db_session
        self.notification_service = notification_service
        self.check_thread = None
        self.is_running = False
        
        # Iniciar thread de verificación
        self.start_checking()
        logger.info("ReminderService inicializado")
    
    def create_reminder(self, user_id: int, title: str, due_date: datetime,
                       description: Optional[str] = None,
                       recurrence_rule: Optional[str] = None) -> Reminder:
        """
        Crea un nuevo recordatorio
        Args:
            user_id: ID del usuario
            title: Título del recordatorio
            due_date: Fecha/hora del recordatorio
            description: Descripción opcional
            recurrence_rule: Regla de recurrencia en formato iCal (ej: 'FREQ=DAILY')
        """
        try:
            reminder = Reminder(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                recurrence_rule=recurrence_rule,
                status='active'
            )
            
            self.db.add(reminder)
            self.db.commit()
            
            logger.info(f"Recordatorio creado: {title}")
            return reminder
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al crear recordatorio: {e}")
            raise
    
    def get_pending_reminders(self, minutes: int = 5) -> List[Reminder]:
        """
        Obtiene recordatorios pendientes para los próximos X minutos
        Args:
            minutes: Minutos a revisar
        Returns:
            Lista de recordatorios pendientes
        """
        try:
            now = datetime.utcnow()
            end_time = now + timedelta(minutes=minutes)
            
            reminders = self.db.query(Reminder).filter(
                Reminder.status == 'active',
                Reminder.scheduled_for.between(now, end_time)
            ).all()
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios pendientes: {e}")
            return []
    
    def mark_completed(self, reminder_id: int):
        """Marca un recordatorio como completado"""
        try:
            reminder = self.db.query(Reminder).get(reminder_id)
            if reminder:
                reminder.status = 'completed'
                self.db.commit()
                logger.info(f"Recordatorio {reminder_id} marcado como completado")
        except Exception as e:
            logger.error(f"Error al marcar recordatorio como completado: {e}")
            self.db.rollback()
    
    def dismiss(self, reminder_id: int, user_id: int):
        """Descarta un recordatorio"""
        try:
            reminder = self.db.query(Reminder).filter(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id
            ).first()
            
            if reminder:
                reminder.status = 'dismissed'
                reminder.updated_at = datetime.now()
                self.db.commit()
                logger.info(f"Recordatorio descartado: {reminder.title}")
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al descartar recordatorio: {e}")
            raise
    
    def start_checking(self):
        """Inicia el thread de verificación de recordatorios"""
        if not self.check_thread:
            self.is_running = True
            self.check_thread = threading.Thread(target=self._check_loop)
            self.check_thread.daemon = True
            self.check_thread.start()
            logger.info("Iniciada verificación de recordatorios")
    
    def stop_checking(self):
        """Detiene el thread de verificación"""
        self.is_running = False
        if self.check_thread:
            self.check_thread.join(timeout=1.0)
            self.check_thread = None
            logger.info("Detenida verificación de recordatorios")
    
    def _check_loop(self):
        """Loop principal de verificación de recordatorios"""
        while self.is_running:
            try:
                # Obtener recordatorios próximos (5 minutos)
                now = datetime.now()
                soon = now + timedelta(minutes=5)
                
                reminders = self.db.query(Reminder).filter(
                    Reminder.status == 'active',
                    Reminder.scheduled_for.between(now, soon)
                ).all()
                
                # Notificar recordatorios
                for reminder in reminders:
                    self.notification_service.notify(
                        title=reminder.title,
                        message=reminder.description or "¡Es hora!",
                        notification_type='reminder',
                        data={'reminder_id': reminder.id}
                    )
                    logger.info(f"Notificación enviada para: {reminder.title}")
                
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error en verificación de recordatorios: {e}")
                time.sleep(60)  # Esperar antes de reintentar
    
    def _create_next_occurrence(self, reminder: Reminder):
        """Crea el siguiente recordatorio recurrente"""
        # TODO: Implementar lógica de recurrencia usando rrule
        pass
