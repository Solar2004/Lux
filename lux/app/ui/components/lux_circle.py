from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QPointF, QRectF, QTimer, pyqtProperty
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QRadialGradient, QPen
import math

class LuxCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuración inicial
        self.setMinimumSize(200, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # Estado del círculo
        self._radius = 50.0
        self._pulse_scale = 1.0
        self._rotation = 0.0
        self._opacity = 1.0
        self._color = QColor(64, 144, 255)  # Azul por defecto
        self._is_listening = False
        self._is_speaking = False
        
        # Animaciones
        self._setup_animations()
        
        # Timer para la rotación continua
        self._rotation_timer = QTimer(self)
        self._rotation_timer.timeout.connect(self._update_rotation)
        self._rotation_timer.start(50)  # 20 FPS
    
    def _setup_animations(self):
        """Configura las animaciones del círculo"""
        # Animación de pulso
        self._pulse_animation = QPropertyAnimation(self, b"pulse_scale")
        self._pulse_animation.setDuration(1000)
        self._pulse_animation.setLoopCount(-1)  # Infinito
        self._pulse_animation.setStartValue(1.0)
        self._pulse_animation.setEndValue(1.2)
        
        # Animación de opacidad
        self._opacity_animation = QPropertyAnimation(self, b"opacity")
        self._opacity_animation.setDuration(500)
    
    def start_listening(self):
        """Inicia el modo de escucha"""
        self._is_listening = True
        self._color = QColor(255, 64, 129)  # Rosa/Rojo
        self._pulse_animation.start()
        self.update()
    
    def stop_listening(self):
        """Detiene el modo de escucha"""
        self._is_listening = False
        self._color = QColor(64, 144, 255)  # Azul
        self._pulse_animation.stop()
        self._pulse_scale = 1.0
        self.update()
    
    def start_speaking(self):
        """Inicia el modo de habla"""
        self._is_speaking = True
        self._color = QColor(76, 175, 80)  # Verde
        self._pulse_animation.start()
        self.update()
    
    def stop_speaking(self):
        """Detiene el modo de habla"""
        self._is_speaking = False
        self._color = QColor(64, 144, 255)  # Azul
        self._pulse_animation.stop()
        self._pulse_scale = 1.0
        self.update()
    
    def _update_rotation(self):
        """Actualiza la rotación del círculo"""
        self._rotation += 2
        if self._rotation >= 360:
            self._rotation = 0
        self.update()
    
    def paintEvent(self, event):
        """Dibuja el círculo y sus efectos"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calcular el centro y radio
        center = QPointF(self.width() / 2, self.height() / 2)
        scaled_radius = self._radius * self._pulse_scale
        
        # Crear el gradiente radial
        gradient = QRadialGradient(center, scaled_radius)
        base_color = self._color
        gradient.setColorAt(0, QColor(base_color.red(), base_color.green(), 
                                    base_color.blue(), 150))
        gradient.setColorAt(1, QColor(base_color.red(), base_color.green(), 
                                    base_color.blue(), 0))
        
        # Dibujar el círculo principal
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, scaled_radius, scaled_radius)
        
        # Dibujar anillo exterior
        painter.save()
        painter.translate(center)
        painter.rotate(self._rotation)
        
        path = QPainterPath()
        rect = QRectF(-scaled_radius, -scaled_radius, 
                     scaled_radius * 2, scaled_radius * 2)
        path.addEllipse(rect)
        
        pen_width = 2
        painter.setPen(QPen(self._color, pen_width))
        painter.drawPath(path)
        
        # Dibujar puntos decorativos
        if self._is_listening or self._is_speaking:
            num_points = 8
            point_radius = 3
            for i in range(num_points):
                angle = (i * 360 / num_points) * math.pi / 180
                x = scaled_radius * math.cos(angle)
                y = scaled_radius * math.sin(angle)
                painter.drawEllipse(QPointF(x, y), point_radius, point_radius)
        
        painter.restore()
    
    # Propiedades para animaciones
    def get_pulse_scale(self):
        return self._pulse_scale
    
    def set_pulse_scale(self, scale):
        self._pulse_scale = scale
        self.update()
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()
    
    pulse_scale = pyqtProperty(float, get_pulse_scale, set_pulse_scale)
    opacity = pyqtProperty(float, get_opacity, set_opacity)
