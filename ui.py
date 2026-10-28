"""
Ventanas de entrada/salida de texto con un look moderno y minimalista
(tema oscuro, tipografia limpia), usando solo tkinter estandar
(no necesita instalar nada extra).

IMPORTANTE - HILOS:
Tkinter solo puede crear/manipular ventanas desde el hilo principal del
programa. Como los atajos de teclado disparan las acciones en hilos de
trabajo (threading.Thread) para no bloquear la escucha de atajos, este
modulo usa un "puente": las funciones publicas (pedir_texto, mostrar_respuesta)
pueden llamarse desde CUALQUIER hilo. Si no estan en el hilo principal,
encolan el pedido y el hilo principal (que corre root.mainloop() en main.py)
lo ejecuta por ellas, devolviendo el resultado de vuelta.

Antes de usar este modulo hay que llamar una vez a iniciar(root) desde
el hilo principal (main.py ya lo hace).
"""
import tkinter as tk
from tkinter import font as tkfont
import textwrap
import threading
import queue

# ---------------------------------------------------------------
# Paleta de colores (tema oscuro minimalista)
# ---------------------------------------------------------------
BG = "#1e1f26"          # fondo principal
BG_PANEL = "#262832"    # fondo de campos/paneles
FG = "#e6e6e6"          # texto principal
FG_MUTED = "#8a8d98"    # texto secundario
ACCENT = "#7c9cff"      # color de acento (boton principal)
ACCENT_HOVER = "#6a89ee"
BORDER = "#33353f"

# Limites para el auto-ajuste de tamano de la ventana de respuesta
RESP_ANCHO_MIN, RESP_ANCHO_MAX = 380, 720
RESP_ALTO_MIN, RESP_ALTO_MAX = 220, 720
RESP_ALTO_COLECTADO = 190  # alto de la vista "colapsada" (2 lineas + botones)

# Esquina de pantalla donde aparecen SIEMPRE las ventanas (pregunta y respuesta)
# Opciones: "top-right", "top-left", "bottom-right", "bottom-left"
ESQUINA = "top-right"
MARGEN_X = 40
MARGEN_Y = 50


# =================================================================
# PUENTE ENTRE HILOS (ver nota IMPORTANTE arriba)
# =================================================================
_root = None
_cola_tareas = queue.Queue()


def iniciar(root):
    """Debe llamarse UNA vez desde main.py, en el hilo principal, pasando el root de tkinter."""
    global _root
    _root = root
    _procesar_cola()  # arranca el ciclo de revisión de la cola


def _procesar_cola():
    """Revisa si hay pedidos de ventanas encolados por otros hilos y los ejecuta. Corre en el hilo principal."""
    try:
        while True:
            tarea = _cola_tareas.get_nowait()
            tarea()
    except queue.Empty:
        pass
    if _root is not None:
        _root.after(50, _procesar_cola)


def _ejecutar_en_hilo_principal(func, *args, **kwargs):
    """
    Ejecuta func(*args, **kwargs) en el hilo principal (donde vive tkinter)
    y devuelve su resultado, sin importar desde qué hilo se la llame.
    """
    if threading.current_thread() is threading.main_thread():
        return func(*args, **kwargs)

    evento = threading.Event()
    contenedor = {}

    def tarea():
        try:
            contenedor["valor"] = func(*args, **kwargs)
        except Exception as e:
            contenedor["error"] = e
        finally:
            evento.set()

    _cola_tareas.put(tarea)
    evento.wait()

    if "error" in contenedor:
        raise contenedor["error"]
    return contenedor.get("valor")


# =================================================================
# UTILIDADES DE ESTILO
# =================================================================
def _posicionar_en_esquina(win, ancho, alto):
    """Coloca la ventana en la esquina configurada, con margen fijo."""
    win.update_idletasks()
    pantalla_w = win.winfo_screenwidth()
    pantalla_h = win.winfo_screenheight()

    if ESQUINA == "top-right":
        x = pantalla_w - ancho - MARGEN_X
        y = MARGEN_Y
    elif ESQUINA == "top-left":
        x = MARGEN_X
        y = MARGEN_Y
    elif ESQUINA == "bottom-right":
        x = pantalla_w - ancho - MARGEN_X
        y = pantalla_h - alto - MARGEN_Y
    else:  # bottom-left
        x = MARGEN_X
        y = pantalla_h - alto - MARGEN_Y

    win.geometry(f"{ancho}x{alto}+{x}+{y}")


def _fuente(tam=10, negrita=False):
    return tkfont.Font(family="Segoe UI", size=tam, weight="bold" if negrita else "normal")


# =================================================================
# VENTANA: pedir texto
# =================================================================
def _pedir_texto_impl(titulo: str) -> str:
    resultado = {"valor": None}

    win = tk.Toplevel(_root)
    win.overrideredirect(True)
    win.configure(bg=BG)
    win.attributes("-topmost", True)

    ancho, alto = 460, 210
    _posicionar_en_esquina(win, ancho, alto)

    borde = tk.Frame(win, bg=BORDER)
    borde.pack(fill="both", expand=True, padx=1, pady=1)
    contenedor = tk.Frame(borde, bg=BG)
    contenedor.pack(fill="both", expand=True)

    # 1) Barra superior (arriba)
    barra = tk.Frame(contenedor, bg=BG, height=32)
    barra.pack(side="top", fill="x", padx=14, pady=(10, 0))

    tk.Label(barra, text=titulo, bg=BG, fg=FG_MUTED, font=_fuente(8)).pack(side="left")

    def cerrar_cancelar():
        resultado["valor"] = None
        win.destroy()

    btn_cerrar = tk.Label(barra, text="\u2715", bg=BG, fg=FG_MUTED, font=_fuente(9), cursor="hand2")
    btn_cerrar.pack(side="right")
    btn_cerrar.bind("<Button-1>", lambda e: cerrar_cancelar())

    offset_x = offset_y = 0

    def _mover(event):
        win.geometry(f"+{event.x_root - offset_x}+{event.y_root - offset_y}")

    def _iniciar_mover(event):
        nonlocal offset_x, offset_y
        offset_x, offset_y = event.x, event.y

    barra.bind("<Button-1>", _iniciar_mover)
    barra.bind("<B1-Motion>", _mover)

    # 2) Pie de botones (abajo) — se empaqueta ANTES que el campo de texto
    #    para que siempre tenga su espacio reservado, sin importar el alto.
    pie = tk.Frame(contenedor, bg=BG)
    pie.pack(side="bottom", fill="x", padx=14, pady=(0, 12))

    tk.Label(pie, text="Enter enviar - Shift+Enter linea - Esc cancelar",
             bg=BG, fg=FG_MUTED, font=_fuente(7)).pack(side="left")

    def confirmar():
        resultado["valor"] = texto.get("1.0", "end").strip()
        win.destroy()

    btn = tk.Label(pie, text="Enviar  \u2192", bg=ACCENT, fg="#101116", font=_fuente(8, negrita=True),
                   cursor="hand2", padx=12, pady=5)
    btn.pack(side="right")
    btn.bind("<Button-1>", lambda e: confirmar())
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))

    # 3) Campo de texto (ocupa lo que sobra en el medio)
    campo_frame = tk.Frame(contenedor, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER)
    campo_frame.pack(side="top", fill="both", expand=True, padx=14, pady=14)

    texto = tk.Text(
        campo_frame, bg=BG_PANEL, fg=FG, insertbackground=ACCENT,
        font=_fuente(11), wrap="word", relief="flat", padx=12, pady=10,
        highlightthickness=0, borderwidth=0,
    )
    texto.pack(fill="both", expand=True)

    def on_key(event):
        if event.keysym == "Return" and not (event.state & 0x0001):
            confirmar()
            return "break"
        if event.keysym == "Escape":
            cerrar_cancelar()

    texto.bind("<Key>", on_key)

    # Forzar que la ventana quede al frente y se robe el foco de teclado,
    # sin importar en que app estabas escribiendo antes.
    win.lift()
    win.attributes("-topmost", True)
    win.focus_force()
    texto.focus_force()

    _root.wait_window(win)  # bloquea (sin trabar el resto de la app) hasta que se cierre
    return resultado["valor"]


def pedir_texto(titulo: str = "Preguntar a la IA") -> str:
    return _ejecutar_en_hilo_principal(_pedir_texto_impl, titulo)


# =================================================================
# VENTANA: mostrar respuesta
# =================================================================
def _calcular_tamano_respuesta(texto: str):
    """
    Calcula un ancho/alto razonable para que la ventana se ajuste al texto
    completo (usado en la vista expandida), dentro de limites min/max.
    """
    PADDING_EXTRA_ALTO = 150
    PADDING_EXTRA_ANCHO = 60
    CHAR_ANCHO_APROX = 6.8  # ancho aproximado por caracter con Segoe UI 10

    if not texto:
        return RESP_ANCHO_MIN, RESP_ALTO_MIN

    lineas = texto.split("\n")
    linea_mas_larga = max((len(l) for l in lineas), default=0)

    ancho_estimado = int(linea_mas_larga * CHAR_ANCHO_APROX) + PADDING_EXTRA_ANCHO
    ancho = max(RESP_ANCHO_MIN, min(RESP_ANCHO_MAX, ancho_estimado))

    caracteres_por_linea = max(10, int((ancho - PADDING_EXTRA_ANCHO) / CHAR_ANCHO_APROX))
    lineas_totales = 0
    for l in lineas:
        if len(l) == 0:
            lineas_totales += 1
        else:
            lineas_totales += -(-len(l) // caracteres_por_linea)

    alto_estimado = lineas_totales * 18 + PADDING_EXTRA_ALTO
    alto = max(RESP_ALTO_MIN, min(RESP_ALTO_MAX, alto_estimado))

    return ancho, alto


def _texto_preview(texto: str, ancho: int, n_lineas: int = 2):
    """Devuelve solo las primeras n_lineas del texto ya envueltas (wrap), y si quedo truncado."""
    PADDING_EXTRA_ANCHO = 60
    CHAR_ANCHO_APROX = 6.8
    caracteres_por_linea = max(10, int((ancho - PADDING_EXTRA_ANCHO) / CHAR_ANCHO_APROX))

    lineas_envueltas = []
    for parrafo in texto.split("\n"):
        if parrafo == "":
            lineas_envueltas.append("")
        else:
            lineas_envueltas.extend(textwrap.wrap(parrafo, width=caracteres_por_linea) or [""])

    truncado = len(lineas_envueltas) > n_lineas
    preview = "\n".join(lineas_envueltas[:n_lineas])
    return preview, truncado


def _mostrar_respuesta_impl(respuesta: str, titulo: str):
    # Siempre mostramos la respuesta completa en consola tambien
    print("\n[RESPUESTA IA]")
    print(respuesta)
    print()

    win = tk.Toplevel(_root)
    win.overrideredirect(True)
    win.configure(bg=BG)
    win.attributes("-topmost", True)

    ancho_final, alto_final = _calcular_tamano_respuesta(respuesta)
    preview, truncado = _texto_preview(respuesta, ancho_final, n_lineas=2)

    ancho_actual = ancho_final
    alto_colapsado = RESP_ALTO_COLECTADO
    alto_actual = alto_colapsado if truncado else min(alto_final, RESP_ALTO_MAX)

    win.withdraw()
    _posicionar_en_esquina(win, ancho_actual, alto_actual)

    borde = tk.Frame(win, bg=BORDER)
    borde.pack(fill="both", expand=True, padx=1, pady=1)
    contenedor = tk.Frame(borde, bg=BG)
    contenedor.pack(fill="both", expand=True)

    # 1) Barra superior (arriba)
    barra = tk.Frame(contenedor, bg=BG, height=32)
    barra.pack(side="top", fill="x", padx=14, pady=(10, 0))

    tk.Label(barra, text=titulo, bg=BG, fg=FG_MUTED, font=_fuente(8)).pack(side="left")

    btn_cerrar = tk.Label(barra, text="\u2715", bg=BG, fg=FG_MUTED, font=_fuente(9), cursor="hand2")
    btn_cerrar.pack(side="right")
    btn_cerrar.bind("<Button-1>", lambda e: win.destroy())

    offset_x = offset_y = 0

    def _mover(event):
        win.geometry(f"+{event.x_root - offset_x}+{event.y_root - offset_y}")

    def _iniciar_mover(event):
        nonlocal offset_x, offset_y
        offset_x, offset_y = event.x, event.y

    barra.bind("<Button-1>", _iniciar_mover)
    barra.bind("<B1-Motion>", _mover)

    # 2) Pie de botones (abajo) — SIEMPRE visible, en colapsado y expandido.
    #    Se empaqueta ANTES que el area de texto para que nunca pierda su espacio.
    pie = tk.Frame(contenedor, bg=BG)
    pie.pack(side="bottom", fill="x", padx=14, pady=(0, 12))

    def copiar():
        win.clipboard_clear()
        win.clipboard_append(respuesta)
        etiqueta_copiado.config(text="\u2713 Copiado")
        win.after(1500, lambda: etiqueta_copiado.config(text=""))

    etiqueta_copiado = tk.Label(pie, text="", bg=BG, fg=ACCENT, font=_fuente(7))
    etiqueta_copiado.pack(side="left")

    btn_copiar = tk.Label(pie, text="Copiar", bg=BG_PANEL, fg=FG, font=_fuente(8),
                           cursor="hand2", padx=12, pady=5, highlightthickness=1,
                           highlightbackground=BORDER)
    btn_copiar.pack(side="right", padx=(8, 0))
    btn_copiar.bind("<Button-1>", lambda e: copiar())

    btn_cerrar2 = tk.Label(pie, text="Cerrar", bg=ACCENT, fg="#101116", font=_fuente(8, negrita=True),
                            cursor="hand2", padx=12, pady=5)
    btn_cerrar2.pack(side="right")
    btn_cerrar2.bind("<Button-1>", lambda e: win.destroy())
    btn_cerrar2.bind("<Enter>", lambda e: btn_cerrar2.config(bg=ACCENT_HOVER))
    btn_cerrar2.bind("<Leave>", lambda e: btn_cerrar2.config(bg=ACCENT))

    # 3) Area de texto (ocupa lo que sobra en el medio)
    campo_frame = tk.Frame(contenedor, bg=BG_PANEL, highlightthickness=1, highlightbackground=BORDER)
    campo_frame.pack(side="top", fill="both", expand=True, padx=14, pady=14)

    scrollbar = tk.Scrollbar(campo_frame, bg=BG_PANEL, troughcolor=BG, borderwidth=0)

    texto_widget = tk.Text(
        campo_frame, bg=BG_PANEL, fg=FG, font=_fuente(10), wrap="word",
        relief="flat", padx=12, pady=10, highlightthickness=0, borderwidth=0,
        yscrollcommand=scrollbar.set,
    )
    texto_widget.pack(fill="both", expand=True, side="left")
    scrollbar.config(command=texto_widget.yview)

    estado = {"expandido": not truncado}

    def _set_contenido(mostrar_completo: bool):
        texto_widget.config(state="normal")
        texto_widget.delete("1.0", "end")
        texto_widget.insert("1.0", respuesta if mostrar_completo else preview)
        texto_widget.config(state="disabled")
        if mostrar_completo:
            scrollbar.pack(side="right", fill="y")
        else:
            scrollbar.pack_forget()

    _set_contenido(estado["expandido"])

    # Boton "Mostrar mas/menos" — se agrega en el pie, al lado izquierdo de Copiar
    if truncado:
        def alternar_expandir():
            estado["expandido"] = not estado["expandido"]
            nuevo_alto = min(alto_final, RESP_ALTO_MAX) if estado["expandido"] else alto_colapsado
            _set_contenido(estado["expandido"])
            _posicionar_en_esquina(win, ancho_actual, nuevo_alto)
            btn_expandir.config(text="Mostrar menos" if estado["expandido"] else "Mostrar mas \u2193")

        btn_expandir = tk.Label(pie, text="Mostrar mas \u2193", bg=BG_PANEL, fg=ACCENT, font=_fuente(8),
                                 cursor="hand2", padx=10, pady=5, highlightthickness=1,
                                 highlightbackground=BORDER)
        btn_expandir.pack(side="left", padx=(10, 0))
        btn_expandir.bind("<Button-1>", lambda e: alternar_expandir())

    win.bind("<Escape>", lambda e: win.destroy())

    win.deiconify()
    win.lift()
    win.attributes("-topmost", True)
    win.focus_force()

    _root.wait_window(win)


def mostrar_respuesta(respuesta: str, titulo: str = "Respuesta de la IA"):
    _ejecutar_en_hilo_principal(_mostrar_respuesta_impl, respuesta, titulo)


def notificar(mensaje: str):
    """Notificacion simple no bloqueante. Segura de llamar desde cualquier hilo (solo imprime)."""
    print(f"[NOTIFICACION] {mensaje}")