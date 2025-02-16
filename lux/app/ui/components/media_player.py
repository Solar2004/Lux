from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QStyle, QSizePolicy, QProgressBar, QListWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
import pygame
import logging
from pathlib import Path
from ...services.file_service import FileService

logger = logging.getLogger('lux')

class MediaPlayer(QWidget):
    """Widget para reproducción de audio"""
    playbackFinished = pyqtSignal()
    
    def __init__(self, file_service: FileService, parent=None):
        super().__init__(parent)
        self.file_service = file_service
        
        # Inicializar pygame mixer
        pygame.mixer.init()
        
        # Estado del reproductor
        self.current_file = None
        self.is_playing = False
        self.volume = 0.5
        
        # Timer para actualizar la posición
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(100)  # 100ms
        self.update_timer.timeout.connect(self._update_position)
        
        self._setup_ui()
        logger.info("MediaPlayer inicializado")
    
    def _setup_ui(self):
        """Configura la interfaz del reproductor"""
        layout = QVBoxLayout(self)
        
        # Panel superior con título y controles
        top_panel = QHBoxLayout()
        
        # Título actual
        self.title_label = QLabel("No hay nada reproduciéndose")
        self.title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14px;
            font-weight: bold;
        """)
        top_panel.addWidget(self.title_label)
        
        # Controles
        controls = QHBoxLayout()
        
        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))
        controls.addWidget(self.prev_button)
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        controls.addWidget(self.play_button)
        
        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward))
        controls.addWidget(self.next_button)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        controls.addWidget(self.volume_slider)
        
        top_panel.addLayout(controls)
        layout.addLayout(top_panel)
        
        # Barra de progreso
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("0:00 / 0:00")
        progress_layout.addWidget(self.time_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3E3E3E;
                border-radius: 2px;
                background: #2D2D2D;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Lista de reproducción
        self.playlist = QListWidget()
        self.playlist.setMaximumHeight(100)
        self.playlist.setStyleSheet("""
            QListWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.playlist)
        
        # Estilo
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #404040;
                border: none;
                border-radius: 15px;
                padding: 5px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #4D4D4D;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #CCCCCC;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
    
    def load_file(self, file_path: str) -> bool:
        """Carga un archivo de audio"""
        try:
            pygame.mixer.music.load(file_path)
            self.current_file = Path(file_path)
            self.title_label.setText(self.current_file.name)
            self.position_slider.setValue(0)
            logger.info(f"Archivo cargado: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error al cargar archivo: {e}")
            return False
    
    def play_pause(self):
        """Alterna entre reproducir y pausar"""
        if not self.current_file:
            return
        
        try:
            if not self.is_playing:
                pygame.mixer.music.play()
                self.is_playing = True
                self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
                self.update_timer.start()
                logger.info("Reproducción iniciada")
            else:
                pygame.mixer.music.pause()
                self.is_playing = False
                self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                self.update_timer.stop()
                logger.info("Reproducción pausada")
        except Exception as e:
            logger.error(f"Error en play/pause: {e}")
    
    def stop(self):
        """Detiene la reproducción"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.position_slider.setValue(0)
            self.update_timer.stop()
            logger.info("Reproducción detenida")
        except Exception as e:
            logger.error(f"Error al detener: {e}")
    
    def _set_volume(self, value):
        """Ajusta el volumen"""
        self.volume = value / 100
        pygame.mixer.music.set_volume(self.volume)
    
    def _seek(self, position):
        """Busca una posición en el archivo"""
        if self.current_file:
            # pygame.mixer.music no soporta seek directamente
            # Tendríamos que reimplementar esto con otra biblioteca
            pass
    
    def _update_position(self):
        """Actualiza la posición del slider"""
        if not pygame.mixer.music.get_busy():
            self.stop()
            self.playbackFinished.emit()
    
    def cleanup(self):
        """Limpia recursos"""
        self.stop()
        pygame.mixer.quit()
        logger.info("MediaPlayer limpiado")
