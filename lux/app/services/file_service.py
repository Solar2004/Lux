import os
import shutil
import logging
from typing import Optional, List, Tuple
from pathlib import Path
import yt_dlp
from datetime import datetime

logger = logging.getLogger('lux')

class FileService:
    def __init__(self, base_dir: str = "resources"):
        """
        Inicializa el servicio de archivos.
        
        Args:
            base_dir: Directorio base para almacenar archivos
        """
        self.base_dir = Path(base_dir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Asegura que existan los directorios necesarios"""
        directories = [
            self.base_dir / "audio" / "notifications",
            self.base_dir / "audio" / "downloads",
            self.base_dir / "images" / "icons",
            self.base_dir / "documents",
            self.base_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_path: str, category: str, new_name: Optional[str] = None) -> Optional[Path]:
        """
        Guarda un archivo en la categoría especificada.
        
        Args:
            file_path: Ruta del archivo a guardar
            category: Categoría (audio, images, documents)
            new_name: Nuevo nombre para el archivo (opcional)
            
        Returns:
            Path: Ruta del archivo guardado o None si hay error
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return None
            
            # Determinar el nombre final del archivo
            if new_name:
                final_name = new_name + source_path.suffix
            else:
                final_name = source_path.name
            
            # Construir ruta de destino
            dest_dir = self.base_dir / category
            dest_path = dest_dir / final_name
            
            # Copiar archivo
            shutil.copy2(source_path, dest_path)
            logger.info(f"Archivo guardado: {dest_path}")
            return dest_path
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            return None
    
    def download_media(self, url: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Descarga contenido multimedia desde una URL.
        
        Args:
            url: URL del contenido a descargar
            output_path: Ruta de salida personalizada (opcional)
            
        Returns:
            str: Ruta del archivo descargado o None si hay error
        """
        try:
            if not output_path:
                output_path = str(self.base_dir / "audio" / "downloads" / f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            logger.info(f"Contenido descargado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error al descargar contenido: {e}")
            return None
    
    def list_files(self, category: str, extension: Optional[str] = None) -> List[Path]:
        """
        Lista archivos en una categoría específica.
        
        Args:
            category: Categoría a listar
            extension: Filtrar por extensión (opcional)
            
        Returns:
            List[Path]: Lista de archivos encontrados
        """
        try:
            directory = self.base_dir / category
            if not directory.exists():
                return []
            
            if extension:
                return list(directory.glob(f"*.{extension}"))
            return list(directory.glob("*.*"))
            
        except Exception as e:
            logger.error(f"Error al listar archivos: {e}")
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """
        Elimina un archivo.
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Archivo eliminado: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Tuple[float, datetime]]:
        """
        Obtiene información de un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Tuple[float, datetime]: (tamaño en MB, fecha de modificación)
        """
        try:
            path = Path(file_path)
            if path.exists():
                size_mb = path.stat().st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(path.stat().st_mtime)
                return (size_mb, mod_time)
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener información del archivo: {e}")
            return None
