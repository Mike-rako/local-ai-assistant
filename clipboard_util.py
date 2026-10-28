"""
Captura el texto que el usuario tiene seleccionado en CUALQUIER aplicación
(navegador, Word, PDF, editor de texto, etc.), simulando Ctrl+C y leyendo
el portapapeles. Restaura el portapapeles original al terminar, para no
pisar lo que el usuario tenía copiado antes.
"""
import time, keyboard, pyperclip


def obtener_texto_seleccionado(espera: float = 0.3) -> str:
    """
    Simula Ctrl+C sobre la selección actual y devuelve el texto copiado.
    Restaura el contenido previo del portapapeles al finalizar.
    """
    # Guardamos lo que había antes en el portapapeles, si algo
    try:
        contenido_previo = pyperclip.paste()
    except Exception:
        contenido_previo = ""

    # Ponemos un valor "centinela" para detectar si realmente se copió algo nuevo
    centinela = "\x00__SIN_SELECCION__\x00"
    pyperclip.copy(centinela)

    # IMPORTANTE: como esta función se dispara desde un atajo tipo Ctrl+Alt+S,
    # el sistema todavía puede "creer" que Ctrl y Alt siguen presionados.
    # Si mandamos Ctrl+C en ese estado, en realidad se envía Ctrl+Alt+C (no copia nada).
    # Por eso soltamos explícitamente los modificadores antes de copiar.
    for tecla in ("alt", "ctrl", "shift"):
        try:
            keyboard.release(tecla)
        except Exception:
            pass

    time.sleep(0.05)  # pequeño respiro para que el sistema registre que se soltaron
    keyboard.send("ctrl+c")
    time.sleep(espera)  # darle tiempo al sistema a completar la copia

    texto_copiado = pyperclip.paste()

    # Restauramos el portapapeles original para no pisar lo que el usuario tenía
    try:
        pyperclip.copy(contenido_previo)
    except Exception:
        pass

    if texto_copiado == centinela:
        return ""  # no había nada seleccionado

    return texto_copiado.strip()