import ast
import logging
from typing import Dict, List, Set, Optional
from pathlib import Path
import re

logger = logging.getLogger('lux.security')

class SecurityViolation:
    def __init__(self, type: str, message: str, line: int = 0):
        self.type = type
        self.message = message
        self.line = line

class SecurityAnalyzer:
    def __init__(self):
        self.violations: List[SecurityViolation] = []
        
        # Patrones de código peligroso
        self.dangerous_patterns = {
            'system_access': r'os\.(system|popen|spawn|exec)',
            'network_access': r'(socket|urllib|http|requests|ftp)',
            'file_write': r'(write|create|remove|delete|rmdir|unlink)',
            'code_execution': r'(eval|exec|compile|__import__)',
            'shell_injection': r'(subprocess|shell|command)',
        }
        
        # Imports prohibidos
        self.prohibited_imports = {
            'requests', 'urllib', 'socket', 'subprocess',
            'threading', 'multiprocessing', 'concurrent',
            'selenium', 'scrapy', 'beautifulsoup4'
        }
        
        # Imports permitidos
        self.allowed_imports = {
            'os.path', 'pathlib', 'datetime', 'random', 'math', 
            'json', 'pygame', 'sys', 'typing'
        }
        
        # Patrones de código malicioso
        self.malicious_patterns = {
            'shell_commands': r'(subprocess\..*|os\.system|os\.popen|commands\..*)',
            'network_access': r'(socket\..*|urllib\..*|requests\..*|http\..*)',
            'file_operations': r'(open|file|io\..*|fileinput\..*)',
            'code_execution': r'(eval|exec|compile|__import__|globals|locals)',
            'system_info': r'(os\.uname|platform\..*|sys\.version)',
            'process_manipulation': r'(os\.kill|signal\..*|psutil\..*)',
            'memory_manipulation': r'(ctypes\..*|mmap\..*)',
            'environment_vars': r'(os\.environ|os\.getenv|os\.putenv)',
        }
        
        # Operaciones sensibles que requieren permisos
        self.sensitive_operations = {
            'file_access': {
                'patterns': [r'open\(', r'Path\(', r'os\.path'],
                'permissions': ['file_read', 'file_write']
            },
            'network': {
                'patterns': [r'socket\.', r'requests\.'],
                'permissions': ['network_access']
            },
            'system': {
                'patterns': [r'os\.system', r'subprocess\.'],
                'permissions': ['system_exec']
            }
        }
        
    def analyze_code(self, code: str, function_name: str) -> List[SecurityViolation]:
        """Analiza el código en busca de problemas de seguridad"""
        self.violations = []
        
        try:
            # Parsear el código
            tree = ast.parse(code)
            
            # Análisis estático básico
            self._check_imports(tree)
            self._check_dangerous_calls(tree)
            self._check_file_operations(tree)
            self._check_infinite_loops(tree)
            self._check_resource_usage(tree)
            
            # Análisis de seguridad avanzado
            self._check_malicious_patterns(code)
            self._check_sensitive_operations(tree)
            self._check_data_validation(tree)
            self._check_error_handling(tree)
            self._check_input_sanitization(tree)
            
            return self.violations
            
        except Exception as e:
            logger.error(f"Error en análisis de seguridad: {e}")
            self.violations.append(
                SecurityViolation("error", f"Error analizando código: {e}")
            )
            return self.violations
            
    def _check_imports(self, tree: ast.AST):
        """Verifica imports prohibidos y permitidos"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.names[0].name
                if module in self.prohibited_imports:
                    self.violations.append(
                        SecurityViolation(
                            "import",
                            f"Import prohibido: {module}",
                            node.lineno
                        )
                    )
                elif not any(module.startswith(allowed) for allowed in self.allowed_imports):
                    self.violations.append(
                        SecurityViolation(
                            "import",
                            f"Import no permitido: {module}",
                            node.lineno
                        )
                    )
                    
    def _check_dangerous_calls(self, tree: ast.AST):
        """Verifica llamadas a funciones peligrosas"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in {'eval', 'exec', 'compile'}:
                        self.violations.append(
                            SecurityViolation(
                                "dangerous_call",
                                f"Llamada peligrosa a {func_name}()",
                                node.lineno
                            )
                        )
                        
    def _check_file_operations(self, tree: ast.AST):
        """Verifica operaciones de archivo seguras"""
        allowed_dirs = {'resources', 'logs', 'temp'}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Verificar que el path esté en directorios permitidos
                    if len(node.args) > 0:
                        path_arg = node.args[0]
                        if isinstance(path_arg, ast.Str):
                            path = Path(path_arg.s)
                            if not any(dir in path.parts for dir in allowed_dirs):
                                self.violations.append(
                                    SecurityViolation(
                                        "file_access",
                                        f"Acceso a archivo fuera de directorios permitidos: {path}",
                                        node.lineno
                                    )
                                )
                                
    def _check_infinite_loops(self, tree: ast.AST):
        """Detecta posibles loops infinitos"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.While, ast.For)):
                if not self._has_break_or_return(node):
                    self.violations.append(
                        SecurityViolation(
                            "infinite_loop",
                            "Posible loop infinito detectado",
                            node.lineno
                        )
                    )
                    
    def _has_break_or_return(self, node: ast.AST) -> bool:
        """Verifica si un nodo contiene break o return"""
        for child in ast.walk(node):
            if isinstance(child, (ast.Break, ast.Return)):
                return True
        return False
        
    def _check_resource_usage(self, tree: ast.AST):
        """Analiza uso de recursos"""
        # Contar variables y loops anidados
        loop_depth = 0
        var_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loop_depth += 1
                if loop_depth > 2:
                    self.violations.append(
                        SecurityViolation(
                            "resource_usage",
                            "Demasiados loops anidados",
                            node.lineno
                        )
                    )
            elif isinstance(node, ast.Name):
                var_count += 1
                
        if var_count > 50:
            self.violations.append(
                SecurityViolation(
                    "resource_usage",
                    f"Demasiadas variables ({var_count})"
                )
            )
            
    def _check_patterns(self, code: str):
        """Busca patrones de código peligroso"""
        for pattern_name, pattern in self.dangerous_patterns.items():
            matches = re.finditer(pattern, code)
            for match in matches:
                self.violations.append(
                    SecurityViolation(
                        pattern_name,
                        f"Patrón peligroso detectado: {match.group()}"
                    )
                )

    def _check_malicious_patterns(self, code: str):
        """Busca patrones de código potencialmente malicioso"""
        for pattern_name, pattern in self.malicious_patterns.items():
            matches = re.finditer(pattern, code)
            for match in matches:
                self.violations.append(
                    SecurityViolation(
                        "malicious_code",
                        f"Patrón de código potencialmente malicioso detectado: {match.group()}"
                    )
                )

    def _check_sensitive_operations(self, tree: ast.AST):
        """Verifica operaciones que requieren permisos especiales"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = ast.unparse(node)
                for op_name, op_info in self.sensitive_operations.items():
                    for pattern in op_info['patterns']:
                        if re.search(pattern, call_str):
                            self.violations.append(
                                SecurityViolation(
                                    "sensitive_operation",
                                    f"Operación sensible detectada ({op_name}): {call_str}. "
                                    f"Requiere permisos: {', '.join(op_info['permissions'])}"
                                )
                            )

    def _check_data_validation(self, tree: ast.AST):
        """Verifica la validación de datos de entrada"""
        has_input_validation = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Buscar comparaciones o validaciones
                for child in ast.walk(node):
                    if isinstance(child, (ast.Compare, ast.Call)):
                        has_input_validation = True
                        break
        
        if not has_input_validation:
            self.violations.append(
                SecurityViolation(
                    "input_validation",
                    "No se detectó validación de datos de entrada"
                )
            )

    def _check_input_sanitization(self, tree: ast.AST):
        """Verifica la sanitización de inputs"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Detectar uso directo de inputs sin sanitización
                    if node.func.id in {'input', 'raw_input'}:
                        self.violations.append(
                            SecurityViolation(
                                "input_sanitization",
                                "Uso de input sin sanitización detectado",
                                node.lineno
                            )
                        ) 