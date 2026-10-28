"""
Grabación de audio y transcripción local con faster-whisper.
El modelo de Whisper se carga UNA sola vez (es lento cargarlo) y se reutiliza.
"""
import os
import tempfile
import threading
import wave

import keyboard
import numpy as np
import sounddevice as sd

import config

_whisper_model = None


def _cargar_modelo():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print(f"[STT] Cargando modelo Whisper '{config.WHISPER_MODEL_SIZE}' (solo la primera vez)...")
        _whisper_model = WhisperModel(config.WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        print("[STT] Modelo Whisper listo.")
    return _whisper_model


def grabar_audio(tecla_para_detener: str, samplerate: int = 16000):
    """
    Graba audio del micrófono hasta que se vuelva a presionar `tecla_para_detener`
    o se llegue al límite de MAX_RECORDING_SECONDS.
    Devuelve la ruta a un archivo .wav temporal (o None si no se grabó nada).
    """
    print(f"[GRABANDO] Hablá ahora. Presioná '{tecla_para_detener}' de nuevo para terminar "
          f"(máx. {config.MAX_RECORDING_SECONDS}s)...")

    audio_chunks = []
    detener = threading.Event()

    def callback(indata, frames, time_info, status):
        if not detener.is_set():
            audio_chunks.append(indata.copy())

    quitar_hotkey = keyboard.add_hotkey(tecla_para_detener, detener.set)
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback):
            # Espera a que se presione la tecla de nuevo o se cumpla el tiempo máximo
            if not detener.wait(timeout=config.MAX_RECORDING_SECONDS):
                print("[GRABANDO] Se alcanzó el tiempo máximo de grabación.")
            detener.set()
    finally:
        keyboard.remove_hotkey(quitar_hotkey)

    print("[GRABANDO] Terminado. Procesando...")

    if not audio_chunks:
        return None

    audio_data = np.concatenate(audio_chunks, axis=0)

    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with wave.open(tmp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 = 2 bytes
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    return tmp_path


def transcribir(audio_path: str) -> str:
    """
    Transcribe un archivo de audio a texto usando Whisper local.
    """
    if audio_path is None or not os.path.exists(audio_path):
        return ""

    idioma = None if config.WHISPER_LANGUAGE.lower() == "auto" else config.WHISPER_LANGUAGE

    try:
        model = _cargar_modelo()
        segments, _info = model.transcribe(audio_path, language=idioma)
        texto = " ".join(segment.text.strip() for segment in segments)
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass

    return texto.strip()
