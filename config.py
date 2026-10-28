"""
Configuración central del proyecto.

Todas las variables de .env tienen un valor por defecto, así que el programa
funciona aunque no exista el archivo .env o falte alguna variable.
"""
import os
import sys
from dotenv import load_dotenv

# Carpeta del proyecto (o del .exe si se empaqueta con PyInstaller)
BASE_DIR = os.path.dirname(
    sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
)

load_dotenv(os.path.join(BASE_DIR, ".env"))


# ---------------------------------------------------------------
# Lectores con valor por defecto
# ---------------------------------------------------------------
def _get_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get_str(name, str(default)))
    except ValueError:
        print(f"[CONFIG] Valor inválido para {name}, se usa {default}")
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(_get_str(name, str(default)))
    except ValueError:
        print(f"[CONFIG] Valor inválido para {name}, se usa {default}")
        return default


def _get_bool(name: str, default: bool) -> bool:
    value = _get_str(name, "").lower()
    if value in ("1", "true", "yes", "on", "si", "sí"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    return default


# ---------------------------------------------------------------
# Modelo de lenguaje (llama.cpp)
# ---------------------------------------------------------------
_model_path = _get_str("MODEL_PATH", "models/qwen2.5-7b-instruct-q3_k_m.gguf")
MODEL_PATH = _model_path if os.path.isabs(_model_path) else os.path.join(BASE_DIR, _model_path)

N_CTX = _get_int("N_CTX", 2048)
MAX_TOKENS = _get_int("MAX_TOKENS", 512)
TEMPERATURE = _get_float("TEMPERATURE", 0.7)
ASSISTANT_LANGUAGE = _get_str("ASSISTANT_LANGUAGE", "español")

# ---------------------------------------------------------------
# Memoria de conversación
# ---------------------------------------------------------------
MEMORY_ENABLED = _get_bool("MEMORY_ENABLED", True)
MEMORY_MAX_MESSAGES = _get_int("MEMORY_MAX_MESSAGES", 10)

# ---------------------------------------------------------------
# Voz (Whisper)
# ---------------------------------------------------------------
WHISPER_MODEL_SIZE = _get_str("WHISPER_MODEL_SIZE", "base")
WHISPER_LANGUAGE = _get_str("WHISPER_LANGUAGE", "es")  # "auto" = detectar idioma
MAX_RECORDING_SECONDS = _get_int("MAX_RECORDING_SECONDS", 60)

# ---------------------------------------------------------------
# Atajos de teclado
# ---------------------------------------------------------------
HOTKEY_TEXT = _get_str("HOTKEY_TEXT", "ctrl+alt+t")
HOTKEY_VOICE = _get_str("HOTKEY_VOICE", "ctrl+alt+g")
HOTKEY_SELECTION = _get_str("HOTKEY_SELECTION", "ctrl+alt+s")
HOTKEY_SELECTION_INSTRUCTION = _get_str("HOTKEY_SELECTION_INSTRUCTION", "ctrl+alt+i")
