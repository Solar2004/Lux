import logging
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
import importlib.util
import ast

logger = logging.getLogger('lux.testing')

class TestManager:
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.max_repair_attempts = 4  # 3 intentos de reparación + 1 reescritura completa
        
    def test_function(self, function_name: str, code: str) -> Dict[str, Any]:
        """
        Prueba una función y repara si es necesario
        Returns:
            Dict con resultado y código reparado si aplica
        """
        try:
            # Crear módulo temporal para pruebas
            spec = importlib.util.spec_from_file_location(function_name, "")
            module = importlib.util.module_from_spec(spec)
            
            # Ejecutar código en el módulo
            exec(code, module.__dict__)
            
            # Obtener la función
            func = getattr(module, function_name, None)
            if not func:
                return self._repair_code(
                    code, 
                    f"Función {function_name} no encontrada en el código"
                )
            
            # Validar estructura
            validation_result = self._validate_function(func, code)
            if not validation_result['valid']:
                return self._repair_code(code, validation_result['error'])
            
            # Ejecutar prueba básica
            try:
                result = func()
                if not isinstance(result, str):
                    return self._repair_code(
                        code,
                        "La función debe retornar un string"
                    )
                    
                return {
                    'success': True,
                    'code': code,
                    'result': result
                }
                
            except Exception as e:
                return self._repair_code(
                    code,
                    f"Error ejecutando función: {str(e)}\n{traceback.format_exc()}"
                )
                
        except Exception as e:
            return self._repair_code(
                code,
                f"Error en prueba: {str(e)}\n{traceback.format_exc()}"
            )
            
    def _repair_code(self, code: str, error: str, attempt: int = 1) -> Dict[str, Any]:
        """
        Intenta reparar código con errores
        Args:
            code: Código original
            error: Descripción del error
            attempt: Número de intento actual
        """
        logger.info(f"Intento {attempt} de reparación")
        logger.error(f"Error encontrado: {error}")
        
        if attempt > self.max_repair_attempts:
            return {
                'success': False,
                'error': "Se agotaron los intentos de reparación",
                'code': code
            }
            
        try:
            prompt = f"""
            REPARA ESTE CÓDIGO PYTHON QUE TIENE ERRORES:

            ERROR ENCONTRADO:
            {error}

            CÓDIGO ACTUAL:
            {code}

            {'IMPORTANTE: Genera el código completamente nuevo' if attempt == self.max_repair_attempts else 'IMPORTANTE: Corrige solo los errores encontrados'}

            REGLAS:
            1. La función debe retornar siempre un string descriptivo
            2. Manejar todos los errores posibles
            3. Usar solo librerías permitidas
            4. Mantener la funcionalidad original
            5. Documentar los cambios realizados

            Responde SOLO con el código corregido, sin explicaciones.
            """

            repaired_code = self.ai_service.generate_content(prompt)
            if not repaired_code:
                return {
                    'success': False,
                    'error': "No se pudo generar código reparado",
                    'code': code
                }
                
            # Probar código reparado
            test_result = self.test_function(
                self._extract_function_name(code),
                repaired_code
            )
            
            if test_result['success']:
                return test_result
                
            # Si falla, intentar de nuevo
            return self._repair_code(
                repaired_code,
                test_result['error'],
                attempt + 1
            )
            
        except Exception as e:
            logger.error(f"Error en reparación: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': code
            }
            
    def _validate_function(self, func: Any, code: str) -> Dict[str, Any]:
        """Valida la estructura y documentación de una función"""
        try:
            # Verificar docstring
            if not func.__doc__:
                return {
                    'valid': False,
                    'error': "Función sin documentación"
                }
                
            # Verificar manejo de errores
            tree = ast.parse(code)
            has_try_except = False
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    has_try_except = True
                    break
                    
            if not has_try_except:
                return {
                    'valid': False,
                    'error': "Función sin manejo de errores"
                }
                
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error en validación: {e}"
            }
            
    def _extract_function_name(self, code: str) -> str:
        """Extrae el nombre de la función del código"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    return node.name
            return ""
        except:
            return "" 