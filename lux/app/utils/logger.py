import logging
import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QTextEdit
from typing import Optional

class QtHandler(logging.Handler):
    def __init__(self, widget: QTextEdit):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    def emit(self, record):
        msg = self.format.format(record)
        self.widget.append(msg)
        # Auto-scroll al final
        self.widget.verticalScrollBar().setValue(
            self.widget.verticalScrollBar().maximum()
        )

def setup_logging():
    """Configura el sistema de logging"""
    # Limpiar handlers existentes
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Configurar logger raíz
    root_logger.setLevel(logging.INFO)
    
    # Crear directorio de logs si no existe
    log_dir = Path("resources/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo
    log_file = log_dir / f"lux_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Configurar logger específico de la app
    app_logger = logging.getLogger('lux')
    app_logger.handlers.clear()
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(console_handler)
    app_logger.addHandler(file_handler)
    
    # Configurar logger de funciones
    function_logger = logging.getLogger('lux.functions')
    function_logger.setLevel(logging.DEBUG)
    function_logger.propagate = False  # No propagar logs al logger padre

class LuxLogger:
    """Clase para manejar el widget de logs en la UI"""
    _instance = None
    _widget_handler = None
    
    @classmethod
    def setup(cls, widget: Optional[QTextEdit] = None):
        if widget and not cls._widget_handler:
            # Configurar handler para el widget
            cls._widget_handler = QtHandler(widget)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            cls._widget_handler.setFormatter(formatter)
            
            # Agregar handler solo al logger de la app
            app_logger = logging.getLogger('lux')
            app_logger.addHandler(cls._widget_handler)
            
            # Cargar logs previos si existen
            log_dir = Path("resources/logs")
            latest_log = sorted(log_dir.glob("lux_*.log"))[-1] if log_dir.exists() else None
            if latest_log:
                try:
                    with open(latest_log, 'r') as f:
                        widget.setPlainText(f.read())
                except:
                    pass
