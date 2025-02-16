# Crear el directorio principal y entrar en él
New-Item -ItemType Directory -Path "lux" -Force
Set-Location lux

# Crear y activar el entorno virtual
python -m venv venv

# Crear la estructura de carpetas
$folders = @(
    "app/core",
    "app/database",
    "app/services",
    "app/ui/components",
    "app/ui/styles",
    "app/utils",
    "tests/test_services",
    "docs",
    "resources/audio/notifications",
    "resources/images/icons",
    "resources/fonts"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Crear archivos base
$files = @(
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/core/__init__.py",
    "app/core/ai_manager.py",
    "app/core/voice_manager.py",
    "app/core/media_manager.py",
    "app/database/__init__.py",
    "app/database/models.py",
    "app/database/database.py",
    "app/services/__init__.py",
    "app/services/reminder_service.py",
    "app/services/task_service.py",
    "app/services/file_service.py",
    "app/services/search_service.py",
    "app/ui/__init__.py",
    "app/ui/main_window.py",
    "app/ui/components/__init__.py",
    "app/ui/components/lux_circle.py",
    "app/ui/components/media_player.py",
    "app/ui/components/task_view.py",
    "app/ui/styles/__init__.py",
    "app/ui/styles/main.qss",
    "app/utils/__init__.py",
    "app/utils/logger.py",
    "app/utils/helpers.py"
)

foreach ($file in $files) {
    New-Item -ItemType File -Path $file -Force
}

Write-Host "Estructura del proyecto creada exitosamente."
Write-Host "Para continuar:"
Write-Host "1. Activa el entorno virtual con: .\venv\Scripts\Activate"
Write-Host "2. Instala las dependencias con: pip install -r requirements.txt" 