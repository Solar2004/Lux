import threading
import signal
from typing import Optional, Any, Dict
import logging
from pathlib import Path
import tempfile
import os
import sys
import platform

logger = logging.getLogger('lux.executor')

class TimeoutError(Exception):
    pass

class ResourceLimitError(Exception):
    pass

class SafeExecutor:
    def __init__(self, max_time: int = 30, max_memory: int = 100 * 1024 * 1024):  # 100MB default
        self.max_time = max_time  # segundos
        self.max_memory = max_memory  # bytes
        self.result = None
        self.error = None
        self.is_windows = platform.system() == 'Windows'
        
    def _timeout_handler(self, signum, frame):
        raise TimeoutError("Función excedió el tiempo límite")
        
    def _limit_resources(self):
        """Establece límites de recursos para la ejecución"""
        if not self.is_windows:
            # En sistemas Unix/Linux
            import resource
            # Límite de memoria
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
            # Límite de CPU
            resource.setrlimit(resource.RLIMIT_CPU, (self.max_time, self.max_time))
            # Límite de procesos
            resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
            # Límite de archivos
            resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
        else:
            # En Windows no podemos usar resource, así que solo usamos el timeout
            pass
        
    def execute(self, function: Any, *args, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una función de forma segura con límites de recursos
        Returns:
            Dict con resultado o error y métricas
        """
        try:
            # Crear directorio temporal para la ejecución
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)  # Cambiar al directorio temporal
                
                # Configurar timeout
                if not self.is_windows:
                    signal.signal(signal.SIGALRM, self._timeout_handler)
                    signal.alarm(self.max_time)
                
                # Ejecutar en thread separado con límites
                def run_function():
                    try:
                        self._limit_resources()
                        self.result = function(*args, **kwargs)
                    except Exception as e:
                        self.error = str(e)
                
                thread = threading.Thread(target=run_function)
                thread.start()
                thread.join(timeout=self.max_time)
                
                # Desactivar alarma en sistemas Unix
                if not self.is_windows:
                    signal.alarm(0)
                
                if thread.is_alive():
                    raise TimeoutError("Función excedió el tiempo límite")
                
                if self.error:
                    raise Exception(self.error)
                
                return {
                    'success': True,
                    'result': self.result,
                    'execution_time': self.max_time,  # Aproximado en Windows
                    'memory_used': 0  # No podemos medir en Windows fácilmente
                }
                
        except TimeoutError as e:
            return {
                'success': False,
                'error': str(e),
                'type': 'timeout'
            }
        except ResourceLimitError as e:
            return {
                'success': False,
                'error': str(e),
                'type': 'resource_limit'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'type': 'runtime'
            }
        finally:
            # Restaurar directorio de trabajo
            os.chdir(str(Path.cwd().parent))
            # Restaurar señales en sistemas Unix
            if not self.is_windows:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, signal.SIG_DFL) 