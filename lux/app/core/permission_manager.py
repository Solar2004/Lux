import logging
from typing import Dict, List, Set, Optional
from pathlib import Path
import json

logger = logging.getLogger('lux.permissions')

class Permission:
    def __init__(self, name: str, description: str, risk_level: str = 'low'):
        self.name = name
        self.description = description
        self.risk_level = risk_level

class PermissionManager:
    def __init__(self):
        self.permissions_file = Path("resources/permissions.json")
        self.function_permissions: Dict[str, Set[str]] = {}
        
        # Definir permisos disponibles
        self.available_permissions = {
            'file_read': Permission(
                'file_read',
                'Leer archivos del sistema',
                'medium'
            ),
            'file_write': Permission(
                'file_write',
                'Escribir archivos en el sistema',
                'high'
            ),
            'network_access': Permission(
                'network_access',
                'Acceder a la red',
                'high'
            ),
            'system_exec': Permission(
                'system_exec',
                'Ejecutar comandos del sistema',
                'critical'
            ),
            'gui_access': Permission(
                'gui_access',
                'Crear interfaces gráficas',
                'low'
            ),
            'input_device': Permission(
                'input_device',
                'Acceder a dispositivos de entrada',
                'medium'
            )
        }
        
        self._load_permissions()
        
    def _load_permissions(self):
        """Carga los permisos desde el archivo"""
        try:
            if self.permissions_file.exists():
                with open(self.permissions_file, 'r') as f:
                    data = json.load(f)
                    self.function_permissions = {
                        func: set(perms)
                        for func, perms in data.items()
                    }
            else:
                self._save_permissions()
                
        except Exception as e:
            logger.error(f"Error cargando permisos: {e}")
            
    def _save_permissions(self):
        """Guarda los permisos en el archivo"""
        try:
            data = {
                func: list(perms)
                for func, perms in self.function_permissions.items()
            }
            
            with open(self.permissions_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando permisos: {e}")
            
    def analyze_required_permissions(self, code: str) -> List[Permission]:
        """Analiza el código para determinar los permisos necesarios"""
        required_permissions = set()
        
        # Buscar operaciones que requieren permisos
        if 'open(' in code or 'Path(' in code:
            if 'write' in code or 'create' in code:
                required_permissions.add('file_write')
            else:
                required_permissions.add('file_read')
                
        if 'socket' in code or 'urllib' in code or 'requests' in code:
            required_permissions.add('network_access')
            
        if 'subprocess' in code or 'os.system' in code:
            required_permissions.add('system_exec')
            
        if 'pygame' in code or 'tkinter' in code:
            required_permissions.add('gui_access')
            
        if 'input(' in code or 'keyboard' in code:
            required_permissions.add('input_device')
            
        return [
            self.available_permissions[perm]
            for perm in required_permissions
            if perm in self.available_permissions
        ]
        
    def grant_permissions(self, function_name: str, permissions: List[str]) -> bool:
        """Otorga permisos a una función"""
        try:
            # Validar que los permisos existan
            invalid_perms = [p for p in permissions if p not in self.available_permissions]
            if invalid_perms:
                logger.error(f"Permisos inválidos: {invalid_perms}")
                return False
                
            self.function_permissions[function_name] = set(permissions)
            self._save_permissions()
            return True
            
        except Exception as e:
            logger.error(f"Error otorgando permisos: {e}")
            return False
            
    def check_permissions(self, function_name: str, required_permissions: List[str]) -> bool:
        """Verifica si una función tiene los permisos necesarios"""
        if function_name not in self.function_permissions:
            return False
            
        granted_permissions = self.function_permissions[function_name]
        return all(perm in granted_permissions for perm in required_permissions)
        
    def get_function_permissions(self, function_name: str) -> List[Permission]:
        """Obtiene los permisos de una función"""
        if function_name not in self.function_permissions:
            return []
            
        return [
            self.available_permissions[perm]
            for perm in self.function_permissions[function_name]
            if perm in self.available_permissions
        ]
        
    def revoke_permissions(self, function_name: str, permissions: Optional[List[str]] = None):
        """Revoca permisos de una función"""
        try:
            if permissions is None:
                # Revocar todos los permisos
                self.function_permissions.pop(function_name, None)
            else:
                # Revocar permisos específicos
                if function_name in self.function_permissions:
                    self.function_permissions[function_name] -= set(permissions)
                    
            self._save_permissions()
            
        except Exception as e:
            logger.error(f"Error revocando permisos: {e}") 