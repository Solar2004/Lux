from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QListWidgetItem, QPushButton, QLabel, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from ...services.task_service import TaskService
import logging

logger = logging.getLogger(__name__)

class TaskItem(QWidget):
    """Widget personalizado para mostrar una tarea"""
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Título y descripción
        text_layout = QVBoxLayout()
        self.title_label = QLabel(self.task.title)
        self.title_label.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(self.title_label)
        
        if self.task.description:
            self.desc_label = QLabel(self.task.description)
            self.desc_label.setStyleSheet("color: #666;")
            text_layout.addWidget(self.desc_label)
        
        layout.addLayout(text_layout)
        
        # Fecha límite
        if self.task.due_date:
            due_date = self.task.due_date.strftime("%d/%m/%Y")
            self.date_label = QLabel(due_date)
            self.date_label.setStyleSheet("color: #888;")
            layout.addWidget(self.date_label)
        
        # Prioridad
        priority_colors = {0: "#808080", 1: "#FFA500", 2: "#FF0000"}
        self.priority_indicator = QLabel("●")
        self.priority_indicator.setStyleSheet(f"color: {priority_colors[self.task.priority]};")
        layout.addWidget(self.priority_indicator)

class TaskView(QWidget):
    """Widget para mostrar y gestionar tareas"""
    taskCompleted = pyqtSignal(int)  # ID de la tarea completada
    taskDeleted = pyqtSignal(int)    # ID de la tarea eliminada
    
    def __init__(self, task_service: TaskService, parent=None):
        super().__init__(parent)
        self.task_service = task_service
        self._setup_ui()
        self.refresh_tasks()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("Tareas")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #FFFFFF;
        """)
        header.addWidget(title)
        
        add_button = QPushButton("Nueva Tarea")
        add_button.clicked.connect(self._add_task)
        header.addWidget(add_button)
        
        layout.addLayout(header)
        
        # Lista de tareas
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3E3E3E;
            }
            QListWidget::item:hover {
                background-color: #3D3D3D;
            }
        """)
        layout.addWidget(self.task_list)
    
    def _add_task(self):
        """Agrega una nueva tarea"""
        try:
            # Por ahora agregamos una tarea de prueba
            task = self.task_service.create_task(
                user_id=1,  # TODO: Usar ID real
                title="Nueva tarea",
                description="",
                priority=0
            )
            logger.info(f"Tarea creada: {task.title}")
            self.refresh_tasks()
        except Exception as e:
            logger.error(f"Error al crear tarea: {e}")
    
    def _create_task_widget(self, task):
        """Crea el widget para una tarea"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.stateChanged.connect(lambda state: self._toggle_task(task, state))
        layout.addWidget(checkbox)
        
        # Título
        title = QLabel(task.title)
        title.setStyleSheet("color: #FFFFFF;")
        if task.completed:
            title.setStyleSheet("color: #888888; text-decoration: line-through;")
        layout.addWidget(title)
        
        # Prioridad
        priority_label = QLabel(["Baja", "Media", "Alta"][task.priority])
        priority_label.setStyleSheet(f"""
            color: {['#4CAF50', '#FFC107', '#F44336'][task.priority]};
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
        """)
        layout.addWidget(priority_label)
        
        # Botón eliminar
        delete_button = QPushButton("×")
        delete_button.setStyleSheet("""
            background: none;
            color: #FF5252;
            font-size: 18px;
            font-weight: bold;
            border: none;
            padding: 0 5px;
        """)
        delete_button.clicked.connect(lambda: self._delete_task(task))
        layout.addWidget(delete_button)
        
        # Agregar espaciador para alinear elementos
        layout.addStretch()
        
        return widget
    
    def _toggle_task(self, task, state):
        """Cambia el estado de una tarea"""
        try:
            completed = state == Qt.CheckState.Checked.value
            self.task_service.update_task(
                task.id,
                completed=completed
            )
            if completed:
                self.taskCompleted.emit(task.id)
            self.refresh_tasks()
        except Exception as e:
            logger.error(f"Error al actualizar tarea: {e}")
    
    def _delete_task(self, task):
        """Elimina una tarea"""
        try:
            self.task_service.delete_task(task.id)
            self.taskDeleted.emit(task.id)
            self.refresh_tasks()
        except Exception as e:
            logger.error(f"Error al eliminar tarea: {e}")
    
    def refresh_tasks(self):
        """Actualiza la lista de tareas"""
        try:
            self.task_list.clear()
            tasks = self.task_service.get_user_tasks(1)  # TODO: Usar ID real
            
            for task in tasks:
                item = QListWidgetItem()
                task_widget = self._create_task_widget(task)
                item.setSizeHint(task_widget.sizeHint())
                self.task_list.addItem(item)
                self.task_list.setItemWidget(item, task_widget)
                
        except Exception as e:
            logger.error(f"Error al actualizar tareas: {e}")
    
    def _show_context_menu(self, position):
        """Muestra el menú contextual para una tarea"""
        item = self.task_list.itemAt(position)
        if not item:
            return
        
        task_widget = self.task_list.itemWidget(item)
        task = task_widget.task
        
        menu = QMenu()
        complete_action = menu.addAction("Completar")
        delete_action = menu.addAction("Eliminar")
        
        action = menu.exec(self.task_list.viewport().mapToGlobal(position))
        
        if action == complete_action:
            self.task_service.mark_completed(task.id, 1)  # TODO: Usar ID de usuario real
            self.taskCompleted.emit(task.id)
            self.refresh_tasks()
        elif action == delete_action:
            self.task_service.delete_task(task.id, 1)  # TODO: Usar ID de usuario real
            self.taskDeleted.emit(task.id)
            self.refresh_tasks()
