import json
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import inspect

logger = logging.getLogger('lux.registry')

class FunctionRegistry:
    """Registry for managing function registrations and metadata"""
    
    def __init__(self):
        self.registry_file = Path("resources/functions/registry.json")
        self.functions: Dict[str, Dict[str, Any]] = {}
        self._load_registry()
        
    def _load_registry(self):
        """Carga o crea el registro de funciones"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.functions = json.load(f)
            else:
                self._save_registry()
                
        except Exception as e:
            logger.error(f"Error cargando registry: {e}")
            self.functions = {}
            
    def _save_registry(self):
        """Guarda el registro en JSON con formato consistente"""
        try:
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Asegurar formato consistente
            registry_data = {}
            for name, data in self.functions.items():
                registry_data[name] = {
                    'name': data.get('name', name),
                    'description': data.get('description', 'No description'),
                    'file_path': data.get('file_path', ''),
                    'enabled': data.get('enabled', True),
                    'created_at': data.get('created_at', datetime.now().isoformat()),
                    'last_used': data.get('last_used', None),
                    'usage_count': data.get('usage_count', 0),
                    'average_execution_time': data.get('average_execution_time', 0),
                    'tags': data.get('tags', []),
                    'version': data.get('version', '1.0.0')
                }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando registry: {e}")
            
    def register(self, name: str, function: Any, description: Optional[str] = None, 
                file_path: Optional[str] = None, tags: Optional[list] = None,
                function_type: Optional[str] = None) -> bool:
        """
        Registra o actualiza una función
        Args:
            name: Nombre de la función
            function: Objeto de la función
            description: Descripción de la función
            file_path: Ruta al archivo
            tags: Lista de etiquetas
            function_type: Tipo de función (juego, utilidad, etc.)
        """
        try:
            now = datetime.now().isoformat()
            
            self.functions[name] = {
                'name': name,
                'description': description or function.__doc__ or 'Sin descripción',
                'file_path': str(file_path) if file_path else None,
                'enabled': True,
                'created_at': now,
                'updated_at': now,
                'tags': tags or [],
                'function_type': function_type or 'utility',
                'usage_count': 0,
                'error_count': 0,
                'success_rate': 100,
                'average_execution_time': 0
            }
            
            self._save_registry()
            return True
            
        except Exception as e:
            logger.error(f"Error registrando función: {e}")
            return False

    def _analyze_system_requirements(self, function) -> Dict[str, Any]:
        """Analiza los requisitos del sistema para una función"""
        try:
            source = inspect.getsource(function)
            reqs = {
                'libraries': [],
                'min_python_version': '3.6',
                'gui_required': False,
                'estimated_memory': 'low',
                'file_access': False
            }
            
            # Analizar imports
            for line in source.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    lib = line.split()[1].split('.')[0]
                    reqs['libraries'].append(lib)
            
            # Detectar uso de GUI
            if 'pygame' in reqs['libraries'] or 'tkinter' in reqs['libraries']:
                reqs['gui_required'] = True
                reqs['estimated_memory'] = 'medium'
            
            # Detectar acceso a archivos
            if 'open(' in source or 'Path' in source:
                reqs['file_access'] = True
            
            return reqs
            
        except Exception as e:
            logger.error(f"Error analizando requisitos: {e}")
            return {}

    def _generate_usage_examples(self, name: str, description: str) -> List[Dict[str, str]]:
        """Genera ejemplos de uso para una función"""
        try:
            examples = []
            
            # Ejemplo básico
            examples.append({
                'description': 'Uso básico',
                'code': f'result = {name}()',
                'expected_output': 'Mensaje de éxito'
            })
            
            # TODO: Usar IA para generar ejemplos más específicos
            # basados en la descripción de la función
            
            return examples
            
        except Exception as e:
            logger.error(f"Error generando ejemplos: {e}")
            return []

    def _backup_function(self, name: str):
        """Crea un backup de una función antes de actualizarla"""
        try:
            if name not in self.functions:
                return
            
            backup_dir = Path("resources/functions/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear backup del archivo
            func_info = self.functions[name]
            if func_info.get('file_path'):
                source_file = Path(func_info['file_path'])
                if source_file.exists():
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = backup_dir / f"{name}_{timestamp}.py"
                    
                    with open(source_file, 'r') as src, open(backup_file, 'w') as dst:
                        dst.write(src.read())
                    
                    # Registrar backup
                    self.functions[name].setdefault('backup_history', []).append({
                        'timestamp': timestamp,
                        'version': func_info.get('version', '1.0.0'),
                        'file_path': str(backup_file)
                    })
                
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            
    def update_usage(self, name: str, execution_time: float):
        """Actualiza estadísticas de uso de una función"""
        if name in self.functions:
            now = datetime.now().isoformat()
            current = self.functions[name]
            
            # Actualizar estadísticas
            count = current.get('usage_count', 0) + 1
            avg_time = current.get('average_execution_time', 0)
            new_avg = ((avg_time * (count - 1)) + execution_time) / count
            
            self.functions[name].update({
                'last_used': now,
                'usage_count': count,
                'average_execution_time': new_avg
            })
            
            self._save_registry()
            
    def get_function_info(self, name: str) -> Dict[str, Any]:
        """Obtiene información detallada de una función"""
        return self.functions.get(name, {})
        
    def get_description(self, name):
        """Get the description of a registered function"""
        return self.functions.get(name, {}).get('description')
        
    def list_functions(self) -> Dict[str, Dict[str, Any]]:
        """Lista todas las funciones registradas"""
        return self.functions
        
    def search_functions(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Busca funciones por nombre o descripción"""
        query = query.lower()
        return {
            name: data for name, data in self.functions.items()
            if query in name.lower() or query in data.get('description', '').lower()
        }
        
    def disable_function(self, name):
        """Disable a function"""
        if name in self.functions:
            self.functions[name]['enabled'] = False
            self._save_registry()
            
    def enable_function(self, name):
        """Enable a function"""
        if name in self.functions:
            self.functions[name]['enabled'] = True
            self._save_registry()

    def is_function_enabled(self, name: str) -> bool:
        """Verifica si una función está habilitada"""
        return self.functions.get(name, {}).get('enabled', False)

    def get_function_stats(self, name: str) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de una función"""
        if name not in self.functions:
            return {}
        
        func = self.functions[name]
        return {
            'usage_count': func.get('usage_count', 0),
            'average_execution_time': func.get('average_execution_time', 0),
            'last_used': func.get('last_used'),
            'error_count': func.get('error_count', 0),
            'success_rate': func.get('success_rate', 100)
        }

    def increment_error_count(self, name: str):
        """Incrementa el contador de errores de una función"""
        if name in self.functions:
            current = self.functions[name]
            error_count = current.get('error_count', 0) + 1
            total_uses = current.get('usage_count', 0)
            
            if total_uses > 0:
                success_rate = ((total_uses - error_count) / total_uses) * 100
            else:
                success_rate = 0
                
            self.functions[name].update({
                'error_count': error_count,
                'success_rate': success_rate
            })
            self._save_registry() 