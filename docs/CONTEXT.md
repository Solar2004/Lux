# Lux: Asistente de IA Personal - Documentación para Desarrolladores

## Descripción General

Lux es un asistente de inteligencia artificial diseñado para mejorar la vida del usuario, ofreciendo una amplia gama de funcionalidades que abarcan desde el entretenimiento y la gestión de información hasta la organización de tareas y el soporte personalizado. Inspirado en la figura de un asistente personal avanzado como Jarvis, y con la personalidad del personaje Luxion del anime "Otome game no hametsu flag shika nai kuni", Lux busca ser una herramienta intuitiva, proactiva y con una interfaz conversacional natural.

## Tech Stack

- Frontend: PyQt
- Backend: Python
- Database: SQLite
- AI Processing: Deepseek, Gemini, Groq, OpenRouter
- TTS: Google Text-to-Speech
- STT: Google Speech-to-Text

## Funcionalidades Principales

Lux se distingue por las siguientes funcionalidades:

1.  **Reproducción Multimedia:**
    *   **Funcionalidad:** Permite reproducir listas de reproducción y videos individuales de YouTube.
    *   **Interacción del Usuario:** El usuario puede solicitar la reproducción de una playlist o video específico indicando la URL o el nombre de la playlist/video.  Ejemplo: "Lux, reproduce mi playlist de YouTube de música para estudiar." o "Lux, reproduce el video https://www.youtube.com/channel/UC6lZ5D0xFdkykMhaUOylKEw".
    *   **Detalles Técnicos:**  Integración con la API de YouTube Data V3 para búsqueda y reproducción. Uso de Gemini Fast Functions para interpretar la solicitud del usuario y extraer la información necesaria (URL, nombre).
    *   **Elementos de UI:**  Controlador multimedia básico (play, pause, siguiente, anterior, volumen). Posibilidad de mostrar miniaturas de video/playlist.
    *   **Notas para Desarrolladores:**  Considerar la gestión de errores en caso de URLs inválidas o problemas con la API de YouTube. Implementar caché para las playlists para mejorar la velocidad de carga.

2.  **Gestión de Archivos:**
    *   **Funcionalidad:** Permite crear archivos de texto (.txt) en ubicaciones específicas del sistema de archivos del usuario (Escritorio, Documentos, etc.).
    *   **Interacción del Usuario:**  El usuario puede indicar la ubicación y el nombre del archivo a crear. Ejemplo: "Lux, crea un archivo llamado 'ideas.txt' en el Escritorio." o "Lux, guarda un archivo de texto en Documentos llamado 'lista de compras'".
    *   **Detalles Técnicos:**  Uso de funciones del sistema operativo para la creación de archivos y directorios. Gemini Fast Functions para interpretar la solicitud y extraer la ubicación y el nombre del archivo.  Validación de permisos de escritura.
    *   **Elementos de UI:**  Confirmación visual de la creación del archivo.  Posibilidad de mostrar un diálogo para confirmar la ubicación y el nombre antes de la creación. (Opcional, la confirmación por voz puede ser suficiente).
    *   **Notas para Desarrolladores:** Implementar manejo de errores en caso de permisos insuficientes, nombres de archivo inválidos, o directorios inexistentes. Considerar la posibilidad de soportar otros formatos de archivo en el futuro (ej: .docx, .xlsx).

3.  **Búsqueda y Resumen de Información Web:**
    *   **Funcionalidad:** Realiza búsquedas en internet utilizando múltiples fuentes (ej: Google, Bing, DuckDuckGo) y, con la ayuda de IA, genera un resumen conciso de la información encontrada.
    *   **Interacción del Usuario:** El usuario realiza una pregunta o solicita información sobre un tema. Ejemplo: "Lux, ¿qué es el amor?" o "Lux, busca información sobre la fotosíntesis".
    *   **Detalles Técnicos:** Integración con APIs de motores de búsqueda o uso de bibliotecas de web scraping (con consideraciones éticas y de términos de servicio).  Uso de Gemini Fast Functions para procesar la pregunta del usuario, realizar búsquedas, y luego utilizar un modelo de lenguaje (parte de Gemini Fast) para generar un resumen cohesivo y relevante de los resultados.
    *   **Elementos de UI:**  Presentación del resumen de forma clara y legible (texto formateado, listas, etc.).  Posibilidad de citar las fuentes de información (opcional inicialmente).
    *   **Notas para Desarrolladores:**  Optimizar las consultas de búsqueda para obtener resultados relevantes.  Mejorar la calidad del resumen generado por la IA, enfocándose en la precisión y la concisión. Considerar la implementación de un sistema de "fuentes" para que el usuario pueda verificar la información. Manejar casos donde la búsqueda no arroja resultados relevantes.

4.  **Gestión de Recordatorios:**
    *   **Funcionalidad:** Permite al usuario crear recordatorios de tareas, ideas, y eventos recurrentes.
    *   **Interacción del Usuario:**
        *   **Tareas/Ideas:**  El usuario puede dictar o escribir tareas pendientes o ideas. Ejemplo: "Lux, recuérdame comprar leche" o "Lux, guarda la idea de escribir un libro de ciencia ficción".
        *   **Recordatorios Programados:** El usuario puede programar recordatorios para fechas y horas específicas o intervalos recurrentes. Ejemplo: "Lux, recuérdame tomar agua cada hora" o "Lux, recuérdame ir al gimnasio todos los lunes a las 7 PM".
    *   **Detalles Técnicos:**  Uso de almacenamiento persistente (base de datos local o en la nube) para guardar los recordatorios.  Implementación de un sistema de notificaciones push para alertar al usuario en el momento programado.  Gemini Fast Functions para procesar las solicitudes de creación y gestión de recordatorios.
    *   **Elementos de UI:**
        *   Lista de recordatorios pendientes (en la interfaz principal o en una sección dedicada).
        *   Interfaz para crear nuevos recordatorios (input de texto, selector de fecha/hora, opción de recurrencia).
        *   Notificaciones visuales y sonoras para los recordatorios programados.
    *   **Notas para Desarrolladores:**  Asegurar la persistencia de los recordatorios incluso si la app se cierra o el dispositivo se reinicia.  Implementar un sistema eficiente de gestión de notificaciones.  Permitir la edición y eliminación de recordatorios.

5.  **Asistencia Inteligente para Tareas:**
    *   **Funcionalidad:**  Lux asiste al usuario en la realización de tareas, proporcionando contexto sobre el objetivo actual, sugiriendo pasos a seguir y ofreciendo herramientas como un cronómetro.
    *   **Interacción del Usuario:**
        *   **Inicio de Tarea:** Al iniciar la app o invocar a Lux ("Lux"), este recuerda el objetivo actual (si lo hay) y ofrece asistencia. Ejemplo: "Bienvenido/a Lorian, veo que tu objetivo actual es [objetivo]. ¿Quieres que te ayude a continuar?"
        *   **Planificación de Tareas:**  Lux puede ayudar a desglosar un objetivo en pasos más pequeños. Ejemplo: "Lux, quiero aprender a programar en Python".  Lux podría responder: "Para aprender Python, podríamos empezar por: 1. Instalar Python, 2. Aprender los tipos de datos básicos, 3. Practicar con ejercicios sencillos... ¿Quieres que empecemos con el paso 1?".
        *   **Gestión del Tiempo:**  Lux puede iniciar un cronómetro para medir el tiempo dedicado a una tarea. Ejemplo: "Lux, inicia un cronómetro para el paso 1".
        *   **Adaptabilidad y Flexibilidad:**  Lux escucha las peticiones del usuario para cambiar el objetivo o tomar descansos. Ejemplo: "Lux, quiero cambiar mi objetivo a aprender francés" o "Lux, necesito un descanso".  Lux responde consecuentemente, pausando la tarea actual o adaptándose al nuevo objetivo.
        *   **Reanudación:** Al invocar a Lux después de un descanso ("Lux"), este retoma la asistencia donde se dejó.
    *   **Detalles Técnicos:**  Gemini Fast Functions para mantener el contexto de la conversación y el objetivo del usuario.  Gestión del estado de la tarea (objetivo actual, pasos completados, tiempo dedicado).  Implementación de un cronómetro funcional.  Personalización de las sugerencias y el tono de voz para reflejar la personalidad de Luxion.
    *   **Elementos de UI:**
        *   Presentación clara del objetivo actual y los pasos sugeridos (listas, tarjetas).
        *   Interfaz de cronómetro visible y fácil de usar (botones de inicio, pausa, stop).
        *   Respuestas de voz consistentes con la personalidad de Luxion.
    *   **Notas para Desarrolladores:**  Desarrollar una lógica de conversación fluida y adaptable a diferentes escenarios y peticiones del usuario.  Implementar un sistema de gestión de "objetivos" y "tareas" que persista entre sesiones.  Asegurar que la personalidad de Luxion se refleje consistentemente en las respuestas de voz y texto.

6.  **Interacción por Voz:**
    *   **Funcionalidad:** Lux puede hablar, escuchar y entender lenguaje natural.
    *   **Detalles Técnicos:**
        *   **Texto a Voz (TTS):** Integración con una API de TTS de alta calidad (ej: Google Text-to-Speech, Amazon Polly) para generar la voz de Luxion.  Configuración para emular la voz y el tono de Luxion.
        *   **Voz a Texto (STT):** Integración con una API de STT (ej: Google Speech-to-Text, AssemblyAI) para transcribir el habla del usuario.
        *   **Procesamiento del Lenguaje Natural (NLP):**  Gemini Fast Functions actúa como el motor NLP para entender la intención del usuario, extraer entidades (ej: URLs, nombres de archivos, fechas), y generar respuestas coherentes.
    *   **Notas para Desarrolladores:**  Optimizar la calidad del TTS para sonar natural y similar a Luxion.  Asegurar la precisión del STT en diferentes entornos y con diferentes acentos.  Mejorar continuamente la capacidad de NLP para entender mejor las peticiones complejas y ambiguas.

7.  **Personalidad de Luxion:**
    *   **Funcionalidad:**  Lux adopta la personalidad de Luxion del anime "Otome game no hametsu flag shika nai kuni". Esto se manifiesta en su tono de voz, estilo de respuesta, y (potencialmente) en elementos visuales en la interfaz (ej: un avatar opcional de Luxion).
    *   **Detalles Técnicos:**  La personalidad se implementa a través de:
        *   **Tono de Voz TTS:**  Selección de una voz TTS que se asemeje a la de Luxion o personalización de los parámetros de la voz (tono, velocidad) para lograr el efecto deseado.
        *   **Estilo de Respuesta:**  Programación de Gemini Fast Functions para generar respuestas que reflejen la personalidad de Luxion:  serio, eficiente, ligeramente sarcástico pero siempre útil y leal (a su "Lorian").  Considerar frases y expresiones características del personaje.
    *   **Elementos de UI:**
        *   Círculo con el nombre "Lux" como icono de inicio/espera (ya mencionado en la descripción inicial).
        *   (Opcional) Avatar de Luxion que puede aparecer en la interfaz durante la interacción o en momentos clave.
    *   **Notas para Desarrolladores:**  Investigar a fondo la personalidad de Luxion para capturarla de forma precisa y respetuosa.  Realizar pruebas con usuarios para asegurar que la personalidad implementada sea reconocible y agradable.

## Interacción por Voz y Control

### Control por Micrófono Físico
- La aplicación utiliza el estado físico del micrófono (mute/unmute) para controlar la escucha
- Cuando el micrófono está unmute, Lux escucha continuamente
- Al mutear el micrófono, Lux deja de escuchar automáticamente
- No requiere palabra de activación ("wake word")

### Panel de Control
- Ventana secundaria independiente que muestra:
  - Logs del sistema en tiempo real
  - Estado de servicios (IA, voz, media)
  - Métricas de uso
  - Gestión avanzada de tareas
  - Control de reproducción multimedia
- Accesible desde la ventana principal
- Diseñado para usuarios avanzados y debugging

### Modelos de IA
- **Chat General:** Gemini (modelo principal)
- **Programación y Tareas Técnicas:** 
  - Deepseek-coder
  - Claude 3
  - GPT-4 (vía OpenRouter)
- **Análisis de Voz:** 
  - Google Speech-to-Text
  - Whisper (alternativa local)

## Estructura de Ventanas

1. **Ventana Principal**
   - LuxCircle (elemento central)
   - Controles básicos
   - Indicadores de estado
   - Acceso al chat y panel de control

2. **Ventana de Chat**
   - Selector de modelos de IA
   - Historial de conversación
   - Campo de entrada
   - Indicadores de estado del modelo

3. **Panel de Control**
   - Visor de logs
   - Métricas y estadísticas
   - Gestión avanzada de tareas
   - Control multimedia detallado
   - Estado de servicios

## Flujo de Usuario

1.  **Inicio de la App:** Al abrir la aplicación, se muestra un círculo con el nombre "Lux" en el centro de la pantalla.
2.  **Bienvenida:**  Inmediatamente después de iniciar, Lux (con la voz de Luxion) da la bienvenida al usuario llamándolo "Lorian". Ejemplo: "Bienvenido a tu servicio, Lorian."
3.  **Escucha Activa (Palabra Clave "Lux"):** La app entra en un estado de escucha pasiva, esperando a que el usuario pronuncie la palabra clave "Lux" para activarse completamente.
4.  **Interacción Vocal:**  Una vez que se pronuncia "Lux", el asistente se activa y espera comandos de voz. El usuario puede realizar cualquiera de las acciones descritas en las funcionalidades principales.
5.  **Respuesta y Acción:** Lux procesa la solicitud del usuario utilizando Gemini Fast Functions, entiende la intención, y realiza la acción correspondiente (reproducir música, crear archivo, buscar información, etc.).  Lux responde al usuario verbalmente (con voz de Luxion) y/o visualmente (mostrando resultados, confirmaciones, etc.).
6.  **Asistencia Proactiva (Contexto de Tareas):**  Si el usuario tiene un objetivo o tarea en curso, al invocar a Lux ("Lux") o al iniciar la app, este le recordará el objetivo y ofrecerá continuar la asistencia, guiando al usuario paso a paso.
7.  **Descanso/Reanudación:**  Si el usuario solicita un descanso, Lux reconoce la petición y se "desactiva" hasta que se le invoque de nuevo con la palabra clave "Lux".  Al reanudarse, Lux retoma el contexto donde se dejó.
8.  **Cierre de la App:** Al cerrar la aplicación, el estado de la tarea, los recordatorios y la configuración se guardan para la próxima sesión.

## Consideraciones Técnicas Clave

*   **Integración con Gemini Fast Functions:**  Fundamental para la interpretación del lenguaje natural, la gestión de funciones específicas (reproducción multimedia, gestión de archivos, etc.), y la generación de respuestas.
*   **APIs Externas:**  Uso de APIs de YouTube, motores de búsqueda, servicios TTS y STT.  Seleccionar APIs robustas, con buena documentación y precios adecuados.
*   **Procesamiento de Voz:**  Implementar un sistema eficiente y preciso de STT y TTS.  Optimizar para diferentes entornos de audio y dispositivos.
*   **Gestión de Estado y Contexto:**  Mantener el contexto de la conversación y el estado de las tareas del usuario para una experiencia fluida y proactiva.
*   **Persistencia de Datos:**  Almacenar de forma segura y eficiente los recordatorios, objetivos, historial de sesiones, y preferencias del usuario.
*   **Diseño de UI/UX:**  Priorizar una interfaz de usuario limpia, intuitiva y que complemente la interacción vocal.  El círculo "Lux" como elemento visual central.
*   **Rendimiento y Optimización:**  Asegurar que la app sea rápida, responsiva y consuma pocos recursos, especialmente en dispositivos móviles.

## Estructura de Base de Datos

### Tablas

1. **users**
   - id (INTEGER PRIMARY KEY)
   - name (TEXT)
   - settings_json (TEXT) # Configuraciones del usuario en formato JSON
   - created_at (TIMESTAMP)
   - last_login (TIMESTAMP)

2. **tasks**
   - id (INTEGER PRIMARY KEY)
   - user_id (INTEGER) # FK -> users.id
   - title (TEXT)
   - description (TEXT)
   - status (TEXT) # ['active', 'completed', 'paused']
   - steps_json (TEXT) # Pasos de la tarea en formato JSON
   - current_step (INTEGER)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

3. **reminders**
   - id (INTEGER PRIMARY KEY)
   - user_id (INTEGER) # FK -> users.id
   - title (TEXT)
   - description (TEXT)
   - due_date (TIMESTAMP)
   - recurrence_rule (TEXT) # Regla de recurrencia en formato iCal
   - status (TEXT) # ['active', 'completed', 'dismissed']
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

4. **media_history**
   - id (INTEGER PRIMARY KEY)
   - user_id (INTEGER) # FK -> users.id
   - type (TEXT) # ['youtube_video', 'youtube_playlist']
   - media_id (TEXT) # ID del video/playlist
   - title (TEXT)
   - last_played (TIMESTAMP)
   - play_count (INTEGER)

5. **chat_history**
   - id (INTEGER PRIMARY KEY)
   - user_id (INTEGER) # FK -> users.id
   - message (TEXT)
   - response (TEXT)
   - context_json (TEXT) # Contexto de la conversación en JSON
   - timestamp (TIMESTAMP)

6. **files**
   - id (INTEGER PRIMARY KEY)
   - user_id (INTEGER) # FK -> users.id
   - path (TEXT)
   - name (TEXT)
   - type (TEXT)
   - created_at (TIMESTAMP)
   - last_accessed (TIMESTAMP)

## Estructura de Carpetas

lux/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── config.py
│ ├── core/
│ │ ├── init.py
│ │ ├── ai_manager.py # Gestión de IA (Gemini, etc.)
│ │ ├── voice_manager.py # Gestión de TTS/STT
│ │ └── media_manager.py # Gestión de multimedia
│ ├── database/
│ │ ├── init.py
│ │ ├── models.py
│ │ └── database.py
│ ├── services/
│ │ ├── init.py
│ │ ├── reminder_service.py
│ │ ├── task_service.py
│ │ ├── file_service.py
│ │ └── search_service.py
│ ├── ui/
│ │ ├── init.py
│ │ ├── main_window.py
│ │ ├── components/
│ │ │ ├── init.py
│ │ │ ├── lux_circle.py
│ │ │ ├── media_player.py
│ │ │ └── task_view.py
│ │ └── styles/
│ │ ├── init.py
│ │ └── main.qss
│ └── utils/
│ ├── init.py
│ ├── logger.py
│ └── helpers.py
├── tests/
│ ├── init.py
│ ├── test_ai_manager.py
│ ├── test_voice_manager.py
│ └── test_services/
│ ├── init.py
│ └── test_reminder_service.py
├── docs/
│ ├── CONTEXT.md
│ └── DEVELOPMENT_PLAN.md
├── resources/
│ ├── audio/
│ │ └── notifications/
│ ├── images/
│ │ └── icons/
│ └── fonts/
├── .env.example
├── requirements.txt
└── README.md


Una estructura de carpetas organizada y escalable que sigue las mejores prácticas de Python:
app/: Código principal de la aplicación
core/: Componentes centrales
database/: Modelos y gestión de base de datos
services/: Servicios específicos
ui/: Interfaz de usuario con PyQt
utils/: Utilidades generales
tests/: Pruebas unitarias
docs/: Documentación
resources/: Recursos estáticos


## Conclusión

Este documento proporciona una guía detallada para el desarrollo del asistente de IA Lux.  Los desarrolladores deben enfocarse en la integración robusta de Gemini Fast Functions, la calidad de la interacción vocal, la implementación de la personalidad de Luxion, y la creación de una experiencia de usuario fluida y útil.  Esta documentación es un punto de partida y puede ser ampliada y refinada a medida que el desarrollo avance y se obtenga feedback de los usuarios.