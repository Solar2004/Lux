import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('lux.functions')

class FunctionRegistry:
    def __init__(self):
        self.registry_file = Path("resources/functions/registry.json")
        self.registry: Dict[str, Dict[str, Any]] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Carga el registro desde el archivo JSON"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
            else:
                self.registry_file.parent.mkdir(parents=True, exist_ok=True)
                self._save_registry()
        except Exception as e:
            logger.error(f"Error cargando registro: {e}")
            self.registry = {}
    
    def _save_registry(self):
        """Guarda el registro en el archivo JSON"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando registro: {e}")
    
    def register_function(self, 
                         name: str, 
                         file_path: str, 
                         description: str,
                         function_type: str,
                         extension: str = '.py') -> bool:
        """Registra una nueva función"""
        try:
            self.registry[name] = {
                'path': str(file_path),
                'description': description,
                'type': function_type,
                'extension': extension,
                'created_at': str(datetime.now())
            }
            self._save_registry()
            logger.info(f"Función registrada: {name}")
            return True
        except Exception as e:
            logger.error(f"Error registrando función: {e}")
            return False
    
    def get_function_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una función"""
        return self.registry.get(name)
    
    def remove_function(self, name: str) -> bool:
        """Elimina una función del registro"""
        try:
            if name in self.registry:
                del self.registry[name]
                self._save_registry()
                logger.info(f"Función eliminada del registro: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando función: {e}")
            return False
    
    def get_all_functions(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todas las funciones registradas"""
        return self.registry.copy() 