# Plan de Desarrollo: Sistema de Funciones Dinámicas

## 1. Análisis de Peticiones
### Objetivo
Determinar si una petición corresponde a una función existente o requiere crear una nueva.

### Componentes Necesarios
1. **Prompt para Gemini**
```python
def create_analysis_prompt(request: str, registry: dict) -> str:
    return f"""
    ANALIZA SI LA SIGUIENTE PETICIÓN COINCIDE CON ALGUNA FUNCIÓN EXISTENTE:
    
    PETICIÓN: "{request}"
    
    FUNCIONES DISPONIBLES:
    {json.dumps(registry, indent=2)}
    
    REGLAS:
    1. Si existe una función que hace lo solicitado:
       Responde: "YES - nombre_funcion"
    2. Si no existe y se necesita crear:
       Responde: "NEW - nombre_funcion descripción_función"
    3. Si no es una petición de función válida:
       Responde: "NO"
    
    IMPORTANTE:
    - Los nombres de nuevas funciones deben ser descriptivos y en snake_case
    - Usar verbos que indiquen la acción (crear_, buscar_, etc.)
    
    Responde SOLO con uno de los formatos anteriores, sin explicaciones adicionales.
    """
```

## 2. Generación de Código
### Objetivo
Generar código Python que implemente la funcionalidad solicitada.

### Componentes Necesarios
1. **Prompt para Generación de Código**
```python
def create_code_generation_prompt(function_name: str, description: str) -> str:
    return f"""
    CREA UNA FUNCIÓN EN PYTHON QUE CUMPLA:
    
    NOMBRE: {function_name}
    DESCRIPCIÓN: {description}
    
    REGLAS IMPORTANTES:
    1. SOLO usar estas librerías:
       - Estándar: os, sys, pathlib, datetime, random, math, json
       - GUI: pygame (solo para juegos)
    2. NO usar APIs que requieran keys
    3. NO acceder a recursos del sistema (excepto escritorio)
    4. Manejar TODOS los errores posibles
    5. Documentar el código
    6. Retornar siempre un string descriptivo
    
    FORMATO REQUERIDO:
    ```python
    def {function_name}() -> str:
        '''
        {description}
        Returns:
            str: Mensaje descriptivo del resultado
        '''
        try:
            # Código aquí
            return "Mensaje de éxito"
        except Exception as e:
            return f"Error: {{e}}"
    ```
    
    Responde SOLO con el código, sin explicaciones.
    """
```

## 3. Registro de Funciones
### Estructura del registry.json
```json
{
    "nombre_funcion": {
        "name": "nombre_funcion",
        "description": "Descripción detallada",
        "file_path": "path/to/function.py",
        "enabled": true,
        "created_at": "2024-03-14T12:00:00"
    }
}
```

## 4. Ejecución y Respuesta Natural
### Objetivo
Ejecutar funciones y traducir resultados a lenguaje natural.

### Componentes Necesarios
1. **Prompt para Traducción de Resultados**
```python
def create_response_prompt(output: str, original_request: str) -> str:
    return f"""
    TRADUCE ESTE RESULTADO TÉCNICO A LENGUAJE NATURAL:
    
    PETICIÓN ORIGINAL: "{original_request}"
    OUTPUT TÉCNICO: "{output}"
    
    REGLAS:
    1. Usar lenguaje conversacional y amigable
    2. Mantener la información técnica importante
    3. Contextualizar la respuesta
    
    Responde como si fueras un asistente explicando el resultado a un usuario.
    """
```

## 5. Implementación por Fases

### Fase 1: Análisis de Peticiones ✅
- [x] Implementar función de análisis
- [x] Integrar con Gemini
- [x] Pruebas de reconocimiento

### Fase 2: Generación de Código ✅
- [x] Implementar generador de código
- [x] Sistema de validación
- [x] Manejo de errores

### Fase 3: Sistema de Registro 🔄
- [x] Implementar guardado de archivos
- [x] Gestión del registry.json (falta mejorar)
- [x] Sistema de carga de funciones

### Fase 4: Ejecución y Respuestas ❌
- [x] Sistema de ejecución segura
- [x] Traducción de resultados
- [x] Logging y monitoreo

## 6. Estructura de Archivos
```
lux/
├── app/
│   ├── core/
│   │   ├── function_manager.py
│   │   └── function_registry.py
│   └── services/
│       └── ai_service.py
└── resources/
    └── functions/
        ├── registry.json
        └── [función].py
```