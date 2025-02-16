import sys
import logging
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .database.database import init_db
from .core.voice_manager import VoiceManager
from .core.ai_manager import AIManager
from .utils.logger import setup_logging
from . import config

logger = logging.getLogger('lux')

def main():
    """Punto de entrada principal de la aplicación"""
    try:
        # Configurar logging
        setup_logging()
        
        # Inicializar base de datos desde cero
        db_session = init_db(force_reset=True)
        
        logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION}")
        
        # Inicializar servicios core
        ai_manager = AIManager()
        voice_manager = VoiceManager()  # Las dependencias se establecerán en MainWindow
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setApplicationName(config.APP_NAME)
        app.setApplicationVersion(config.APP_VERSION)
        
        # Crear y mostrar la ventana principal
        window = MainWindow(db_session, voice_manager, ai_manager)
        window.show()
        
        # Ejecutar loop principal
        exit_code = app.exec()
        
        # Limpieza
        window.cleanup()
        return exit_code
        
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
