import logging
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from .. import config
from pathlib import Path
import importlib.util

logger = logging.getLogger('lux.functions')

class AIManager:
    def __init__(self):
        """
        Inicializa el gestor de IA.
        """
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini = genai.GenerativeModel('gemini-pro')
            self.function_manager = None  # Se establecerá después
            self.ai_service = None  # Se establecerá después
            logger.info("AIManager inicializado")
        except Exception as e:
            logger.error(f"Error al inicializar Gemini: {e}")
            self.gemini = None
    
    def set_function_manager(self, function_manager):
        """Establece el gestor de funciones y el servicio de IA"""
        self.function_manager = function_manager
        self.ai_service = function_manager.ai_service  # Obtener referencia al AIService
        logger.info("FunctionManager y AIService establecidos en AIManager")
    
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles"""
        models = ['gemini']
        if config.OPENROUTER_API_KEY:
            models.extend(['deepseek', 'claude', 'gpt4'])
        return models
    
    def chat(self, message: str) -> Optional[str]:
        """Procesa un mensaje y retorna una respuesta"""
        try:
            logger.info(f"Procesando mensaje: {message}")
            
            if self.gemini:
                # Agregar contexto al prompt
                prompt = f"""Eres Luxion, un asistente virtual amigable y servicial.
                Usuario: {message}
                Luxion:"""
                
                logger.debug(f"Enviando prompt a Gemini: {prompt}")
                response = self.gemini.generate_content(prompt)
                
                if response and response.text:
                    text = response.text.strip()
                    logger.info(f"Respuesta generada: {text}")
                    return text
                else:
                    logger.warning("No se generó respuesta")
            else:
                logger.warning("Gemini no está inicializado")
            
            # Respuesta de fallback
            return "Lo siento, no pude procesar tu mensaje correctamente."
                
        except Exception as e:
            logger.error(f"Error en chat: {e}")
            return "Disculpa, tuve un problema al procesar tu mensaje."
    
    def analyze_intent(self, message: str) -> Dict[str, any]:
        """
        Analiza la intención del mensaje del usuario.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Dict: Intención y entidades detectadas
        """
        # Simulación simple de detección de intención
        message = message.lower()
        
        if "recordatorio" in message or "recuérdame" in message:
            return {
                "intent": "set_reminder",
                "confidence": 0.9,
                "entities": {"task": message}
            }
        elif "tarea" in message or "añade" in message:
            return {
                "intent": "create_task",
                "confidence": 0.9,
                "entities": {"task": message}
            }
        elif "reproduce" in message or "pon" in message:
            return {
                "intent": "play_media",
                "confidence": 0.8,
                "entities": {"media": message}
            }
        else:
            return {
                "intent": "chat",
                "confidence": 0.6,
                "entities": {}
            }
    
    def get_task_suggestions(self, current_tasks: List[str]) -> List[str]:
        """
        Genera sugerencias de tareas basadas en las tareas actuales.
        
        Args:
            current_tasks: Lista de tareas actuales
            
        Returns:
            List[str]: Lista de sugerencias
        """
        # Simulación de sugerencias
        suggestions = [
            "Revisar correos pendientes",
            "Actualizar lista de compras",
            "Hacer ejercicio",
            "Leer un libro",
            "Organizar archivos"
        ]
        return suggestions[:3]  # Retorna las primeras 3 sugerencias
    
    def cleanup(self) -> None:
        """Limpia recursos"""
        # No hay recursos que limpiar en esta versión
        logger.info("AIManager limpiado")

    def analyze_task(self, text: str) -> Dict[str, any]:
        """
        Analiza el texto para detectar tareas y comandos
        Args:
            text: Texto a analizar
        Returns:
            Dict con tipo de comando y detalles
        """
        try:
            logger.info(f"Analizando texto: {text}")
            
            # Primero intentar con Gemini
            if self.gemini:
                prompt = f"""
                Analiza el siguiente texto y determina si es un comando o una conversación.
                Texto: "{text}"
                
                Responde en formato JSON con esta estructura:
                {{
                    "type": "task|reminder|music|chat",
                    "action": "create|play|search|respond",
                    "details": {{
                        "title": "título si aplica",
                        "description": "descripción si aplica",
                        "query": "búsqueda si aplica"
                    }}
                }}
                """
                
                response = self.gemini.generate_content(prompt)
                if response and response.text:
                    try:
                        import json
                        result = json.loads(response.text)
                        logger.info(f"Análisis completado: {result}")
                        return result
                    except:
                        logger.warning("No se pudo parsear respuesta JSON")
            
            # Fallback a análisis simple
            text = text.lower()
            if any(word in text for word in ["tarea", "recordar", "anotar"]):
                return {
                    "type": "task",
                    "action": "create",
                    "details": {
                        "title": text,
                        "description": ""
                    }
                }
            elif any(word in text for word in ["música", "canción", "reproducir", "pon"]):
                return {
                    "type": "music",
                    "action": "play",
                    "details": {
                        "query": text
                    }
                }
            else:
                return {
                    "type": "chat",
                    "action": "respond",
                    "details": {}
                }
                
        except Exception as e:
            logger.error(f"Error analizando texto: {e}")
            return {
                "type": "error",
                "action": "none",
                "details": {"error": str(e)}
            }

    def verify_function_request(self, text: str) -> dict:
        """
        Analiza si el texto pide una función existente o nueva
        Args:
            text: Texto a analizar
        Returns:
            dict: {
                "type": "YES|NO|NEW",
                "function_name": str,  # Solo si type es YES o NEW
                "extra_info": str,     # Información adicional si existe
                "description": str     # Descripción de la funcionalidad si type es NEW
            }
        """
        try:
            logger.info("="*50)
            logger.info("ANÁLISIS DE SOLICITUD DE FUNCIÓN")
            logger.info(f"Texto a analizar: '{text}'")
            
            prompt = f"""
            Analiza el siguiente texto y determina si pide ejecutar una función existente o crear una nueva.
            
            TEXTO: "{text}"
            
            FUNCIONES DISPONIBLES Y SUS USOS:
            - abrir_aplicacion: SOLO para abrir aplicaciones o sitios web
            - obtener_hora: SOLO para consultar la hora actual
            
            REGLAS DE ANÁLISIS:
            1. Si pide abrir una app/web -> "YES - abrir_aplicacion NOMBRE_APP"
            2. Si pide la hora -> "YES - obtener_hora"
            3. Si pide CUALQUIER OTRA COSA -> "NEW - nombre_descriptivo_y_unico descripción_detallada"
            
            REGLAS PARA NOMBRES DE FUNCIONES NUEVAS:
            - Usar formato snake_case (palabras separadas por guiones bajos)
            - Empezar con verbo que indique la acción (crear, buscar, jugar, etc)
            - Incluir palabras clave que describan la funcionalidad
            - Ser único y descriptivo
            
            EJEMPLOS DE NOMBRES:
            - "crear un juego de Snake" -> "crear_juego_snake_pygame"
            - "buscar en Wikipedia" -> "buscar_info_wikipedia"
            - "abrir YouTube" -> "YES - abrir_aplicacion youtube"
            - "crear juego de dinosaurio" -> "crear_juego_dino_chrome"
            - "buscar información sobre Minecraft" -> "NEW - buscar_info_internet función para buscar información en internet sobre un tema y retornar un resumen"
            
            IMPORTANTE: 
            - Si la acción NO coincide con una función existente, responde NEW
            - Para funciones nuevas, el nombre debe ser ÚNICO y DESCRIPTIVO
            """
            
            logger.debug("Enviando prompt a Gemini:")
            logger.debug(prompt)
            
            response = self.gemini.generate_content(prompt)
            if not response or not response.text:
                logger.warning("No se obtuvo respuesta del análisis")
                return {"type": "NO"}
            
            # Procesar respuesta
            result = response.text.strip()
            logger.info(f"Respuesta del análisis: {result}")
            
            if result.startswith("YES - "):
                parts = result[6:].split(" ", 1)
                analysis = {
                    "type": "YES",
                    "function_name": parts[0],
                    "extra_info": parts[1] if len(parts) > 1 else "",
                    "description": ""
                }
            elif result.startswith("NEW - "):
                parts = result[6:].split(" ", 1)
                analysis = {
                    "type": "NEW",
                    "function_name": parts[0],
                    "extra_info": "",
                    "description": parts[1] if len(parts) > 1 else ""
                }
            else:
                analysis = {"type": "NO"}
            
            logger.info("Resultado del análisis:")
            logger.info(f"Tipo: {analysis['type']}")
            if analysis['type'] != 'NO':
                logger.info(f"Función: {analysis.get('function_name', 'N/A')}")
                logger.info(f"Info extra: {analysis.get('extra_info', 'N/A')}")
                logger.info(f"Descripción: {analysis.get('description', 'N/A')}")
            logger.info("="*50)
            
            return analysis
            
        except Exception as e:
            logger.error("="*50)
            logger.error(f"Error en verify_function_request: {e}")
            logger.error(f"Texto que causó el error: {text}")
            logger.error("="*50)
            return {"type": "NO"}

    def _ensure_unique_function_name(self, base_name: str) -> str:
        """
        Asegura que el nombre de la función sea único
        Args:
            base_name: Nombre base de la función
        Returns:
            str: Nombre único para la función
        """
        try:
            # Obtener lista de funciones existentes
            existing_functions = list(self.function_manager.functions.keys())
            
            # Si el nombre no existe, retornarlo tal cual
            if base_name not in existing_functions:
                return base_name
            
            # Si existe, agregar un número al final
            counter = 1
            while f"{base_name}_{counter}" in existing_functions:
                counter += 1
            
            unique_name = f"{base_name}_{counter}"
            logger.info(f"Nombre de función ajustado para ser único: {unique_name}")
            return unique_name
            
        except Exception as e:
            logger.error(f"Error al generar nombre único: {e}")
            return base_name

    def create_new_function(self, name: str, description: str) -> Dict[str, Any]:
        try:
            logger.info("="*50)
            logger.info("CREACIÓN DE NUEVA FUNCIÓN")
            
            # Asegurar nombre único
            unique_name = self._ensure_unique_function_name(name)
            if unique_name != name:
                logger.info(f"Nombre original: {name}")
                logger.info(f"Nombre único: {unique_name}")
                name = unique_name
            
            logger.info(f"Nombre: {name}")
            logger.info(f"Descripción: {description}")
            
            # Determinar tipo y extensión
            function_type = self._determine_function_type(description)
            extension = self._determine_file_extension(description)
            
            # Determinar ubicación del archivo
            if function_type == "game":
                file_path = Path.home() / "Desktop" / f"{name}{extension}"
            else:
                file_path = Path("resources/functions") / f"{name}{extension}"
            
            # Generar y guardar código
            code = self._generate_code(name, description, function_type)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            logger.info(f"Archivo creado en: {file_path}")
            
            # Registrar la función
            self.function_manager.registry.register(
                name=name,
                function=None,  # La función se cargará después
                description=description,
                file_path=str(file_path),
                function_type=function_type
            )
            
            if function_type != "game" and extension == '.py':
                # Solo registrar en el function_manager si es Python y no es juego
                try:
                    spec = importlib.util.spec_from_file_location(name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        func = getattr(module, name)
                        self.function_manager.functions[name] = func
                except Exception as e:
                    logger.error(f"Error registrando función: {e}")
                    return {"success": False, "error": str(e)}
            
            return {
                "success": True,
                "function": name,
                "code": code,
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error creando función: {e}")
            return {"success": False, "error": str(e)}

    def _generate_code(self, name: str, description: str, function_type: str) -> str:
        """Genera el código para una función basada en su tipo"""
        try:
            # Usar ai_service para generar el código real
            return self.ai_service.generate_code(name, description)
        except Exception as e:
            logger.error(f"Error generando código: {e}")
            return None

    def _determine_function_type(self, description: str) -> str:
        """Determina el tipo de función basado en la descripción"""
        description = description.lower()
        if any(word in description for word in ["juego", "game", "pygame"]):
            return "game"
        elif any(word in description for word in ["buscar", "internet", "wikipedia"]):
            return "web_search"
        elif any(word in description for word in ["archivo", "file", "crear", "escribir"]):
            return "file_operation"
        return "default"

    def _determine_file_extension(self, description: str) -> str:
        """Determina la extensión del archivo basado en la descripción"""
        description = description.lower()
        if "javascript" in description or "js" in description:
            return ".js"
        elif "batch" in description or "bat" in description:
            return ".bat"
        elif "html" in description:
            return ".html"
        elif "css" in description:
            return ".css"
        else:
            return ".py"
