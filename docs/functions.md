\#\# Integración de Funciones en tu Aplicación con la API de Gemini (Ejemplos con `curl`)

Este documento te explica rápidamente cómo integrar funciones (tool use) en tu aplicación utilizando la API de Gemini y `curl`. Veremos ejemplos sencillos como obtener el clima y ejemplos conceptuales más complejos.

**Concepto de Funciones (Tool Use) en la API de Gemini**

La API de Gemini te permite definir funciones que el modelo puede invocar durante una conversación. Esto extiende las capacidades del modelo, permitiéndole interactuar con el mundo exterior para obtener información o realizar acciones.

**Flujo básico:**

1.  **Envías una solicitud a la API de Gemini** incluyendo la definición de las funciones disponibles.
2.  **La API analiza la solicitud del usuario.** Si determina que necesita usar una función para responder, la API responde indicando **qué función debe ser invocada** y **con qué parámetros**.
3.  **Tu aplicación recibe esta respuesta, invoca la función especificada** (ejecutando el código que implementa la función).
4.  **Tu aplicación envía una nueva solicitud a la API,** incluyendo el **resultado de la función**.
5.  **La API de Gemini utiliza el resultado de la función** para generar la respuesta final al usuario.

**Ejemplos con `curl`**

A continuación, veremos ejemplos paso a paso utilizando `curl`.

### **Ejemplo 1: Obtener el Clima Actual**

**1. Definición de la Función:**

Definiremos una función llamada `get_current_weather` que toma la ubicación como parámetro y devuelve información del clima.

**2. Solicitud `curl` inicial a la API de Gemini (con definición de función):**

```bash
curl \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{ "parts": [{"text": "¿Qué tiempo hace en Gafanha da Nazaré?"}]}],
    "tools": [{
      "function_declarations": [{
        "name": "get_current_weather",
        "description": "Obtiene el clima actual para una ubicación",
        "parameters": {
          "type": "OBJECT",
          "properties": {
            "location": {
              "type": "STRING",
              "description": "La ciudad y el estado, p. ej. 'Gafanha da Nazaré, Portugal'"
            },
            "unit": {
              "type": "STRING",
              "enum": ["celsius", "fahrenheit"],
              "description": "Unidad de temperatura"
            }
          },
          "required": ["location"]
        }
      }]
    }],
    "model": "models/gemini-2.0-flash"
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"
```

  * **`tools`**:  Incluimos la definición de la función `get_current_weather` dentro del campo `tools`.
  * **`function_declarations`**: Describe la función:
      * `name`:  `get_current_weather`
      * `description`:  `Obtiene el clima actual para una ubicación`
      * `parameters`: Define los parámetros que espera la función (`location` y `unit`).

**3. Respuesta de la API (Indicando Función a Invocar):**

La API podría responder con algo similar a esto (ejemplo simplificado):

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {
            "function_call": {
              "name": "get_current_weather",
              "args": {
                "location": "Gafanha da Nazaré, Portugal"
              }
            }
          }
        ]
      },
      "finishReason": "FUNCTION_CALL"
    }
  ]
}
```

  * **`function_call`**: La API indica que se debe invocar la función `get_current_weather`.
  * **`args`**:  Proporciona los argumentos que la función necesita (`location: "Gafanha da Nazaré, Portugal"`).
  * **`finishReason: "FUNCTION_CALL"`**:  Indica que la respuesta no es una respuesta de texto final, sino una solicitud para invocar una función.

**4. Implementación de la Función `get_current_weather` (Ejemplo en Python):**

Aquí implementarías la función `get_current_weather` en tu aplicación.  Este es un ejemplo conceptual usando una API del clima externa (reemplaza `YOUR_WEATHER_API_KEY` con una clave real de una API del clima como [OpenWeatherMap](https://www.google.com/url?sa=E&source=gmail&q=https://openweathermap.org/)):

```python
import requests

def get_current_weather(location, unit="celsius"):
  """Obtiene el clima actual usando una API externa."""
  api_key = "YOUR_WEATHER_API_KEY" # Reemplaza con tu clave API
  base_url = "http://api.openweathermap.org/data/2.5/weather"
  params = {
      "q": location,
      "appid": api_key,
      "units": unit # 'metric' para Celsius, 'imperial' para Fahrenheit
  }
  if unit.lower() == "celsius":
      params["units"] = "metric"
  elif unit.lower() == "fahrenheit":
      params["units"] = "imperial"
  else:
      params["units"] = "metric" # Default to Celsius

  try:
    response = requests.get(base_url, params=params)
    response.raise_for_status() # Lanza una excepción para errores HTTP
    data = response.json()

    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    weather_info = f"El clima en {location} es: {weather_description}. Temperatura: {temperature}°{unit.upper()}. Humedad: {humidity}%. Viento: {wind_speed} m/s."
    return weather_info

  except requests.exceptions.RequestException as e:
    return f"Error al obtener el clima: {e}"

# Ejemplo de uso de la función
location_name = "Gafanha da Nazaré, Portugal"
weather_result = get_current_weather(location_name, unit="celsius")
print(weather_result)
```

**5.  Segunda Solicitud `curl` a la API de Gemini (con el resultado de la función):**

Después de ejecutar la función `get_current_weather` y obtener el resultado (por ejemplo, `weather_result` en el código Python), envías una nueva solicitud a la API de Gemini, incluyendo este resultado:

```bash
curl \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [
      { "parts": [{"text": "¿Qué tiempo hace en Gafanha da Nazaré?"}]},
      {
        "role": "model",
        "parts": [
          {
            "function_call": {
              "name": "get_current_weather",
              "args": {
                "location": "Gafanha da Nazaré, Portugal"
              }
            }
          }
        ]
      },
      {
        "role": "function",
        "parts": [
          {
            "text": "'El clima en Gafanha da Nazaré es: cielo claro. Temperatura: 15.23°C. Humedad: 82%. Viento: 4.63 m/s.'"
          }
        ],
        "function_response": {
          "name": "get_current_weather"
        }
      }
    ],
    "model": "models/gemini-2.0-flash"
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"
```

  * **`contents`**: Ahora el contenido incluye:
      * El mensaje original del usuario: `¿Qué tiempo hace en Gafanha da Nazaré?`
      * La solicitud de invocación de función de la API (con `role: "model"` y `function_call`).
      * **El resultado de la función** (con `role: "function"` y `function_response`). El texto dentro de `parts` es el `weather_result` obtenido en el paso anterior.

**6. Respuesta Final de la API de Gemini (Respuesta al Usuario):**

Finalmente, la API de Gemini responderá con la respuesta final al usuario, utilizando el resultado de la función:

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {
            "text": "El tiempo en Gafanha da Nazaré es agradable. El cielo está despejado, con una temperatura de alrededor de 15 grados Celsius. La humedad es del 82% y el viento sopla a 4.63 metros por segundo."
          }
        ]
      },
      "finishReason": "STOP"
    }
  ]
}
```

  * **`text`**:  Esta es la respuesta final al usuario, generada por el modelo utilizando la información del clima obtenida a través de la función.
  * **`finishReason: "STOP"`**: Indica que esta es la respuesta final.

### **Ejemplo 2 (Conceptual): Crear un Archivo en un Servicio Online**

**Advertencia:**  Crear archivos directamente en la PC del usuario desde una API en la nube no es un caso de uso común ni seguro. Este ejemplo es **conceptual** para ilustrar funciones más complejas que interactúan con servicios externos.

**1. Definición de la Función:**

Definiremos una función `create_online_file` que crea un archivo en un servicio de almacenamiento online (hipotético) y guarda contenido en él.

**2. Solicitud `curl` inicial a la API de Gemini (con definición de función):**

```bash
curl \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [{ "parts": [{"text": "Crea un archivo llamado 'notas.txt' y escribe 'Recordar comprar leche' en él."}]}],
    "tools": [{
      "function_declarations": [{
        "name": "create_online_file",
        "description": "Crea un archivo en un servicio de almacenamiento online y guarda contenido.",
        "parameters": {
          "type": "OBJECT",
          "properties": {
            "filename": {
              "type": "STRING",
              "description": "Nombre del archivo a crear (ej. 'notas.txt')"
            },
            "content": {
              "type": "STRING",
              "description": "Contenido del archivo"
            }
          },
          "required": ["filename", "content"]
        }
      }]
    }],
    "model": "models/gemini-2.0-flash"
  }' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"
```

**3.  Respuesta de la API (Indicando Función a Invocar):**

La API podría responder solicitando la invocación de `create_online_file` con los parámetros `filename: "notas.txt"` y `content: "Recordar comprar leche"`.

**4. Implementación de la Función `create_online_file` (Ejemplo Conceptual):**

Aquí implementarías la función que interactúa con tu servicio de almacenamiento online (esto dependería completamente de la API de tu servicio).  Podría ser algo así conceptualmente:

```python
def create_online_file(filename, content):
  """Crea un archivo en un servicio online (ejemplo conceptual)."""
  # ... (Código para autenticarse en el servicio online) ...
  # ... (Código para llamar a la API del servicio online para crear el archivo) ...
  # ... (Código para manejar errores y respuestas del servicio online) ...

  # Ejemplo simplificado (esto NO funcionaría sin la API real del servicio online)
  print(f"Archivo '{filename}' creado con contenido: '{content}' (Simulación de servicio online)")
  return f"Archivo '{filename}' creado exitosamente."

# Ejemplo de uso
file_result = create_online_file("notas.txt", "Recordar comprar leche")
print(file_result)
```

**5. Segunda Solicitud `curl` a la API de Gemini (con el resultado de la función):**

Similar al ejemplo del clima, enviarías una segunda solicitud `curl` a la API de Gemini, incluyendo el resultado de la función `create_online_file`.

**6. Respuesta Final de la API de Gemini (Respuesta al Usuario):**

La API de Gemini respondería con una confirmación al usuario, utilizando el resultado de la creación del archivo.