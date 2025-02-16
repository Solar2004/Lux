import logging
from typing import Dict, List, Set, Optional, Any
from difflib import get_close_matches
import json
from pathlib import Path

logger = logging.getLogger('lux.feedback')

class FeedbackManager:
    def __init__(self, registry):
        self.registry = registry
        self.error_templates = {
            'function_not_found': {
                'message': "No encontré la función '{name}'. {suggestions}",
                'action': "Puedo crear una nueva función si me describes lo que necesitas."
            },
            'execution_error': {
                'message': "Hubo un error al ejecutar '{name}': {error}",
                'action': "Esto puede deberse a {reason}. Sugerencia: {suggestion}"
            },
            'permission_error': {
                'message': "No tengo permiso para {action}",
                'action': "Por favor, verifica que tengo acceso a {resource}"
            },
            'validation_error': {
                'message': "La función no cumple con los requisitos: {details}",
                'action': "Necesito ajustar el código para cumplir con las reglas de seguridad."
            },
            'dependency_error': {
                'message': "Hay un problema con las dependencias: {details}",
                'action': "Necesito {action} para continuar."
            }
        }
        
    def get_error_message(self, error_type: str, **kwargs) -> Dict[str, str]:
        """
        Genera un mensaje de error descriptivo con sugerencias
        Args:
            error_type: Tipo de error
            **kwargs: Variables para el template
        Returns:
            Dict con mensaje y acción sugerida
        """
        template = self.error_templates.get(error_type, {
            'message': "Error desconocido: {error}",
            'action': "Por favor, intenta de nuevo o describe tu necesidad de otra forma."
        })
        
        try:
            message = template['message'].format(**kwargs)
            action = template['action'].format(**kwargs)
            
            # Agregar sugerencias específicas
            if error_type == 'function_not_found':
                suggestions = self._get_function_suggestions(kwargs.get('name', ''))
                if suggestions:
                    message = message.format(
                        suggestions=f"\n¿Quizás quisiste decir alguna de estas?\n{suggestions}"
                    )
                else:
                    message = message.format(suggestions='')
                    
            return {
                'message': message,
                'action': action
            }
            
        except Exception as e:
            logger.error(f"Error generando mensaje: {e}")
            return {
                'message': f"Error: {kwargs.get('error', 'desconocido')}",
                'action': "Por favor, intenta de nuevo."
            }
            
    def _get_function_suggestions(self, query: str, max_suggestions: int = 3) -> str:
        """Genera sugerencias de funciones similares"""
        try:
            available_functions = list(self.registry.list_functions().keys())
            matches = get_close_matches(query, available_functions, n=max_suggestions, cutoff=0.6)
            
            if matches:
                suggestions = "\n".join([
                    f"- {name}: {self.registry.get_description(name)}"
                    for name in matches
                ])
                return suggestions
            return ""
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return ""
            
    def get_related_functions(self, function_name: str) -> List[Dict[str, str]]:
        """
        Encuentra funciones relacionadas basadas en tags y descripción
        Returns:
            Lista de funciones relacionadas con descripción
        """
        try:
            current_function = self.registry.get_function_info(function_name)
            if not current_function:
                return []
                
            current_tags = set(current_function.get('tags', []))
            current_type = current_function.get('function_type')
            
            related = []
            for name, info in self.registry.list_functions().items():
                if name == function_name:
                    continue
                    
                # Verificar relación por tags y tipo
                tags = set(info.get('tags', []))
                if (tags & current_tags or 
                    info.get('function_type') == current_type):
                    related.append({
                        'name': name,
                        'description': info.get('description', ''),
                        'type': info.get('function_type', 'utility'),
                        'common_tags': list(tags & current_tags)
                    })
                    
            return sorted(
                related,
                key=lambda x: len(x.get('common_tags', [])),
                reverse=True
            )[:3]
            
        except Exception as e:
            logger.error(f"Error buscando funciones relacionadas: {e}")
            return []
            
    def format_execution_result(self, result: Dict[str, Any], function_name: str) -> str:
        """
        Formatea el resultado de una ejecución de forma amigable
        """
        try:
            if result.get('success'):
                output = result['result']
                related = self.get_related_functions(function_name)
                
                if related:
                    output += "\n\nFunciones relacionadas que podrían interesarte:"
                    for func in related:
                        output += f"\n- {func['name']}: {func['description']}"
                        
                return output
                
            else:
                error_context = {
                    'name': function_name,
                    'error': result.get('error', 'Error desconocido'),
                    'type': result.get('type', 'unknown')
                }
                
                error_msg = self.get_error_message(
                    'execution_error',
                    **error_context
                )
                
                return f"{error_msg['message']}\n{error_msg['action']}"
                
        except Exception as e:
            logger.error(f"Error formateando resultado: {e}")
            return str(result.get('result', 'Error en la ejecución')) 