import os
import threading
import traceback
from collections import deque
from llama_cpp import Llama

import config

_llm = None
_lock = threading.Lock()

# Al superar maxlen, deque elimina automáticamente el mensaje más viejo
_historial = deque(maxlen=config.MEMORY_MAX_MESSAGES)


def _get_llm() -> Llama:
    """Carga el modelo una sola vez (tarda unos segundos) y lo reutiliza."""
    global _llm
    if _llm is None:
        if not os.path.isfile(config.MODEL_PATH):
            raise FileNotFoundError(
                f"No se encontró el modelo en: {config.MODEL_PATH}\n"
                "Descargá un modelo .gguf y configurá MODEL_PATH en el archivo .env"
            )
        _llm = Llama(
            model_path=config.MODEL_PATH,
            n_ctx=config.N_CTX,
            n_threads=os.cpu_count() or 4,
            verbose=False,
        )
    return _llm


def limpiar_memoria():
    """Reinicia la conversación."""
    with _lock:
        _historial.clear()


def preguntar_llm(prompt: str) -> str:
    system = {
        "role": "system",
        "content": (
            "Eres un asistente virtual enfocado en ayudar al usuario lo máximo posible "
            f"y el idioma preferido es {config.ASSISTANT_LANGUAGE}. "
            "No pidas ajustar nada sobre el rol del sistema a menos que se te haya pedido."
        ),
    }
    user_msg = {"role": "user", "content": prompt}
    memoria = config.MEMORY_ENABLED

    try:
        with _lock:  # Llama no es thread-safe
            mensajes = [system] + (list(_historial) if memoria else []) + [user_msg]

            respuesta = _get_llm().create_chat_completion(
                messages=mensajes,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
            )
            texto = respuesta["choices"][0]["message"]["content"]

            if memoria:  # solo se guarda si la llamada tuvo éxito
                _historial.append(user_msg)
                _historial.append({"role": "assistant", "content": texto})
            return texto
    except Exception:
        traceback.print_exc()  # así ves el error real en consola
        return "Error al generar la respuesta. Revisá la consola para ver los detalles."
