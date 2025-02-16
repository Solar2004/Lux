import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime
from app.services.file_service import FileService

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def file_service(temp_dir):
    return FileService(base_dir=temp_dir)

def test_directory_creation(temp_dir):
    service = FileService(base_dir=temp_dir)
    
    # Verificar que se crearon los directorios necesarios
    assert (Path(temp_dir) / "audio" / "notifications").exists()
    assert (Path(temp_dir) / "audio" / "downloads").exists()
    assert (Path(temp_dir) / "images" / "icons").exists()
    assert (Path(temp_dir) / "documents").exists()
    assert (Path(temp_dir) / "temp").exists()

def test_save_file(file_service, temp_dir):
    # Crear archivo temporal para prueba
    test_file = Path(temp_dir) / "test.txt"
    test_file.write_text("Test content")
    
    # Guardar archivo
    saved_path = file_service.save_file(
        str(test_file),
        "documents",
        "new_name"
    )
    
    assert saved_path is not None
    assert saved_path.exists()
    assert saved_path.name == "new_name.txt"
    assert saved_path.read_text() == "Test content"

def test_list_files(file_service, temp_dir):
    # Crear algunos archivos de prueba
    (Path(temp_dir) / "documents" / "test1.txt").write_text("Test 1")
    (Path(temp_dir) / "documents" / "test2.txt").write_text("Test 2")
    (Path(temp_dir) / "documents" / "test.pdf").write_text("PDF")
    
    # Listar todos los archivos
    all_files = file_service.list_files("documents")
    assert len(all_files) == 3
    
    # Listar solo archivos txt
    txt_files = file_service.list_files("documents", "txt")
    assert len(txt_files) == 2

def test_delete_file(file_service, temp_dir):
    # Crear archivo para eliminar
    test_file = Path(temp_dir) / "documents" / "to_delete.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Delete me")
    
    # Eliminar archivo
    assert file_service.delete_file(str(test_file))
    assert not test_file.exists()
    
    # Intentar eliminar archivo inexistente
    assert not file_service.delete_file("nonexistent.txt")

def test_get_file_info(file_service, temp_dir):
    # Crear archivo para prueba
    test_file = Path(temp_dir) / "documents" / "info_test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Test content" * 1000)  # Crear archivo con contenido
    
    # Obtener información
    info = file_service.get_file_info(str(test_file))
    
    assert info is not None
    size_mb, mod_time = info
    
    assert size_mb > 0
    assert isinstance(mod_time, datetime)
    assert mod_time <= datetime.now()

def test_download_media(file_service, temp_dir):
    # Este test es más complicado porque requiere una URL real
    # Podríamos mock la función de descarga para pruebas
    pass 