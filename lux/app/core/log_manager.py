import logging
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any
import os

class LogManager:
    def __init__(self):
        # Directorio base para logs
        self.logs_dir = Path("resources/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos específicos de log
        self.execution_log = self.logs_dir / "executions.log"
        self.error_log = self.logs_dir / "errors.log"
        self.function_logs_dir = self.logs_dir / "functions"
        self.function_logs_dir.mkdir(exist_ok=True)

    def log_execution(self, function_name: str, result: Dict[str, Any]):
        """Registra una ejecución de función"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "function": function_name,
                "success": result.get("success", False),
                "execution_time": result.get("execution_time", 0),
                "error": result.get("error", None)
            }
            
            # Log general de ejecuciones
            with open(self.execution_log, "a", encoding="utf-8") as f:
                json.dump(log_entry, f)
                f.write("\n")
                
            # Log específico de la función
            function_log = self.function_logs_dir / f"{function_name}.log"
            with open(function_log, "a", encoding="utf-8") as f:
                json.dump(log_entry, f)
                f.write("\n")
                
        except Exception as e:
            logger.error(f"Error logging execution: {e}")

    def log_error(self, function_name: str, error: str, context: Dict[str, Any]):
        """Registra un error de función"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "function": function_name,
                "error": str(error),
                "context": context
            }
            
            # Log general de errores
            with open(self.error_log, "a", encoding="utf-8") as f:
                json.dump(log_entry, f)
                f.write("\n")
                
            # Log específico de la función
            function_log = self.function_logs_dir / f"{function_name}_errors.log"
            with open(function_log, "a", encoding="utf-8") as f:
                json.dump(log_entry, f)
                f.write("\n")
                
        except Exception as e:
            logger.error(f"Error logging error: {e}")

    def setup_logging(self):
        """Configura la estructura de directorios y handlers de logging"""
        # Crear estructura de directorios
        dirs = {
            'functions': self.logs_dir / 'functions',
            'executions': self.logs_dir / 'executions',
            'errors': self.logs_dir / 'errors',
            'metrics': self.logs_dir / 'metrics'
        }
        
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Configurar formato base
        self.base_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def log_function_creation(self, function_name: str, metadata: Dict[str, Any]):
        """Registra la creación de una nueva función"""
        log_file = self.logs_dir / 'functions' / f'{function_name}_creation.log'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
            f.write("METADATA:\n")
            f.write(json.dumps(metadata, indent=2))
            f.write("\n")
            
    def log_execution(self, function_name: str, execution_data: Dict[str, Any]):
        """Registra la ejecución de una función"""
        log_file = self.logs_dir / 'executions' / f'{function_name}_executions.log'
        metrics_file = self.logs_dir / 'metrics' / f'{function_name}_metrics.json'
        
        # Registrar ejecución
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
            f.write(f"SUCCESS: {execution_data.get('success', False)}\n")
            f.write(f"EXECUTION TIME: {execution_data.get('execution_time', 0)}s\n")
            f.write(f"MEMORY USED: {execution_data.get('memory_used', 0)} bytes\n")
            if not execution_data.get('success'):
                f.write(f"ERROR: {execution_data.get('error', 'Unknown error')}\n")
                
        # Actualizar métricas
        try:
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                metrics = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'total_execution_time': 0,
                    'average_execution_time': 0,
                    'total_memory_used': 0,
                    'average_memory_used': 0,
                    'error_count': 0,
                    'last_execution': None,
                    'execution_history': []
                }
                
            # Actualizar estadísticas
            metrics['total_executions'] += 1
            if execution_data.get('success'):
                metrics['successful_executions'] += 1
            else:
                metrics['error_count'] += 1
                
            metrics['total_execution_time'] += execution_data.get('execution_time', 0)
            metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_executions']
            
            metrics['total_memory_used'] += execution_data.get('memory_used', 0)
            metrics['average_memory_used'] = metrics['total_memory_used'] / metrics['total_executions']
            
            metrics['last_execution'] = datetime.now().isoformat()
            
            # Mantener historial de últimas 100 ejecuciones
            metrics['execution_history'].append({
                'timestamp': datetime.now().isoformat(),
                'success': execution_data.get('success', False),
                'execution_time': execution_data.get('execution_time', 0),
                'memory_used': execution_data.get('memory_used', 0)
            })
            metrics['execution_history'] = metrics['execution_history'][-100:]
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error updating metrics for {function_name}: {e}")
            
    def get_function_metrics(self, function_name: str) -> Dict[str, Any]:
        """Obtiene las métricas de una función"""
        metrics_file = self.logs_dir / 'metrics' / f'{function_name}_metrics.json'
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                return json.load(f)
        return {} 