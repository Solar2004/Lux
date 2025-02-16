from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QSystemTrayIcon, QMenu,
                            QStyle)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
import logging
from pathlib import Path

from .components.lux_circle import LuxCircle
from ..core.voice_manager import VoiceManager
from ..core.ai_manager import AIManager
from ..services.task_service import TaskService
from ..services.reminder_service import ReminderService
from .. import config
from .components.task_view import TaskView
from .components.media_player import MediaPlayer
from ..core.command_handler import CommandHandler
from ..services.file_service import FileService
from .components.chat_window import ChatWindow
from .components.control_panel import ControlPanel
from ..services.notification_service import NotificationService
from ..core.function_manager import FunctionManager

logger = logging.getLogger('lux')

class MainWindow(QMainWindow):
    def __init__(self, db_session, voice_manager: VoiceManager, ai_manager: AIManager):
        super().__init__()
        
        self.db_session = db_session
        self.voice_manager = voice_manager
        self.ai_manager = ai_manager
        
        # Primero configurar el tray icon
        self._setup_tray()
        
        # Luego inicializar servicios que dependen del tray icon
        self.task_service = TaskService(db_session)
        self.notification_service = NotificationService(self.tray_icon)
        self.reminder_service = ReminderService(db_session, self.notification_service)
        self.file_service = FileService()
        
        # Inicializar command handler
        self.command_handler = CommandHandler(
            ai_service=self.ai_manager,
            task_service=self.task_service,
            media_player=None  # Se actualizará después de crear MediaPlayer
        )
        
        # Actualizar dependencias del VoiceManager
        self.voice_manager.set_command_handler(self.command_handler)
        self.voice_manager.set_ai_manager(self.ai_manager)
        
        # Iniciar escuchando por defecto
        self.is_listening = True
        self.voice_manager.start_listening()
        
        # Actualizar VoiceManager con servicios
        function_manager = FunctionManager(
            task_service=self.task_service,
            media_player=None,  # Se actualizará después de crear MediaPlayer
            reminder_service=self.reminder_service,
            file_service=self.file_service
        )
        self.voice_manager.function_manager = function_manager
        self.ai_manager.set_function_manager(function_manager)
        
        # Configurar UI después de tener todos los servicios
        self._setup_ui()
        self._setup_connections()
        
        # Añadir TaskView y MediaPlayer
        self.task_view = TaskView(self.task_service)
        self.task_view.taskCompleted.connect(self._on_task_completed)
        self.task_view.taskDeleted.connect(self._on_task_deleted)
        
        self.media_player = MediaPlayer(self.file_service)
        self.media_player.playbackFinished.connect(self._on_playback_finished)
        
        # Actualizar media_player en command_handler
        self.command_handler.media_player = self.media_player
        
        # Actualizar layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Cambiar a horizontal
        
        # Panel izquierdo (LuxCircle y controles)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_layout.addWidget(self.lux_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addLayout(self._create_control_buttons())
        left_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Panel derecho (TaskView y MediaPlayer)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.task_view, stretch=2)
        right_layout.addWidget(self.media_player, stretch=1)
        
        # Añadir paneles al layout principal
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Crear panel de control pero no mostrarlo
        self.control_panel = ControlPanel(
            self.voice_manager,
            self.ai_manager,
            self.media_player,
            self
        )
        
        logger.info("Ventana principal inicializada")
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setMinimumSize(400, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Círculo Lux (más grande y centrado)
        self.lux_circle = LuxCircle()
        self.lux_circle.setMinimumSize(200, 200)  # Hacer más grande el orbe
        main_layout.addWidget(self.lux_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Botones de control en una fila
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botón de mute con icono
        self.mute_button = QPushButton()
        self.mute_button.setCheckable(True)
        self.mute_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)))
        self.mute_button.setIconSize(QSize(24, 24))
        self.mute_button.setToolTip("Activar/Desactivar escucha")
        self.mute_button.toggled.connect(self._handle_mute_toggle)
        control_layout.addWidget(self.mute_button)
        
        # Botón de chat
        self.chat_button = QPushButton()
        self.chat_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)))
        self.chat_button.setIconSize(QSize(24, 24))
        self.chat_button.setToolTip("Abrir chat")
        self.chat_button.clicked.connect(self._show_chat)
        control_layout.addWidget(self.chat_button)
        
        # Botón de panel de control
        self.panel_button = QPushButton()
        self.panel_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)))
        self.panel_button.setIconSize(QSize(24, 24))
        self.panel_button.setToolTip("Panel de control")
        self.panel_button.clicked.connect(self._show_control_panel)
        control_layout.addWidget(self.panel_button)
        
        main_layout.addLayout(control_layout)
        
        # Reproductor de medios
        self.media_player = MediaPlayer(self.file_service)
        self.media_player.setMaximumHeight(100)  # Hacer más compacto
        main_layout.addWidget(self.media_player)
        
        # Estado
        self.status_label = QLabel("Escuchando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 8px;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
            QPushButton:checked {
                background-color: #404040;
            }
        """)
    
    def _setup_tray(self):
        """Configura el icono en la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Cargar icono
        icon_path = Path(config.RESOURCES_DIR) / "images" / "icons" / "app_icon.png"
        if not icon_path.exists():
            # Usar icono por defecto si no existe el personalizado
            self.tray_icon.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)))
        else:
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        
        # Menú del tray
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Ocultar", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _setup_connections(self):
        """Configura las conexiones de señales y slots"""
        self.mute_button.toggled.connect(self._handle_mute_toggle)
        self.chat_button.clicked.connect(self._show_chat)
        self.panel_button.clicked.connect(self._show_control_panel)
        
        # Conexión con el tray
        self.tray_icon.activated.connect(self._handle_tray_activation)
    
    def _handle_mute_toggle(self, checked):
        """Maneja el toggle del botón de mute"""
        if checked:
            self.voice_manager.stop_listening()
            self.lux_circle.stop_listening()
            self.status_label.setText("Escucha pausada")
            self.mute_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted)))
        else:
            # Crear nuevo thread de escucha
            self.voice_manager.is_listening = True
            self.voice_manager.start_listening()
            self.lux_circle.start_listening()
            self.status_label.setText("Escuchando...")
            self.mute_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)))
    
    def _handle_tray_activation(self, reason):
        """Maneja la activación del icono en la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self.hide()
        event.ignore()  # Previene el cierre real de la aplicación
    
    def cleanup(self):
        """Limpia recursos antes de cerrar"""
        self.voice_manager.cleanup()
        self.tray_icon.hide()
        logger.info("Recursos de la ventana principal liberados")

    def _on_voice_command(self, text: str) -> str:
        """
        Maneja comandos de voz y retorna la respuesta
        Returns:
            str: Respuesta para TTS
        """
        try:
            # Primero intentar procesar como comando
            command_response = self.command_handler.handle_command(text)
            if command_response:
                return command_response
            
            # Si no es comando, procesar como chat
            chat_response = self.ai_manager.chat(text)
            return chat_response or "No pude entender el comando."
            
        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            return "Lo siento, ocurrió un error al procesar tu comando."

    def _on_task_completed(self, task_id):
        """Callback cuando se completa una tarea"""
        self.status_label.setText("Tarea completada")
        self.notification_service.notify(
            "Tarea Completada",
            "La tarea ha sido marcada como completada",
            'task',
            {'task_id': task_id}
        )
    
    def _on_task_deleted(self, task_id):
        """Callback cuando se elimina una tarea"""
        self.status_label.setText("Tarea eliminada")
        self.notification_service.notify(
            "Tarea Eliminada",
            "La tarea ha sido eliminada",
            'task',
            {'task_id': task_id}
        )
    
    def _on_playback_finished(self):
        """Callback cuando termina la reproducción"""
        self.status_label.setText("Reproducción finalizada")
        self.notification_service.notify(
            "Reproducción Finalizada",
            "La reproducción del medio ha terminado",
            'system'
        )
    
    def _create_control_buttons(self):
        """Crea el layout de botones de control"""
        control_layout = QHBoxLayout()
        
        self.mute_button = QPushButton()
        self.mute_button.setCheckable(True)
        self.mute_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)))
        self.mute_button.setIconSize(QSize(24, 24))
        self.mute_button.setToolTip("Activar/Desactivar escucha")
        self.mute_button.toggled.connect(self._handle_mute_toggle)
        control_layout.addWidget(self.mute_button)
        
        self.chat_button = QPushButton()
        self.chat_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)))
        self.chat_button.setIconSize(QSize(24, 24))
        self.chat_button.setToolTip("Abrir chat")
        self.chat_button.clicked.connect(self._show_chat)
        control_layout.addWidget(self.chat_button)
        
        self.panel_button = QPushButton()
        self.panel_button.setIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)))
        self.panel_button.setIconSize(QSize(24, 24))
        self.panel_button.setToolTip("Panel de control")
        self.panel_button.clicked.connect(self._show_control_panel)
        control_layout.addWidget(self.panel_button)
        
        return control_layout
    
    def _show_chat(self):
        """Muestra la ventana de chat"""
        chat_window = ChatWindow(self.ai_manager, self)
        chat_window.exec()
    
    def _show_control_panel(self):
        """Muestra el panel de control"""
        if not self.control_panel.isVisible():
            self.control_panel.show()
        else:
            self.control_panel.activateWindow()  # Traer al frente si ya está visible
