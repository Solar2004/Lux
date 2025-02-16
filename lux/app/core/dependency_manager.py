import pkg_resources
import subprocess
import sys
import logging
from typing import Dict, List, Set, Optional
from pathlib import Path
import ast
import json

logger = logging.getLogger('lux.dependencies')

class DependencyManager:
    def __init__(self):
        self.dependencies_file = Path("resources/dependencies.json")
        self.installed_packages = self._get_installed_packages()
        self.allowed_packages = {
            'pygame': '2.5.0',
            'pillow': '10.0.0',
            'numpy': '1.24.0',
            'pandas': '2.0.0',
            'matplotlib': '3.7.0'
        }
        
    def analyze_dependencies(self, code: str) -> Dict[str, List[str]]:
        """
        Analiza las dependencias de un código
        Returns:
            Dict con dependencias requeridas y conflictos
        """
        try:
            tree = ast.parse(code)
            imports = set()
            
            # Extraer imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                        
            # Filtrar librerías estándar
            stdlib = set(sys.stdlib_module_names)
            external_deps = imports - stdlib
            
            # Verificar compatibilidad
            conflicts = []
            required = []
            
            for dep in external_deps:
                if dep in self.allowed_packages:
                    if dep not in self.installed_packages:
                        required.append(dep)
                    elif pkg_resources.parse_version(self.installed_packages[dep]) < \
                         pkg_resources.parse_version(self.allowed_packages[dep]):
                        required.append(dep)
                else:
                    conflicts.append(dep)
                    
            return {
                'required': required,
                'conflicts': conflicts
            }
            
        except Exception as e:
            logger.error(f"Error analizando dependencias: {e}")
            return {'required': [], 'conflicts': []}
            
    def install_dependencies(self, dependencies: List[str]) -> bool:
        """
        Instala las dependencias requeridas
        Args:
            dependencies: Lista de paquetes a instalar
        Returns:
            bool: True si la instalación fue exitosa
        """
        try:
            for package in dependencies:
                if package in self.allowed_packages:
                    version = self.allowed_packages[package]
                    spec = f"{package}=={version}"
                    
                    logger.info(f"Instalando {spec}")
                    subprocess.check_call([
                        sys.executable, 
                        "-m", 
                        "pip", 
                        "install", 
                        spec
                    ])
                    
            # Actualizar lista de paquetes instalados
            self.installed_packages = self._get_installed_packages()
            return True
            
        except Exception as e:
            logger.error(f"Error instalando dependencias: {e}")
            return False
            
    def _get_installed_packages(self) -> Dict[str, str]:
        """Obtiene lista de paquetes instalados con sus versiones"""
        try:
            installed = {}
            for package in pkg_resources.working_set:
                installed[package.key] = package.version
            return installed
        except:
            return {}
            
    def save_function_dependencies(self, function_name: str, dependencies: List[str]):
        """Guarda las dependencias de una función"""
        try:
            data = {}
            if self.dependencies_file.exists():
                with open(self.dependencies_file, 'r') as f:
                    data = json.load(f)
                    
            data[function_name] = {
                'dependencies': dependencies,
                'versions': {
                    dep: self.allowed_packages[dep]
                    for dep in dependencies
                    if dep in self.allowed_packages
                }
            }
            
            with open(self.dependencies_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando dependencias: {e}")
            
    def get_function_dependencies(self, function_name: str) -> Dict[str, str]:
        """Obtiene las dependencias de una función"""
        try:
            if self.dependencies_file.exists():
                with open(self.dependencies_file, 'r') as f:
                    data = json.load(f)
                    return data.get(function_name, {}).get('versions', {})
            return {}
        except:
            return {} 