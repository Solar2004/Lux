import logging
import importlib
import inspect
from typing import Dict, Any, Callable, Optional
from pathlib import Path
from datetime import datetime, timedelta
from ...core.function_registry import FunctionRegistry
from ..services.ai_service import AIService
from .safe_executor import SafeExecutor
from .log_manager import LogManager
from .security_analyzer import SecurityAnalyzer
from .test_manager import TestManager
from .dependency_manager import DependencyManager
from .feedback_manager import FeedbackManager
from .permission_manager import PermissionManager

logger = logging.getLogger('lux.functions')

class FunctionManager:
    def __init__(self, task_service=None, media_player=None, reminder_service=None, file_service=None):
        # Inicializar directorio de funciones
        self.functions: Dict[str, Callable] = {}
        self.functions_dir = Path("resources/functions")
        self.functions_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar servicios
        self.registry = FunctionRegistry()
        self.ai_service = AIService()
        self.safe_executor = SafeExecutor()
        self.log_manager = LogManager()
        self.security_analyzer = SecurityAnalyzer()
        self.test_manager = TestManager(self.ai_service)
        self.dependency_manager = DependencyManager()
        self.feedback_manager = FeedbackManager(self.registry)
        self.permission_manager = PermissionManager()
        
        # Cargar funciones existentes
        self._load_functions()
        logger.info(f"FunctionManager inicializado con {len(self.functions)} funciones")
    
    def _load_functions(self):
        """Carga todas las funciones desde el directorio"""
        try:
            for file in self.functions_dir.glob("*.py"):
                if file.name.startswith('_'):
                    continue
                    
                try:
                    module_name = file.stem
                    spec = importlib.util.spec_from_file_location(module_name, file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        for name, obj in inspect.getmembers(module):
                            if inspect.isfunction(obj) and not name.startswith('_'):
                                self.functions[name] = obj
                                logger.info(f"Función cargada: {name}")
                                
                except Exception as e:
                    logger.error(f"Error cargando función desde {file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error cargando funciones: {e}")
    
    def execute_function(self, request: str) -> Optional[str]:
        """
        Analiza y ejecuta una petición
        Args:
            request: Petición del usuario
        Returns:
            str: Resultado en lenguaje natural
        """
        try:
            start_time = datetime.now()
            
            # Analizar petición
            analysis = self.analyze_request(request)
            logger.info("Resultado del análisis:")
            logger.info(f"Tipo: {analysis['type']}")
            logger.info(f"Función: {analysis['function']}")
            logger.info(f"Info extra: {analysis.get('description', '')}")

            if analysis['type'] == "NO":
                return None
            
            if analysis['type'] == "NEW":
                result = self.create_new_function(
                    f"NEW - {analysis['function']}\n{analysis['description']}"
                )
                return self.ai_service.translate_result(result, request)
            
            # Ejecutar función existente de forma segura
            function_name = analysis['function']
            if function_name not in self.functions:
                logger.error(f"Función no encontrada: {function_name}")
                return None
            
            # Verificar si la función está habilitada
            if not self.registry.is_function_enabled(function_name):
                return f"La función {function_name} está deshabilitada temporalmente"
            
            try:
                # Ejecutar con timeout
                func = self.functions[function_name]
                result = self.safe_executor.execute(func)
                
                # Registrar ejecución
                self.log_manager.log_execution(function_name, result)
                
                if not result['success']:
                    error_msg = self.feedback_manager.get_error_message(
                        'execution_error',
                        name=function_name,
                        error=result['error']
                    )
                    logger.error(f"Error ejecutando {function_name}: {result['error']}")
                    self.registry.increment_error_count(function_name)
                    self.log_manager.log_error(function_name, result['error'], {
                        'request': request,
                        'type': result.get('type', 'unknown')
                    })
                    # Traducir error a lenguaje natural
                    natural_error = self.ai_service.translate_result(
                        f"{error_msg['message']}\n{error_msg['action']}", 
                        request
                    )
                    return natural_error
                
                # Registrar uso exitoso
                self.registry.update_usage(function_name, result['execution_time'])
                
                # Obtener resultado y contexto
                output = str(result['result'])
                function_info = self.registry.get_function_info(function_name)
                context = {
                    'request': request,
                    'function_name': function_name,
                    'description': function_info.get('description', ''),
                    'execution_time': result['execution_time']
                }
                
                # Traducir a lenguaje natural
                natural_response = self.ai_service.translate_result(
                    output,
                    str(context)  # Convertir contexto a string para el prompt
                )
                
                logger.info(f"Respuesta natural: {natural_response}")
                return natural_response
                
            except Exception as e:
                error_msg = self.feedback_manager.get_error_message(
                    'execution_error',
                    name=function_name,
                    error=str(e)
                )
                logger.error(f"Error ejecutando {function_name}: {e}")
                # Registrar error en archivo específico
                self._log_function_error(function_name, str(e), request)
                return f"{error_msg['message']}\n{error_msg['action']}"

        except Exception as e:
            logger.error(f"Error en execute_function: {e}")
            return None

    def _log_function_error(self, function_name: str, error: str, context: str):
        """Registra errores de función en archivo específico"""
        try:
            error_log = self.functions_dir / "errors" / f"{function_name}_errors.log"
            error_log.parent.mkdir(exist_ok=True)
            
            timestamp = datetime.now().isoformat()
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"TIMESTAMP: {timestamp}\n")
                f.write(f"CONTEXT: {context}\n")
                f.write(f"ERROR: {error}\n")
                
        except Exception as e:
            logger.error(f"Error logging function error: {e}")

    def create_new_function(self, ai_response: str) -> str:
        """Crea una nueva función basada en la respuesta de la IA"""
        try:
            # Extraer información
            lines = ai_response.split('\n')
            if not lines[0].startswith('NEW - '):
                return "Error: Formato inválido de respuesta"
            
            function_name = lines[0].replace('NEW - ', '').strip()
            description = lines[1].strip()
            
            logger.info("="*50)
            logger.info("CREACIÓN DE NUEVA FUNCIÓN")
            logger.info(f"Nombre: {function_name}")
            logger.info(f"Descripción: {description}")
            
            # Generar código
            code = self.ai_service.generate_code(function_name, description)
            if not code:
                return "Error: No se pudo generar el código"
            
            # Análisis de seguridad
            violations = self.security_analyzer.analyze_code(code, function_name)
            if violations:
                error_msg = "\n".join([f"- {v.type}: {v.message}" for v in violations])
                logger.error(f"Violaciones de seguridad encontradas:\n{error_msg}")
                return f"Error: El código no cumple con los requisitos de seguridad:\n{error_msg}"
            
            # Validar código
            if not self.ai_service.validate_code(code):
                return "Error: El código generado no cumple con los requisitos"
            
            # Probar y reparar si es necesario
            test_result = self.test_manager.test_function(function_name, code)
            if not test_result['success']:
                return f"Error: No se pudo crear la función después de varios intentos:\n{test_result['error']}"
                
            code = test_result['code']  # Usar código reparado si hubo cambios
            
            # Analizar y gestionar dependencias
            deps = self.dependency_manager.analyze_dependencies(code)
            
            if deps['conflicts']:
                return f"Error: Librerías no permitidas: {', '.join(deps['conflicts'])}"
                
            if deps['required']:
                if not self.dependency_manager.install_dependencies(deps['required']):
                    return "Error: No se pudieron instalar las dependencias requeridas"
                    
                # Guardar dependencias de la función
                self.dependency_manager.save_function_dependencies(
                    function_name, 
                    deps['required']
                )
            
            # Analizar permisos requeridos
            required_permissions = self.permission_manager.analyze_required_permissions(code)
            
            # Verificar permisos de alto riesgo
            high_risk_perms = [
                p for p in required_permissions 
                if p.risk_level in {'high', 'critical'}
            ]
            
            if high_risk_perms:
                perms_list = "\n".join([
                    f"- {p.name}: {p.description} (Nivel: {p.risk_level})"
                    for p in high_risk_perms
                ])
                return f"Error: La función requiere permisos de alto riesgo:\n{perms_list}"
            
            # Otorgar permisos necesarios
            self.permission_manager.grant_permissions(
                function_name,
                [p.name for p in required_permissions]
            )
            
            # Crear archivo
            file_path = self.functions_dir / f"{function_name}.py"
            logger.info(f"Archivo creado en: {file_path}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Cargar y registrar función
            try:
                spec = importlib.util.spec_from_file_location(function_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Buscar la función en el módulo
                    for name, obj in inspect.getmembers(module):
                        if inspect.isfunction(obj) and name == function_name:
                            # Registrar en el registry
                            self.registry.register(
                                name=name,
                                function=obj,
                                description=description,
                                file_path=str(file_path)
                            )
                            self.functions[name] = obj
                            
                            # Ejecutar la función para probarla
                            try:
                                result = obj()
                                logger.info(f"Prueba de función: {result}")
                                return f"Función {name} creada y probada exitosamente"
                            except Exception as e:
                                logger.error(f"Error en prueba de función: {e}")
                                return f"Función creada pero falló la prueba: {e}"
                            
            except Exception as e:
                logger.error(f"Error registrando función: {e}")
                return f"Error al registrar la función: {e}"
            
        except Exception as e:
            logger.error(f"Error creando función: {e}")
            return f"Error al crear la función: {e}"

    def _ensure_base_functions(self):
        """Asegura que las funciones base estén en el directorio"""
        try:
            # Crear directorio si no existe
            self.functions_dir.mkdir(parents=True, exist_ok=True)
            
            base_functions = {
                'obtener_hora.py': self._get_obtener_hora_code()
                # Ya no incluimos el snake game aquí
            }
            
            for filename, code in base_functions.items():
                file_path = self.functions_dir / filename
                if not file_path.exists():
                    # Escribir el código al archivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    logger.info(f"Función base creada: {filename}")
                    
                    # Cargar el módulo para registrarlo
                    try:
                        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Buscar la función en el módulo
                            for name, obj in inspect.getmembers(module):
                                if inspect.isfunction(obj) and not name.startswith('_'):
                                    # Registrar en el registry
                                    self.registry.register(
                                        name=name,
                                        function=obj,
                                        description=obj.__doc__,
                                        file_path=str(file_path)
                                    )
                                    logger.info(f"Función registrada: {name}")
                    except Exception as e:
                        logger.error(f"Error registrando función {filename}: {e}")
                    
        except Exception as e:
            logger.error(f"Error en _ensure_base_functions: {e}")
    
    def _get_obtener_hora_code(self):
        """Retorna el código de la función obtener_hora"""
        return '''
from datetime import datetime

def obtener_hora() -> str:
    """Obtiene la hora actual del sistema"""
    try:
        ahora = datetime.now()
        return f"Son las {ahora.strftime('%H:%M')}"
    except Exception as e:
        return f"Error al obtener la hora: {e}"
'''
    
    def get_available_functions(self) -> Dict[str, str]:
        """
        Retorna diccionario de funciones disponibles
        Returns:
            Dict[str, str]: {nombre_función: descripción}
        """
        return {
            name: func.__doc__ or "Sin descripción"
            for name, func in self.functions.items()
        }
    
    # Funciones base del sistema
    def _crear_tarea(self, descripcion: str) -> str:
        """Crea una nueva tarea en el sistema"""
        try:
            if not self.task_service:
                return "Servicio de tareas no disponible"
                
            task = self.task_service.create_task(
                user_id=1,  # TODO: Implementar sistema de usuarios
                title=descripcion,
                priority=0
            )
            
            logger.info(f"Tarea creada: {task.title}")
            return f"He creado la tarea: {task.title}"
            
        except Exception as e:
            logger.error(f"Error creando tarea: {e}")
            return "Hubo un error al crear la tarea"
    
    def _poner_musica(self, query: str) -> str:
        """Reproduce música según la búsqueda"""
        try:
            if not self.media_player:
                return "Reproductor de música no disponible"
                
            # TODO: Implementar búsqueda de música
            # Por ahora solo simulamos
            self.media_player.load_file("resources/audio/test.mp3")
            self.media_player.play_pause()
            
            return f"Reproduciendo música: {query}"
            
        except Exception as e:
            logger.error(f"Error reproduciendo música: {e}")
            return "Hubo un error al reproducir la música"
    
    def _crear_recordatorio(self, descripcion: str) -> str:
        """Crea un recordatorio en el sistema"""
        try:
            if not self.reminder_service:
                return "Servicio de recordatorios no disponible"
                
            # Crear recordatorio para dentro de 1 hora por defecto
            due_date = datetime.now() + timedelta(hours=1)
            
            reminder = self.reminder_service.create_reminder(
                user_id=1,  # TODO: Implementar sistema de usuarios
                title=descripcion,
                due_date=due_date
            )
            
            logger.info(f"Recordatorio creado: {reminder.title}")
            return f"He creado un recordatorio para dentro de 1 hora: {reminder.title}"
            
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            return "Hubo un error al crear el recordatorio"
    
    def _buscar_archivos(self, query: str) -> str:
        """Busca archivos en el sistema"""
        try:
            if not self.file_service:
                return "Servicio de archivos no disponible"
                
            files = self.file_service.list_files("documents")
            matching_files = [
                f for f in files 
                if query.lower() in f.name.lower()
            ]
            
            if matching_files:
                file_list = "\n".join([f"- {f.name}" for f in matching_files[:5]])
                return f"Encontré estos archivos:\n{file_list}"
            else:
                return f"No encontré archivos que coincidan con: {query}"
            
        except Exception as e:
            logger.error(f"Error buscando archivos: {e}")
            return "Hubo un error al buscar archivos" 

    def analyze_request(self, request: str) -> Dict[str, str]:
        """
        Analiza una petición para determinar qué acción tomar
        Args:
            request: Petición del usuario
        Returns:
            Dict con tipo de acción, nombre de función y descripción
        """
        try:
            logger.info("="*50)
            logger.info("ANÁLISIS DE SOLICITUD DE FUNCIÓN")
            logger.info(f"Texto a analizar: '{request}'")

            # Obtener funciones registradas
            registry = self.registry.list_functions()
            
            # Analizar con IA
            response = self.ai_service.analyze_request(request, registry)
            logger.info(f"Respuesta del análisis: {response}")
            
            # Procesar respuesta
            if response.startswith("YES - "):
                function_name = response.replace("YES - ", "").strip()
                return {
                    "type": "YES",
                    "function": function_name,
                    "extra_info": registry.get(function_name, {}).get("description", "")
                }
            elif response.startswith("NEW - "):
                parts = response.replace("NEW - ", "").split(" ", 1)
                if len(parts) == 2:
                    return {
                        "type": "NEW",
                        "function": parts[0].strip(),
                        "description": parts[1].strip()
                    }
            
            return {
                "type": "NO",
                "function": "",
                "description": ""
            }

        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            return {
                "type": "NO",
                "function": "",
                "description": str(e)
            } 