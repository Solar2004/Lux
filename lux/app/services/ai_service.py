import logging
from typing import Optional, Dict, List, Any
import google.generativeai as genai
import requests
import json
import time
from datetime import datetime
from .. import config

logger = logging.getLogger('lux.ai')

class AIService:
    def __init__(self):
        self.models = {
            'gemini': self._init_gemini(),
            'deepseek': {
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'model': 'deepseek-ai/deepseek-coder-33b-instruct',
            },
            'claude': {
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'model': 'anthropic/claude-3-opus',
            },
            'gpt4': {
                'url': 'https://openrouter.ai/api/v1/chat/completions',
                'model': 'openai/gpt-4-turbo',
            }
        }
        self.openrouter_headers = {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": config.APP_DOMAIN,
        }
        logger.info("AIService inicializado")

    def _init_gemini(self):
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini inicializado")
            return model
        except Exception as e:
            logger.error(f"Error al inicializar Gemini: {e}")
            return None

    def chat_with_model(self, message: str, model: str = 'gemini') -> Optional[str]:
        try:
            if model == 'gemini':
                return self._chat_with_gemini(message)
            else:
                return self._chat_with_openrouter(message, model)
        except Exception as e:
            logger.error(f"Error en chat_with_model ({model}): {e}")
            return None

    def _chat_with_gemini(self, message: str) -> Optional[str]:
        if not self.models['gemini']:
            return "Gemini no está disponible"
        try:
            response = self.models['gemini'].generate_content(message)
            return response.text
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return None

    def _chat_with_openrouter(self, message: str, model_key: str) -> Optional[str]:
        try:
            model_info = self.models.get(model_key)
            if not model_info:
                return f"Modelo {model_key} no encontrado"

            payload = {
                "model": model_info['model'],
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7
            }

            response = requests.post(
                model_info['url'],
                headers=self.openrouter_headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Error en OpenRouter: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error en OpenRouter ({model_key}): {e}")
            return None

    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles"""
        return list(self.models.keys())

    def is_model_available(self, model: str) -> bool:
        """Verifica si un modelo está disponible"""
        if model == 'gemini':
            return self.models['gemini'] is not None
        return model in self.models

    def code_assistance(self, prompt: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Utiliza OpenRouter para tareas de programación complejas.
        
        Args:
            prompt: Descripción de la tarea de programación
            context: Contexto adicional (código existente, lenguaje, etc.)
            
        Returns:
            Dict: Respuesta estructurada con código y explicación
        """
        try:
            messages = [{"role": "system", "content": """
                Eres un experto programador. Proporciona soluciones de código claras y bien documentadas.
                Incluye explicaciones detalladas y ejemplos de uso cuando sea relevante.
                """}]
            
            # Añadir contexto si existe
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Contexto: {json.dumps(context)}"
                })
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "anthropic/claude-2",  # Modelo optimizado para código
                "messages": messages,
                "temperature": 0.3,  # Más determinista para código
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.openrouter_url,
                headers=self.openrouter_headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "code": self._extract_code(result["choices"][0]["message"]["content"]),
                    "explanation": self._extract_explanation(result["choices"][0]["message"]["content"])
                }
            else:
                logger.error(f"Error en OpenRouter: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error en code_assistance: {e}")
            return None
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analiza una descripción de tarea para extraer información relevante.
        
        Args:
            task_description: Descripción de la tarea
            
        Returns:
            Dict: Información estructurada de la tarea
        """
        try:
            prompt = f"""
            Analiza la siguiente descripción de tarea y extrae información clave:
            "{task_description}"
            
            Proporciona:
            1. Prioridad sugerida (0-2)
            2. Fecha límite si se menciona
            3. Categoría de la tarea
            4. Subtareas si las hay
            """
            
            response = self.models['gemini'].generate_content(prompt)
            # Procesar la respuesta para extraer la información estructurada
            # (Implementar lógica de parsing según el formato de respuesta)
            
            return {
                "priority": 1,  # Valor por defecto
                "due_date": None,
                "category": "general",
                "subtasks": []
            }
            
        except Exception as e:
            logger.error(f"Error en analyze_task: {e}")
            return {}
    
    def generate_task_suggestions(self, user_tasks: List[Dict]) -> List[str]:
        """
        Genera sugerencias de tareas basadas en el historial del usuario.
        
        Args:
            user_tasks: Lista de tareas del usuario
            
        Returns:
            List[str]: Lista de sugerencias de tareas
        """
        try:
            task_history = "\n".join([
                f"- {task['title']} ({task['category']})"
                for task in user_tasks[-5:]  # Últimas 5 tareas
            ])
            
            prompt = f"""
            Basado en estas tareas recientes:
            {task_history}
            
            Sugiere 3 nuevas tareas que podrían ser relevantes.
            Considera patrones, categorías y prioridades similares.
            """
            
            response = self.models['gemini'].generate_content(prompt)
            suggestions = response.text.strip().split("\n")
            return [s.strip("- ") for s in suggestions if s.strip()]
            
        except Exception as e:
            logger.error(f"Error en generate_task_suggestions: {e}")
            return []
    
    def _extract_code(self, content: str) -> str:
        """Extrae bloques de código de la respuesta"""
        # Implementar extracción de código entre marcadores ```
        return content
    
    def _extract_explanation(self, content: str) -> str:
        """Extrae la explicación del código"""
        # Implementar extracción de texto explicativo
        return content
    
    def rate_limit_check(self) -> bool:
        """Verifica límites de tasa de la API"""
        # Implementar lógica de rate limiting
        return True

    def analyze_request(self, request: str, registry: Dict[str, Any]) -> str:
        """
        Analiza una petición para determinar si existe una función o se debe crear una nueva
        Args:
            request: Petición del usuario
            registry: Diccionario con las funciones registradas
        Returns:
            str: Formato "YES - función" | "NEW - función descripción" | "NO"
        """
        try:
            # Formatear registry para el prompt
            functions_list = "\n".join([
                f"- {name}: {info.get('description', 'Sin descripción')}"
                for name, info in registry.items()
            ])

            prompt = f"""
            ANALIZA ESTA PETICIÓN Y DETERMINA SI HAY UNA FUNCIÓN EXISTENTE QUE LA CUMPLA
            O SI SE NECESITA CREAR UNA NUEVA.

            FUNCIONES DISPONIBLES:
            {functions_list}

            PETICIÓN DEL USUARIO:
            {request}

            REGLAS:
            1. Si existe una función que cumpla la petición, responde: "YES - nombre_funcion"
            2. Si no existe y se necesita crear una, responde: "NEW - nombre_funcion descripción"
            3. Si no se pide una función o no requiere acción, responde: "NO"

            IMPORTANTE:
            - Los nombres de funciones deben ser descriptivos y en snake_case
            - No sugerir funciones que requieran APIs externas o keys
            - Solo usar librerías permitidas (pygame, pillow, numpy, etc.)
            - La descripción debe ser clara y específica

            Responde SOLO con uno de los 3 formatos mencionados, sin explicaciones adicionales.
            """

            response = self.models['gemini'].generate_content(prompt)
            if response.text:
                return response.text.strip()
            return "NO"

        except Exception as e:
            logger.error(f"Error en análisis de petición: {e}")
            return "NO"

    def generate_code(self, function_name: str, description: str) -> Optional[str]:
        """
        Genera código Python para una nueva función
        """
        try:
            prompt = f"""
            GENERA EL CÓDIGO COMPLETO PARA ESTA FUNCIÓN:

            NOMBRE: {function_name}
            DESCRIPCIÓN: {description}

            REGLAS IMPORTANTES:
            1. USAR PyQt6 para crear una ventana separada
            2. La función debe ser autocontenida (toda la UI en la misma ventana)
            3. Manejar TODOS los errores posibles
            4. Documentar el código claramente
            5. Retornar un string con el resultado al cerrar

            LIBRERÍAS PERMITIDAS:
            - GUI: PyQt6
            - Audio: pygame, pyttsx3, SpeechRecognition
            - Datos: numpy, pandas
            - Sistema: os, sys, pathlib, datetime, json
            - NO USAR: requests, selenium, etc.

            EJEMPLO DE FORMATO:
            ```python
            from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
            import sys

            def {function_name}() -> str:
                '''
                {description}
                Returns:
                    str: Mensaje con el resultado
                '''
                try:
                    class MainWindow(QMainWindow):
                        def __init__(self):
                            super().__init__()
                            self.setWindowTitle("{function_name}")
                            self.setGeometry(100, 100, 400, 300)
                            
                            # Crear widget central y layout
                            central_widget = QWidget()
                            self.setCentralWidget(central_widget)
                            layout = QVBoxLayout(central_widget)
                            
                            # Agregar widgets aquí...
                            
                            self.show()
                
                    # Crear aplicación
                    app = QApplication(sys.argv)
                    window = MainWindow()
                    app.exec()
                    
                    return "Operación completada exitosamente"
                    
                except Exception as e:
                    return f"Error: {{e}}"
            ```

            IMPORTANTE: 
            - La ventana debe ser independiente y funcional
            - Incluir todos los imports necesarios
            - Manejar el cierre de la ventana
            - NO incluir el template en el archivo

            Responde SOLO con el código Python, sin explicaciones.
            """

            response = self.models['gemini'].generate_content(prompt)
            if response.text:
                code = response.text.strip()
                if code.startswith("```python"):
                    code = code[10:]
                if code.endswith("```"):
                    code = code[:-3]
                return code.strip()
            return None

        except Exception as e:
            logger.error(f"Error generando código: {e}")
            return None

    def validate_code(self, code: str) -> bool:
        """
        Valida que el código generado cumpla con los requisitos
        Args:
            code: Código a validar
        Returns:
            bool: True si el código es válido
        """
        try:
            # Verificar sintaxis
            compile(code, '<string>', 'exec')

            # Verificar imports prohibidos
            prohibited = ['requests', 'beautifulsoup', 'selenium', 'tensorflow', 'torch']
            for line in code.split('\n'):
                if line.strip().startswith('import '):
                    for lib in prohibited:
                        if lib in line:
                            logger.error(f"Librería prohibida encontrada: {lib}")
                            return False

            return True

        except Exception as e:
            logger.error(f"Error validando código: {e}")
            return False

    def translate_result(self, result: str, context: str) -> str:
        """
        Traduce el resultado técnico a lenguaje natural y conversacional
        Args:
            result: Resultado técnico o output de la función
            context: Contexto de la petición original
        """
        try:
            prompt = f"""
            CONVIERTE ESTE RESULTADO EN UNA RESPUESTA NATURAL Y CONVERSACIONAL:

            CONTEXTO DE LA PETICIÓN:
            {context}

            RESULTADO:
            {result}

            REGLAS:
            1. Responder como si fueras un asistente amigable hablando directamente
            2. Si es un resultado exitoso:
               - Confirmar que se realizó la acción
               - Mencionar el resultado específico
               - Ofrecer información adicional relevante
            3. Si es un error:
               - Explicar el problema de forma simple
               - Sugerir posibles soluciones
               - Mostrar empatía
            4. Usar lenguaje:
               - Natural y coloquial
               - Claro y directo
               - Personalizado al contexto

            Ejemplos:
            - "¡Listo! He creado el juego que pediste. Puedes jugarlo escribiendo..."
            - "El cálculo resultó en 42. ¿Quieres que te explique cómo llegué a ese número?"
            - "Ups, parece que hubo un problema al intentar {acción}. ¿Quieres que lo intente de otra manera?"

            Responde SOLO con la traducción conversacional, sin explicaciones adicionales.
            """

            response = self.models['gemini'].generate_content(prompt)
            if response.text:
                return response.text.strip()
            return result

        except Exception as e:
            logger.error(f"Error traduciendo resultado: {e}")
            return result 