"""
Asistente de IA local (llama.cpp + Whisper) — programa principal.

Corre en segundo plano y escucha 4 atajos de teclado:

1. HOTKEY_TEXT                   -> escribís una pregunta en un cuadro de texto,
                                    se envía al modelo local, se muestra la respuesta.
2. HOTKEY_VOICE                  -> grabás tu voz, se transcribe local, se envía
                                    al modelo, se muestra la respuesta.
3. HOTKEY_SELECTION              -> seleccionás texto en cualquier app y se manda
                                    directo a la IA.
4. HOTKEY_SELECTION_INSTRUCTION  -> seleccionás texto, escribís una instrucción,
                                    y se manda instrucción + texto seleccionado juntos.

Todo corre en tu máquina: no se conecta a ningún servidor.

IMPORTANTE: en Windows, conviene correr este script como Administrador para
que los atajos globales funcionen de forma confiable en todas las apps.
"""
import threading
import tkinter as tk

import keyboard

import clipboard_util
import config
import stt
import ui
from llm_client import preguntar_llm

# Evita que al presionar el mismo atajo por segunda vez (para PARAR la
# grabación) se dispare una nueva acción en paralelo por error.
_ocupado = {"voz_pregunta": False, "seleccion": False, "seleccion_instruccion": False}


def accion_texto():
    """Punto 1: preguntar por texto."""
    pregunta = ui.pedir_texto("Preguntar a la IA (texto)")
    if not pregunta:
        return
    ui.notificar("Pensando...")
    respuesta = preguntar_llm(pregunta)
    ui.mostrar_respuesta(respuesta)


def accion_voz_pregunta():
    """Punto 2: preguntar por voz."""
    if _ocupado["voz_pregunta"]:
        return  # ya hay una grabación/procesamiento en curso, ignorar
    _ocupado["voz_pregunta"] = True
    try:
        audio_path = stt.grabar_audio(tecla_para_detener=config.HOTKEY_VOICE)
        ui.notificar("Transcribiendo...")
        texto = stt.transcribir(audio_path)

        if not texto:
            ui.notificar("No se detectó voz.")
            return

        ui.notificar(f"Vos dijiste: {texto}")
        ui.notificar("Pensando...")
        respuesta = preguntar_llm(texto)
        ui.mostrar_respuesta(respuesta, titulo=f"Pregunta: {texto[:50]}")
    finally:
        _ocupado["voz_pregunta"] = False


def accion_texto_seleccionado():
    """
    Punto 3A: seleccionás texto en cualquier app, presionás el atajo,
    y ese texto se manda directo a la IA.
    """
    if _ocupado["seleccion"]:
        return
    _ocupado["seleccion"] = True
    try:
        texto = clipboard_util.obtener_texto_seleccionado()

        if not texto:
            ui.notificar("No hay texto seleccionado.")
            return

        ui.notificar("Pensando...")
        respuesta = preguntar_llm(texto)
        ui.mostrar_respuesta(respuesta, titulo="Respuesta sobre el texto seleccionado")
    finally:
        _ocupado["seleccion"] = False


def accion_seleccion_con_instruccion():
    """
    Punto 3B: seleccionás texto, presionás el atajo, se abre una ventana
    para escribir una instrucción, y se manda instrucción + texto seleccionado
    juntos a la IA.
    """
    if _ocupado["seleccion_instruccion"]:
        return
    _ocupado["seleccion_instruccion"] = True
    try:
        texto_seleccionado = clipboard_util.obtener_texto_seleccionado()

        if not texto_seleccionado:
            ui.notificar("No hay texto seleccionado.")
            return

        instruccion = ui.pedir_texto("¿Qué querés hacer con el texto seleccionado?")
        if not instruccion:
            return

        prompt_final = (
            f"Instrucción: {instruccion}\n\n"
            f"Texto seleccionado:\n\"\"\"\n{texto_seleccionado}\n\"\"\""
        )

        ui.notificar("Pensando...")
        respuesta = preguntar_llm(prompt_final)
        ui.mostrar_respuesta(respuesta, titulo=f"Instrucción: {instruccion[:50]}")
    finally:
        _ocupado["seleccion_instruccion"] = False


def _lanzar(accion):
    """Ejecuta una acción en su propio hilo para no bloquear la escucha de atajos."""
    threading.Thread(target=accion, daemon=True).start()


def main():
    print("=" * 60)
    print("Asistente de IA local — corriendo en segundo plano")
    print("=" * 60)
    print(f"Modelo:  {config.MODEL_PATH}")
    print(f"Whisper: {config.WHISPER_MODEL_SIZE} ({config.WHISPER_LANGUAGE})")
    print(f"Memoria: {'activada' if config.MEMORY_ENABLED else 'desactivada'}")
    print()
    print(f"[{config.HOTKEY_TEXT}] -> Preguntar por texto")
    print(f"[{config.HOTKEY_VOICE}] -> Preguntar por voz")
    print(f"[{config.HOTKEY_SELECTION}] -> Enviar texto seleccionado a la IA")
    print(f"[{config.HOTKEY_SELECTION_INSTRUCTION}] -> Texto seleccionado + instrucción extra")
    print()
    print("Dejá esta ventana abierta mientras usás los atajos.")
    print("=" * 60)

    keyboard.add_hotkey(config.HOTKEY_TEXT, lambda: _lanzar(accion_texto))
    keyboard.add_hotkey(config.HOTKEY_VOICE, lambda: _lanzar(accion_voz_pregunta))
    keyboard.add_hotkey(config.HOTKEY_SELECTION, lambda: _lanzar(accion_texto_seleccionado))
    keyboard.add_hotkey(config.HOTKEY_SELECTION_INSTRUCTION, lambda: _lanzar(accion_seleccion_con_instruccion))

    # IMPORTANTE: tkinter solo puede crear ventanas desde el hilo principal.
    # Creamos un root oculto que vive todo el programa, y usamos su mainloop
    # como el "loop principal" del programa (reemplaza a keyboard.wait()).
    # Los hilos de trabajo le piden ventanas a este root a través de ui.py.
    root = tk.Tk()
    root.withdraw()  # nunca se muestra, es solo el motor de tkinter
    ui.iniciar(root)

    print("(Para salir: cerrá esta ventana de consola)")
    root.mainloop()


if __name__ == "__main__":
    main()
