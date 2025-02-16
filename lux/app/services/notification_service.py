from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import QTimer
from datetime import datetime
import logging
from typing import Optional, Dict
from pathlib import Path
import json

logger = logging.getLogger('lux')

class NotificationService:
    def __init__(self, tray_icon: QSystemTrayIcon):
        self.tray_icon = tray_icon
        self.notification_queue = []
        self.is_showing = False
        
        # Cargar sonidos de notificación
        self.sounds = {
            'task': str(Path('resources/audio/notifications/task.mp3')),
            'reminder': str(Path('resources/audio/notifications/reminder.mp3')),
            'system': str(Path('resources/audio/notifications/system.mp3'))
        }
        
        # Timer para procesar cola
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self._process_queue)
        self.queue_timer.start(1000)  # Procesar cada segundo
        
        logger.info("NotificationService inicializado")
    
    def notify(self, title: str, message: str, 
               notification_type: str = 'system',
               data: Optional[Dict] = None,
               timeout: int = 5000):
        """
        Envía una notificación
        Args:
            title: Título de la notificación
            message: Mensaje principal
            notification_type: Tipo de notificación ('system', 'task', 'reminder')
            data: Datos adicionales
            timeout: Tiempo en ms que se muestra la notificación
        """
        notification = {
            'title': title,
            'message': message,
            'type': notification_type,
            'data': data or {},
            'timeout': timeout,
            'timestamp': datetime.now().isoformat()
        }
        
        self.notification_queue.append(notification)
        self._save_notification(notification)
        logger.info(f"Notificación añadida a la cola: {title}")
    
    def _process_queue(self):
        """Procesa la cola de notificaciones"""
        if not self.notification_queue or self.is_showing:
            return
        
        notification = self.notification_queue.pop(0)
        self.is_showing = True
        
        # Mostrar notificación
        self.tray_icon.showMessage(
            notification['title'],
            notification['message'],
            QSystemTrayIcon.MessageIcon.Information,
            notification['timeout']
        )
        
        # Reproducir sonido según tipo
        sound_file = self.sounds.get(notification['type'])
        if sound_file:
            # TODO: Reproducir sonido
            pass
        
        # Resetear estado después del timeout
        QTimer.singleShot(notification['timeout'], self._reset_showing)
    
    def _reset_showing(self):
        """Resetea el estado de mostrado"""
        self.is_showing = False
    
    def _save_notification(self, notification: Dict):
        """Guarda la notificación en el historial"""
        try:
            history_file = Path('resources/notifications_history.json')
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar historial existente
            if history_file.exists():
                with history_file.open('r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Mantener solo las últimas 100 notificaciones
            history.append(notification)
            if len(history) > 100:
                history = history[-100:]
            
            # Guardar historial actualizado
            with history_file.open('w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error al guardar notificación: {e}") 