#!/bin/bash

# Crear el directorio principal y entrar en él
mkdir lux
cd lux

# Crear y activar el entorno virtual
python -m venv venv

# Crear la estructura de carpetas
mkdir -p app/{core,database,services,ui/{components,styles},utils}
mkdir -p tests/test_services
mkdir -p docs
mkdir -p resources/{audio/notifications,images/icons,fonts}

# Crear archivos base
touch app/__init__.py app/main.py app/config.py
touch app/core/{__init__.py,ai_manager.py,voice_manager.py,media_manager.py}
touch app/database/{__init__.py,models.py,database.py}
touch app/services/{__init__.py,reminder_service.py,task_service.py,file_service.py,search_service.py}
touch app/ui/{__init__.py,main_window.py}
touch app/ui/components/{__init__.py,lux_circle.py,media_player.py,task_view.py}
touch app/ui/styles/{__init__.py,main.qss}
touch app/utils/{__init__.py,logger.py,helpers.py} 