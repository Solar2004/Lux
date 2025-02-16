import logging
from typing import Optional

class CommandHandler:
    def __init__(self, ai_service, task_service, media_player):
        self.ai_service = ai_service
        self.task_service = task_service
        self.media_player = media_player
        self.logger = logging.getLogger('lux')
    
    def handle_command(self, text: str) -> Optional[str]:
        """
        Procesa un comando y retorna una respuesta
        Args:
            text: Texto del comando
        Returns:
            str: Respuesta al comando o None si no es un comando
        """
        try:
            # Analizar el texto con AI
            analysis = self.ai_service.analyze_task(text)
            self.logger.info(f"Análisis de comando: {analysis}")
            
            command_type = analysis.get('type')
            action = analysis.get('action')
            details = analysis.get('details', {})
            
            if command_type == 'task':
                if action == 'create':
                    task = self.task_service.create_task(
                        user_id=1,
                        title=details.get('title', text),
                        description=details.get('description', ''),
                        priority=0
                    )
                    return f"He creado la tarea: {task.title}"
                
            elif command_type == 'music':
                if action == 'play':
                    query = details.get('query', text)
                    # TODO: Implementar búsqueda y reproducción
                    return f"Buscando música: {query}"
                
            elif command_type == 'chat':
                # Procesar como conversación normal
                return self.ai_service.chat(text)
            
            return "No entendí qué quieres que haga"
            
        except Exception as e:
            self.logger.error(f"Error procesando comando: {e}")
            return "Lo siento, ocurrió un error al procesar tu comando" 