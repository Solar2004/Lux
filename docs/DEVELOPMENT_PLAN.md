# Plan de Desarrollo de Lux

## 1. Configuración Inicial del Proyecto

```bash
# Crear estructura del proyecto
mkdir lux
cd lux
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate

# Crear estructura de carpetas
mkdir -p app/{core,database,services,ui/{components,styles},utils}
mkdir -p tests/test_services
mkdir -p docs
mkdir -p resources/{audio/notifications,images/icons,fonts}

# Instalar dependencias básicas
pip install PyQt6 python-dotenv SQLAlchemy pytest google-cloud-speech google-cloud-texttospeech 
pip install yt-dlp google-api-python-client google-auth-oauthlib google-auth-httplib2
pip freeze > requirements.txt

# Crear archivos base
touch app/__init__.py app/main.py app/config.py
touch app/core/{__init__.py,ai_manager.py,voice_manager.py,media_manager.py}
touch app/database/{__init__.py,models.py,database.py}
touch app/services/{__init__.py,reminder_service.py,task_service.py,file_service.py,search_service.py}
touch app/ui/{__init__.py,main_window.py}
touch app/ui/components/{__init__.py,lux_circle.py,media_player.py,task_view.py}
touch app/ui/styles/{__init__.py,main.qss}
touch app/utils/{__init__.py,logger.py,helpers.py}
```

## 2. Configuración de la Base de Datos

```python:app/database/models.py
# Implementar modelos SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Definir modelos según la estructura en CONTEXT.md
class User(Base):
    __tablename__ = 'users'
    # ... definir columnas

class Task(Base):
    __tablename__ = 'tasks'
    # ... definir columnas

# ... definir resto de modelos
```

```python:app/database/database.py
# Implementar conexión y gestión de base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///lux.db"

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
```

## 3. Implementación del Núcleo (Core)

```python:app/core/ai_manager.py
# Implementación básica con Gemini
import requests
import json
import os
from typing import Optional, List

class AIManager:
    MODELS = [
        "gemini-pro",
        "gemini-1.0-pro-latest",
        "gemini-1.5-flash",
        "gemini-2.0-flash-thinking-exp-01-21",
        "gemini-2.0-flash"
    ]
    
    OR_MODELS = [
        "deepseek/deepseek-r1:free",
        "google/gemini-pro",
        "anthropic/claude-v1.3"
    ]

    def __init__(self, gemini_key: str, openrouter_key: str):
        self.gemini_key = gemini_key
        self.or_key = openrouter_key
        self.current_model = self.MODELS[0]
        self.using_openrouter = False

    def send_gemini_message(self, message: str) -> Optional[str]:
        """Envía mensaje a Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.current_model}:generateContent?key={self.gemini_key}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": message}]}]}
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                for candidate in result['candidates']:
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            if 'text' in part:
                                return part['text']
        except Exception as e:
            logger.error(f"Error en Gemini API: {e}")
        return None

    def send_openrouter_message(self, message: str) -> Optional[str]:
        """Envía mensaje a OpenRouter API"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.or_key}'
        }
        data = {
            "model": self.current_model,
            "messages": [{"role": "user", "content": message}]
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error en OpenRouter API: {e}")
        return None

    def send_message(self, message: str) -> Optional[str]:
        """Envía mensaje al modelo actual"""
        if self.using_openrouter:
            return self.send_openrouter_message(message)
        return self.send_gemini_message(message)

    def switch_model(self, model_name: str) -> bool:
        """Cambia el modelo actual"""
        if model_name in self.MODELS:
            self.current_model = model_name
            self.using_openrouter = False
            return True
        elif model_name in self.OR_MODELS:
            self.current_model = model_name
            self.using_openrouter = True
            return True
        return False

    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles"""
        return self.MODELS + self.OR_MODELS
```

```python:app/core/voice_manager.py
# Implementar TTS y STT
from google.cloud import texttospeech, speech
import logging

logger = logging.getLogger('lux')

class VoiceManager:
    def __init__(self):
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
            self.stt_client = speech.SpeechClient()
        except Exception as e:
            logger.error(f"Error al inicializar VoiceManager: {e}")
            raise
    
    def text_to_speech(self, text: str, output_file: str = "output.mp3") -> bool:
        """Convierte texto a voz y guarda en archivo"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-ES",
                name="es-ES-Standard-A"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
            return True
            
        except Exception as e:
            logger.error(f"Error en text_to_speech: {e}")
            return False
    
    def listen(self, duration: int = 5) -> str:
        """Escucha el micrófono y retorna texto"""
        try:
            # Configuración del reconocimiento
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="es-ES",
            )
            
            # Implementar la captura de audio aquí
            # Por ahora retornamos un placeholder
            return "Audio capturado"
            
        except Exception as e:
            logger.error(f"Error en listen: {e}")
            return ""
```

## 4. Implementación de Servicios

```python:app/services/reminder_service.py
# Implementar servicio de recordatorios
from datetime import datetime
from ..database.models import Reminder

class ReminderService:
    def __init__(self, db_session):
        self.session = db_session
    
    def create_reminder(self, user_id, title, description, due_date):
        # Implementar creación de recordatorios
        pass
    
    def get_active_reminders(self, user_id):
        # Obtener recordatorios activos
        pass
```

## 5. Implementación de la UI

```python:app/ui/components/lux_circle.py
# Implementar círculo principal de Lux
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

class LuxCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
    
    def paintEvent(self, event):
        # Implementar dibujo del círculo
        pass
```

## 6. Integración de APIs Externas

```python:app/core/ai_manager.py
# Implementar integración con Gemini y otras APIs
import google.generativeai as genai

class AIManager:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def process_command(self, text):
        # Procesar comandos con Gemini
        pass
```

## 7. Sistema de Logging

```python:app/utils/logger.py
# Implementar sistema de logging
import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='lux.log'
    )
    return logging.getLogger('lux')
```

## 8. Tests Unitarios

```python:tests/test_services/test_ai_manager.py
import pytest
from app.core.ai_manager import AIManager

def test_ai_manager_init():
    manager = AIManager("test_key", "test_or_key")
    assert manager.current_model == "gemini-pro"
    assert not manager.using_openrouter

def test_switch_model():
    manager = AIManager("test_key", "test_or_key")
    
    # Test Gemini model switch
    assert manager.switch_model("gemini-1.5-flash")
    assert manager.current_model == "gemini-1.5-flash"
    assert not manager.using_openrouter
    
    # Test OpenRouter model switch
    assert manager.switch_model("deepseek/deepseek-r1:free")
    assert manager.current_model == "deepseek/deepseek-r1:free"
    assert manager.using_openrouter

def test_get_available_models():
    manager = AIManager("test_key", "test_or_key")
    models = manager.get_available_models()
    assert len(models) == len(manager.MODELS) + len(manager.OR_MODELS)
```

```python:tests/test_services/test_reminder_service.py
import pytest
from datetime import datetime, timedelta
from app.services.reminder_service import ReminderService
from app.database.models import Reminder, User

def test_create_reminder(db_session):
    # Crear usuario de prueba
    user = User(username="test_user")
    db_session.add(user)
    db_session.commit()
    
    service = ReminderService(db_session)
    
    # Test crear recordatorio
    due_date = datetime.now() + timedelta(days=1)
    reminder = service.create_reminder(
        user_id=user.id,
        title="Test Reminder",
        description="Test Description",
        due_date=due_date
    )
    
    assert reminder.id is not None
    assert reminder.title == "Test Reminder"
    assert reminder.user_id == user.id

def test_get_active_reminders(db_session):
    # Crear usuario y recordatorios de prueba
    user = User(username="test_user")
    db_session.add(user)
    db_session.commit()
    
    service = ReminderService(db_session)
    
    # Crear recordatorios activos y completados
    due_date = datetime.now() + timedelta(days=1)
    reminder1 = service.create_reminder(user.id, "Active 1", "Test", due_date)
    reminder2 = service.create_reminder(user.id, "Active 2", "Test", due_date)
    reminder3 = service.create_reminder(user.id, "Completed", "Test", due_date)
    reminder3.completed = True
    db_session.commit()
    
    # Obtener recordatorios activos
    active_reminders = service.get_active_reminders(user.id)
    
    assert len(active_reminders) == 2
    assert all(not r.completed for r in active_reminders)
```

## 9. Aplicación Principal

```python:app/main.py
# Implementar punto de entrada de la aplicación
from PyQt6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .database.database import init_db
from .core.voice_manager import VoiceManager
from .core.ai_manager import AIManager

def main():
    app = QApplication([])
    db_session = init_db()
    voice_manager = VoiceManager()
    ai_manager = AIManager()
    
    window = MainWindow(db_session, voice_manager, ai_manager)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    main()
```

## Orden de Implementación Recomendado:

1. Configuración inicial del proyecto
2. Implementación de la base de datos
3. Implementación del sistema de logging
4. Implementación del núcleo de voz (TTS/STT)
5. Implementación del gestor de IA
6. Implementación de servicios básicos
7. Implementación de la UI básica
8. Integración de componentes
9. Tests unitarios
10. Refinamiento y optimización

Para cada tarea, asegurarse de:
- Escribir tests unitarios
- Documentar el código
- Manejar errores apropiadamente
- Seguir las mejores prácticas de Python
- Mantener la consistencia con el estilo de código del proyecto
