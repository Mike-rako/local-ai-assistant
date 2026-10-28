# Asistente de IA local

🌐 [English](README.md) | **Español**

Asistente de inteligencia artificial que corre **100 % en tu computadora**, sin servidores ni cuentas externas. Se queda en segundo plano y lo invocas con atajos de teclado desde cualquier aplicación: navegador, Word, PDF, editor de texto, etc.

- **Modelo de lenguaje:** [llama.cpp](https://github.com/ggerganov/llama.cpp) (vía `llama-cpp-python`) con cualquier modelo `.gguf`.
- **Voz a texto:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper), también local.
- **Interfaz:** ventanas minimalistas en tema oscuro hechas con `tkinter` (sin dependencias extra).

## Qué puedes hacer

| Atajo (por defecto) | Acción |
|---|---|
| `Ctrl+Alt+T` | Escribir una pregunta en un cuadro de texto |
| `Ctrl+Alt+G` | Preguntar por voz (presiona el mismo atajo otra vez para terminar de grabar) |
| `Ctrl+Alt+S` | Enviar a la IA el texto que tengas seleccionado en cualquier app |
| `Ctrl+Alt+I` | Enviar el texto seleccionado junto con una instrucción (por ejemplo: "resume esto", "traduce al inglés") |

Todos los atajos se pueden cambiar en el archivo `.env`.

## Requisitos

- **Python 3.9 o superior**
- **Windows** (recomendado). La librería `keyboard` necesita permisos de administrador en Windows y de root en Linux, y en macOS prácticamente no funciona.
- Un micrófono (solo para la función de voz).
- Un modelo `.gguf`. Como referencia, un modelo de 7B cuantizado a 3 bits ocupa unos 4 GB en disco y necesita varios GB de RAM libres.
- En Linux, además: `sudo apt install python3-tk`.

## Instalación

**1. Clona el repositorio**

```bash
git clone https://github.com/Mike-rako/local-ai-assistant.git
cd local-ai-assistant
```

**2. (Recomendado) Crea un entorno virtual**

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux
```

**3. Instala las dependencias**

```bash
pip install -r requirements.txt
```

> `llama-cpp-python` se compila al instalarse, y en Windows eso puede requerir las "Build Tools" de Visual Studio. Si falla, puedes instalar una versión precompilada para CPU:
>
> ```bash
> pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
> ```

**4. Descarga un modelo `.gguf` (obligatorio)**

> ⚠️ **Este repositorio NO incluye ningún modelo de IA**, porque pesan varios GB. Debes descargar uno tú mismo; sin él, el programa no puede responder.

1. Elige un modelo de chat en formato GGUF. Estos repositorios están verificados y funcionan con este proyecto (revisa en Hugging Face si hay versiones más nuevas):

   | Modelo | Enlace | Archivo a descargar | Tamaño | Licencia | Para quién |
   |---|---|---|---|---|---|
   | Qwen2.5 1.5B Instruct | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | `qwen2.5-1.5b-instruct-q4_k_m.gguf` | ~1 GB | Apache 2.0 | Equipos con poca RAM; rápido pero más básico |
   | Qwen2.5 3B Instruct | [Qwen/Qwen2.5-3B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) | `qwen2.5-3b-instruct-q4_k_m.gguf` | ~2,1 GB | Qwen Research (no comercial) | Buen equilibrio entre calidad y velocidad |
   | Qwen2.5 7B Instruct | [Qwen/Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF) | `qwen2.5-7b-instruct-q3_k_m.gguf` | ~3,8 GB | Apache 2.0 | Mejores respuestas; más lento y exige más RAM (**modelo por defecto de este proyecto**) |

   Cada repositorio tiene varios archivos `.gguf` con distintas cuantizaciones (archivos más pequeños = menor calidad). Descarga **solo un** archivo. Ten cuidado con los archivos cuyo nombre termina en `-00001-of-0000X.gguf`: el modelo está dividido en varias partes que hay que unir antes de usarlo. Los archivos de la tabla son de una sola pieza, así que funcionan tal cual. Cualquier otro modelo de chat en formato GGUF también sirve.

2. Abre el enlace del modelo que elegiste, entra a la pestaña **Files and versions** y descarga el archivo `.gguf` indicado en la tabla.

3. Guarda el archivo en la carpeta `models/` del proyecto. Si la carpeta no existe, créala.

4. Indica el nombre del archivo en tu `.env`. El programa busca por defecto `models/qwen2.5-7b-instruct-q3_k_m.gguf`, así que, si descargaste otro modelo, **debes** ajustar `MODEL_PATH`:

   ```env
   MODEL_PATH=models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

   Si aún no creaste el `.env`, hazlo en el paso siguiente y luego edita esa línea (ver [Configuración](#configuración)).

**5. (Opcional) Crea tu archivo de configuración**

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux
```

No es obligatorio: todas las variables tienen un valor por defecto, así que el programa funciona sin `.env`.

## Uso

```bash
python main.py
```

En Windows, **ejecuta la terminal como administrador** para que los atajos globales funcionen en todas las aplicaciones. Deja la ventana de consola abierta mientras uses el asistente; para salir, ciérrala.

Notas:
- La **primera respuesta** tarda unos segundos porque se carga el modelo en memoria.
- La **primera vez que uses la voz**, faster-whisper descarga su modelo (se necesita internet solo esa vez).

## Configuración

Todas las variables son opcionales y se definen en el archivo `.env` (puedes partir de `.env.example`).

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `MODEL_PATH` | `models/qwen2.5-7b-instruct-q3_k_m.gguf` | Ruta al modelo `.gguf` (relativa al proyecto o absoluta) |
| `N_CTX` | `2048` | Tamaño de contexto del modelo, en tokens |
| `MAX_TOKENS` | `512` | Longitud máxima de cada respuesta |
| `TEMPERATURE` | `0.7` | Creatividad de las respuestas (más bajo = más predecible) |
| `ASSISTANT_LANGUAGE` | `español` | Idioma preferido de las respuestas |
| `MEMORY_ENABLED` | `true` | Si el asistente recuerda la conversación |
| `MEMORY_MAX_MESSAGES` | `10` | Mensajes que se recuerdan (cuentan preguntas y respuestas) |
| `WHISPER_MODEL_SIZE` | `base` | Tamaño del modelo de voz: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_LANGUAGE` | `es` | Idioma de la voz (`es`, `en`, ...) o `auto` para detectarlo |
| `MAX_RECORDING_SECONDS` | `60` | Duración máxima de una grabación |
| `HOTKEY_TEXT` | `ctrl+alt+t` | Atajo para preguntar por texto |
| `HOTKEY_VOICE` | `ctrl+alt+g` | Atajo para preguntar por voz |
| `HOTKEY_SELECTION` | `ctrl+alt+s` | Atajo para enviar el texto seleccionado |
| `HOTKEY_SELECTION_INSTRUCTION` | `ctrl+alt+i` | Atajo para texto seleccionado + instrucción |

## Estructura del proyecto

```
├── main.py             # Programa principal y atajos de teclado
├── config.py           # Lectura del .env con valores por defecto
├── llm_client.py       # Carga del modelo y chat con memoria
├── stt.py              # Grabación de audio y transcripción (Whisper)
├── clipboard_util.py   # Captura del texto seleccionado en cualquier app
├── ui.py               # Ventanas de entrada y respuesta (tkinter)
├── requirements.txt
├── .env.example        # Plantilla de configuración
└── models/             # Aquí va tu modelo .gguf (no se sube a Git)
```

## Privacidad

- Todo se procesa en tu equipo: el modelo, la transcripción de voz y las respuestas. El programa no envía datos a ningún servidor.
- Para capturar el texto seleccionado, la app simula `Ctrl+C` y lee el portapapeles; después **restaura** lo que tenías copiado antes.
- El audio grabado se guarda en un archivo temporal y se borra al terminar de transcribirlo.
- Se necesita internet únicamente para descargar el modelo `.gguf` y, la primera vez, el modelo de Whisper.

## Solución de problemas

| Problema | Posible solución |
|---|---|
| Los atajos no responden en algunas apps | Ejecuta la terminal como administrador |
| `No se encontró el modelo en: ...` | Revisa que el `.gguf` esté en `models/` o corrige `MODEL_PATH` en `.env` |
| Error al instalar `llama-cpp-python` | Usa la instalación precompilada (ver paso 3) o instala las Build Tools de Visual Studio |
| El atajo de selección no copia nada | Asegúrate de tener el texto seleccionado antes de presionar el atajo |
| Respuestas muy lentas | Usa un modelo más pequeño o una cuantización más ligera, o reduce `MAX_TOKENS` |
| La voz no se transcribe bien | Prueba `WHISPER_MODEL_SIZE=small` o revisa tu micrófono predeterminado |

## Licencia

Distribuido bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.