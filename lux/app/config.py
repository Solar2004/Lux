import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Información de la aplicación
APP_NAME = os.getenv('APP_NAME', 'Lux')
APP_VERSION = os.getenv('APP_VERSION', '0.1.0')
APP_DOMAIN = os.getenv('APP_DOMAIN', 'http://localhost')

# Configuración de base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///lux.db')

# APIs
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'tu-api-key-aquí')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Logging
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'lux.log')

# Directorios
RESOURCES_DIR = os.getenv('RESOURCES_DIR', 'resources')
AUDIO_DIR = os.path.join(RESOURCES_DIR, 'audio')
IMAGES_DIR = os.path.join(RESOURCES_DIR, 'images')
FONTS_DIR = os.path.join(RESOURCES_DIR, 'fonts')

class Config:
    # ... otras configuraciones ...
    GEMINI_API_KEY = GEMINI_API_KEY
