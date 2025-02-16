import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.ui.components.lux_circle import LuxCircle

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def lux_circle(app):
    return LuxCircle()

def test_lux_circle_initialization(lux_circle):
    # Verificar tamaño mínimo
    assert lux_circle.minimumSize().width() >= 200
    assert lux_circle.minimumSize().height() >= 200
    
    # Verificar estado inicial
    assert not lux_circle._is_listening
    assert not lux_circle._is_speaking
    assert lux_circle._pulse_scale == 1.0
    assert lux_circle._opacity == 1.0

def test_listening_state(lux_circle):
    # Iniciar escucha
    lux_circle.start_listening()
    assert lux_circle._is_listening
    assert not lux_circle._is_speaking
    
    # Detener escucha
    lux_circle.stop_listening()
    assert not lux_circle._is_listening
    assert lux_circle._pulse_scale == 1.0

def test_speaking_state(lux_circle):
    # Iniciar habla
    lux_circle.start_speaking()
    assert lux_circle._is_speaking
    assert not lux_circle._is_listening
    
    # Detener habla
    lux_circle.stop_speaking()
    assert not lux_circle._is_speaking
    assert lux_circle._pulse_scale == 1.0

def test_animations(lux_circle):
    # Verificar que las animaciones están configuradas
    assert lux_circle._pulse_animation is not None
    assert lux_circle._opacity_animation is not None
    
    # Verificar propiedades de animación
    assert lux_circle._pulse_animation.duration() == 1000
    assert lux_circle._pulse_animation.loopCount() == -1

def test_rotation_timer(lux_circle):
    # Verificar que el timer está activo
    assert lux_circle._rotation_timer.isActive()
    
    # Verificar intervalo del timer
    assert lux_circle._rotation_timer.interval() == 50
    
    # Simular actualización de rotación
    initial_rotation = lux_circle._rotation
    lux_circle._update_rotation()
    assert lux_circle._rotation != initial_rotation 