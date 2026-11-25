"""Genera Presentacion_estados.pptx (requiere python-pptx; diagramas con Graphviz)."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

NAVY = RGBColor(0x1F, 0x2A, 0x44); GOLD = RGBColor(0xB0, 0x7A, 0x00); GREEN = RGBColor(0x1E, 0x7A, 0x4C)
GRAY = RGBColor(0x44, 0x4F, 0x60); LIGHT = RGBColor(0xEE, 0xF2, 0xF7); WHITE = RGBColor(255, 255, 255)
FONT = "Liberation Sans"

prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

def text(slide, x, y, w, h, paras, size=18, color=GRAY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    if isinstance(paras, str): paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(p, tuple): p, opts = p
        else: opts = {}
        run = para.add_run(); run.text = p; f = run.font
        f.name = FONT; f.size = Pt(opts.get("size", size)); f.bold = opts.get("bold", bold)
        f.color.rgb = opts.get("color", color); para.alignment = align; para.space_after = Pt(opts.get("after", 6))
    return tb

def base(title, n, accent=NAVY):
    s = prs.slides.add_slide(blank)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.0))
    bar.fill.solid(); bar.fill.fore_color.rgb = accent; bar.line.fill.background()
    text(s, 0.5, 0.12, 12.3, 0.8, title, size=30, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 12.2, 7.05, 0.9, 0.35, str(n), size=12, align=PP_ALIGN.RIGHT)
    return s

def picture(s, path, x, y, w, h):
    iw, ih = Image.open(path).size; r = min(w / iw, h / ih)
    pw, ph = iw * r, ih * r
    s.shapes.add_picture(path, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))

def table(s, x, y, w, rows, widths, size=14, head=NAVY, rowh=0.5):
    t = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(rowh * len(rows))).table
    for j, cw in enumerate(widths): t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.text = ""; c.margin_left = c.margin_right = Inches(0.08)
            r = c.text_frame.paragraphs[0].add_run(); r.text = val; r.font.name = FONT; r.font.size = Pt(size)
            c.text_frame.word_wrap = True
            c.fill.solid()
            if i == 0: c.fill.fore_color.rgb = head; r.font.color.rgb = WHITE; r.font.bold = True
            else: c.fill.fore_color.rgb = LIGHT if i % 2 else WHITE; r.font.color.rgb = GRAY
    return t


def legend(s, x, y, w, items, size=12):
    """items: (color, dash, texto). Dibuja una leyenda de tipos de flecha."""
    from pptx.enum.dml import MSO_LINE
    n = len(items); cw = w / n
    for i, (col, dash, txt) in enumerate(items):
        cx = x + i * cw
        ln = s.shapes.add_connector(1, Inches(cx), Inches(y + 0.18), Inches(cx + 0.7), Inches(y + 0.18))
        ln.line.color.rgb = col; ln.line.width = Pt(2.5)
        if dash: ln.line.dash_style = MSO_LINE.DASH
        text(s, cx + 0.78, y - 0.02, cw - 0.85, 0.7, txt, size=size)

LEG = [
    (GRAY, False, "Continua: secuencia normal, confirmada por sensores u órdenes"),
    (RGBColor(0xA0, 0x20, 0x20), True, "Punteada roja: entrada a FALLO (condición insegura; prioridad máxima, desde cualquier fase)"),
    (GRAY, True, "Punteada gris: transición de prioridad por orden (stop) o recuperación (reset desde FALLO)"),
]

def notes(s, t): s.notes_slide.notes_text_frame.text = t

# 1 Portada
s = prs.slides.add_slide(blank)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height); bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
text(s, 0.8, 2.2, 11.7, 1.6, "Estados del supervisor de enclavamiento", size=44, color=WHITE, bold=True)
text(s, 0.8, 3.9, 11.7, 1.0, "MARCHA y MANTENIMIENTO: variables, condiciones y asignaciones", size=24, color=RGBColor(0xF6, 0xC4, 0x53))
text(s, 0.8, 5.6, 11.7, 0.8, "AFEV · Enclavamiento de seguridad para minería (faja, zona y dos operarios)", size=16, color=RGBColor(0xCC, 0xD4, 0xE0))
notes(s, "Presentamos el análisis de dos estados del controlador software/controlador.py, la función pura step().")

# 2 Sistema
s = base("El sistema: un supervisor como máquina de estados", 2)
text(s, 0.5, 1.3, 6.4, 5.5, [
    ("Qué protege", {"bold": True, "color": NAVY, "size": 22}),
    "Una faja transportadora y una zona de mantenimiento con 2 operarios (ids 1 y 2).",
    ("Cómo decide", {"bold": True, "color": NAVY, "size": 22}),
    "step(estado, snapshot, órdenes) → (estado', salidas, motivo). Función pura: sin efectos, determinista.",
    "Avanza como máximo UNA fase por tick y la condición insegura siempre tiene prioridad.",
    ("11 fases", {"bold": True, "color": NAVY, "size": 22}),
    "INICIO_SEGURO, LISTO, MARCHA, PARADA_SOLICITADA, AISLAMIENTO, BLOQUEO, VERIFICACION_CERO, MANTENIMIENTO, LIBERACION, RESTABLECIMIENTO, FALLO.",
], size=17)
table(s, 7.2, 1.5, 5.6, [
    ["Entrada", "Tipo (estado.py)"],
    ["Estado", "fase, ocupantes, bloqueos, reset_pendiente, intervencion_activa…"],
    ["Snapshot", "lecturas de sensores de la planta (láser, contacto, seccionador, velocidad…)"],
    ["Orden", "start, stop, solicitar_mantenimiento, cerrar_acceso…"],
    ["→ Salidas", "orden_contactor, permiso_acceso, orden_puerta, alarma…"],
], [1.5, 4.1], size=14, rowh=0.8)
notes(s, "El diseño separa observación (Snapshot), memoria (Estado) y actuación (Salidas).")

# 3 Variables
s = base("Variables del sistema", 3)
table(s, 0.5, 1.3, 12.3, [
    ["Variable", "Tipo", "Rol", "Por qué existe"],
    ["fase", "Fase (enum, 11)", "Estado discreto principal", "Impone el orden obligatorio de la secuencia"],
    ["ocupantes", "conjunto ⊆ {1,2}", "Quién está dentro (RFID)", "No cerrar el acceso ni energizar con gente dentro"],
    ["bloqueos", "conjunto ⊆ {1,2}", "Candados confirmados", "LOTO: cada operario controla su propio candado"],
    ["reset_pendiente", "bool", "Reset nuevo y vigente", "Evita arranques con órdenes antiguas"],
    ["intervencion_activa", "bool", "Hay mantenimiento en curso", "Registra que se pidió mantenimiento (aún no se consulta ni se limpia)"],
    ["comandos_vistos / eventos_vistos", "conjuntos de ids", "Memoria de idempotencia", "Una orden o evento RFID actúa una sola vez"],
    ["contacto_cerrado, seccionador_abierto, velocidad_m_s, laser_ocupado…", "Snapshot (Optional)", "Observación física", "La fase solo avanza si la planta lo CONFIRMA"],
], [3.4, 2.2, 3.0, 3.7], size=13, rowh=0.7)
notes(s, "Los Optional permiten representar 'dato desconocido'; un None nunca cuenta como seguro.")

# 4 Diagrama completo
s = base("Diagrama de estados completo", 4)
picture(s, "img/completo.png", 0.3, 1.1, 5.8, 6.3)
text(s, 6.4, 1.2, 6.5, 4.7, [
    ("Los dos estados elegidos", {"bold": True, "color": NAVY, "size": 22}),
    ("MARCHA (amarillo): ", {"bold": True, "color": GOLD, "size": 18}),
    "único estado con potencia aplicada: el de mayor riesgo.",
    ("MANTENIMIENTO (verde): ", {"bold": True, "color": GREEN, "size": 18}),
    "único estado con acceso humano permitido: el de mayor exposición.",
    ("Son los dos polos opuestos del sistema: ", {"bold": True, "color": NAVY, "size": 18}),
    "nunca pueden coincidir. Entre ambos hay 4 fases de aislamiento (PARADA → AISLAMIENTO → BLOQUEO → VERIFICACION_CERO) que garantizan energía cero.",
    ("FALLO ", {"bold": True, "color": RGBColor(0xA0, 0x20, 0x20), "size": 18}),
    "es transversal: cualquier fase puede caer en él (línea punteada).",
], size=16)
legend(s, 6.4, 6.0, 6.5, LEG[:1], 12)
legend(s, 6.4, 6.45, 6.5, LEG[1:2], 12)
legend(s, 6.4, 6.9, 6.5, LEG[2:], 12)
notes(s, "Diagrama generado con Graphviz (presentacion/completo.dot). Transiciones tomadas de controlador.py.")

# 5 Razón
s = base("¿Por qué estos dos estados?", 5)
for k, (ttl, col, lines) in enumerate([
    ("MARCHA", GOLD, ["Aquí se concentra el riesgo mecánico y eléctrico.", "Es el estado que debe poder abortarse en cualquier tick.", "Cobertura máxima de condiciones de fallo: emergencia, watchdog, dato inválido, presencia.", "Su salida de control es una sola: orden_contactor."]),
    ("MANTENIMIENTO", GREEN, ["Aquí se concentra el riesgo humano.", "Solo se alcanza tras cumplir 4 precondiciones físicas acumuladas.", "Es el único donde ocupantes importa para decidir.", "Su salida: permiso_acceso y puerta abierta."]),
]):
    x = 0.6 + k * 6.2
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.4), Inches(5.9), Inches(5.3))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.color.rgb = col; box.line.width = Pt(3)
    text(s, x + 0.3, 1.6, 5.3, 0.7, ttl, size=28, color=col, bold=True)
    text(s, x + 0.3, 2.5, 5.3, 4.0, ["• " + l for l in lines], size=18)
notes(s, "Son ilustrativos porque exhiben las tres clases de condición: de entrada, de permanencia y de salida/fallo.")

# 6 MARCHA diagrama
s = base("Estado MARCHA — diagrama", 6, GOLD)
picture(s, "img/marcha.png", 0.4, 1.1, 12.5, 5.3)
legend(s, 0.5, 6.55, 12.3, LEG, 12)
notes(s, "Notación: evento [condición] / asignaciones. Línea punteada roja = transición con prioridad por fallo.")

# 7 MARCHA tabla
s = base("MARCHA — variables, condiciones, asignaciones", 7, GOLD)
table(s, 0.4, 1.2, 12.5, [
    ["Transición", "Condición (guarda)", "Asignaciones", "Razón"],
    ["LISTO → MARCHA", "start nuevo ∧ reset_pendiente ∧ seguro_para_listo", "fase := MARCHA; reset_pendiente := False; orden_contactor := True; alarma := False", "Arranque solo con reset fresco y planta verificada segura"],
    ["MARCHA → MARCHA", "sin órdenes nuevas", "orden_contactor := True", "El contactor se re-afirma cada tick (no es memoria)"],
    ["MARCHA → PARADA_SOLICITADA", "solicitar_mantenimiento", "fase := PARADA_SOLICITADA; intervencion_activa := True; Salidas seguras", "Inicia la secuencia de aislamiento"],
    ["MARCHA → PARADA_SOLICITADA", "stop", "fase := PARADA_SOLICITADA; reset_pendiente := False", "Parada con máxima prioridad tras fallo; invalida reset"],
    ["MARCHA → FALLO", "emergencia ∨ watchdog ∨ dato inválido ∨ ((ocupantes ∨ láser) ∧ contacto_cerrado)", "fase := FALLO; reset_pendiente := False; Salidas seguras", "Fail-safe: la salida por defecto desenergiza"],
], [2.3, 3.5, 3.9, 2.8], size=12, head=GOLD, rowh=0.8)
text(s, 0.4, 6.3, 12.5, 0.8, "seguro_para_listo = sensor_valid ∧ ocupantes=∅ ∧ bloqueos=∅ ∧ láser libre ∧ barrera libre ∧ puerta cerrada ∧ contacto abierto ∧ seccionador cerrado ∧ |v| ≤ 0.001 m/s", size=13)
notes(s, "Salidas() por defecto: contactor False, permiso False, alarma True. Por eso 'seguras' = desenergizar y alarmar.")

# 8 MANT diagrama
s = base("Estado MANTENIMIENTO — diagrama", 8, GREEN)
picture(s, "img/mant.png", 0.4, 1.1, 12.5, 5.3)
legend(s, 0.5, 6.55, 12.3, LEG, 12)
notes(s, "Entrada solo desde VERIFICACION_CERO.")

# 9 MANT tabla
s = base("MANTENIMIENTO — variables, condiciones, asignaciones", 9, GREEN)
table(s, 0.4, 1.2, 12.5, [
    ["Transición", "Condición (guarda)", "Asignaciones", "Razón"],
    ["VERIFICACION_CERO → MANTENIMIENTO", "contacto_cerrado = False ∧ seccionador_abierto = True ∧ |velocidad| ≤ 0.001", "fase := MANTENIMIENTO; permiso_acceso := True; orden_puerta := ABRIR; alarma := False", "Energía cero confirmada por sensores, no supuesta"],
    ["MANTENIMIENTO → MANTENIMIENTO", "sin cerrar_acceso", "permiso_acceso := True; orden_puerta := ABRIR", "Mantiene el permiso mientras dure la intervención"],
    ["MANTENIMIENTO → MANTENIMIENTO", "cerrar_acceso ∧ ocupantes ≠ ∅", "permiso_acceso := True; motivo := OPERARIO_DENTRO", "Nunca encerrar a alguien: rechaza el cierre"],
    ["MANTENIMIENTO → LIBERACION", "cerrar_acceso ∧ ocupantes = ∅", "fase := LIBERACION; permiso_acceso := False; alarma := False", "Cierre solo con la zona vacía (RFID)"],
    ["MANTENIMIENTO → FALLO", "emergencia ∨ watchdog ∨ dato inválido ∨ ((ocupantes ∨ láser) ∧ contacto_cerrado)", "fase := FALLO; Salidas seguras", "Si algo energiza con gente dentro, se corta todo"],
], [2.5, 3.6, 3.6, 2.8], size=12, head=GREEN, rowh=0.85)
notes(s, "ocupantes lo actualiza Estado.con_snapshot() con eventos RFID únicos (event_id) de ingreso/salida.")

# 10 Fallo / prioridad
s = base("Cómo se evalúan las condiciones: prioridad", 10)
for i, (n, t1, t2) in enumerate([
    ("1", "Incorporar snapshot", "Estado.con_snapshot(): ocupantes por RFID, bloqueos confirmados"),
    ("2", "Filtrar órdenes duplicadas", "command_id nuevo → entra; repetido → se ignora"),
    ("3", "Condición de fallo", "_motivo_fallo() → FALLO inmediato, sin importar la fase"),
    ("4", "Orden stop", "→ PARADA_SOLICITADA con salidas seguras"),
    ("5", "Lógica propia de la fase", "guardas de MARCHA, MANTENIMIENTO, etc."),
]):
    y = 1.35 + i * 1.1
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), Inches(y), Inches(0.8), Inches(0.8)); c.fill.solid(); c.fill.fore_color.rgb = NAVY; c.line.fill.background()
    c.text_frame.text = n; r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT; c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    text(s, 1.8, y - 0.05, 10.5, 0.5, t1, size=22, color=NAVY, bold=True)
    text(s, 1.8, y + 0.4, 10.5, 0.5, t2, size=17)
notes(s, "Esto explica por qué FALLO aparece como transición desde MARCHA y MANTENIMIENTO aunque no esté en sus ramas del código.")


# 11 Formalización de fallos
s = base("Prioridad de fallo en Event-B (y VDM++)", 11)
text(s, 0.4, 1.15, 6.6, 0.5, "Event-B: ciclo LEER → DECIDIR (M2 corregido)", size=20, color=NAVY, bold=True)
code1 = ("LeerSensores   WHEN ciclo = LEER\n  THEN sensores :∈ …  || ciclo ≔ DECIDIR\n\n"
         "DetectarFallo  WHEN ciclo = DECIDIR ∧ Insegura\n  THEN fase ≔ FALLO || orden_contactor ≔ FALSE\n    || permiso_acceso ≔ FALSE || ciclo ≔ LEER\n\n"
         "Evento normal  WHEN ciclo = DECIDIR ∧ ¬Insegura ∧ …\n  THEN … || ciclo ≔ LEER\n\n"
         "INV_PRIORIDAD:\n  ciclo = LEER ⇒ (Insegura ⇒ fase = FALLO)")
text(s, 0.4, 1.65, 6.6, 3.6, code1.split("\n"), size=13, color=NAVY)
text(s, 0.4, 5.25, 6.6, 1.8, ["• Event-B no tiene orden de ejecución: la prioridad es exclusión mutua por guardas.", "• Insegura y ¬Insegura nunca se habilitan a la vez.", "• Un evento que olvide ¬Insegura genera una obligación de prueba no demostrable."], size=14)
text(s, 7.3, 1.15, 5.6, 0.5, "VDM++ (borrador sin verificar)", size=20, color=GREEN, bold=True)
code2 = ("DetectarFallo() ==\n  ( fase := <FALLO>;\n    ordenContactor := false;\n    permisoAcceso := false )\n"
         "pre  fallo or (contactoReal and ocupantes <> {})\npost fase = <FALLO>;\n\n"
         "Arrancar() == …\npre  fase = <LISTO> and not Insegura\n\n"
         "inv fase = <FALLO> =>\n  (not ordenContactor and not permisoAcceso)")
text(s, 7.3, 1.65, 5.6, 3.6, code2.split("\n"), size=13, color=NAVY)
text(s, 7.3, 5.25, 5.6, 1.8, ["• pre = obligación del llamador, no una guarda que habilite.", "• Cada operación debe repetir ¬Insegura en su pre.", "• El proyecto no contiene VDM++ de fallos."], size=14)
notes(s, "Correccion: un invariante Insegura => fase=FALLO sin ciclo no es demostrable porque LeerSensores cambia el entorno. Por eso se modela el ciclo LEER/DECIDIR, igual que step() en el codigo. Ver modelo/export/M2.txt. El modelo sigue siendo borrador sin POs de Rodin.")

# 12 Conclusiones
s = base("Conclusiones", 12)
text(s, 0.6, 1.4, 12.1, 5.5, [
    "• Las variables se dividen en memoria (Estado), observación (Snapshot) y actuación (Salidas); cada estado solo cambia por confirmación física.",
    "• Las condiciones son guardas conjuntivas conservadoras: un dato desconocido (None) nunca habilita una acción peligrosa.",
    "• Las asignaciones tienen un valor por defecto seguro (Salidas(): contactor off, alarma on); lo peligroso debe re-afirmarse cada tick.",
    "• MARCHA y MANTENIMIENTO nunca coexisten: la cadena PARADA → AISLAMIENTO → BLOQUEO → VERIFICACION_CERO lo impone.",
    ("Alcance: el análisis corresponde al controlador implementado con el doble determinista; la integración con CoppeliaSim y las obligaciones de M1/M2 siguen pendientes.", {"size": 15, "color": GOLD}),
], size=20)
notes(s, "Fuente: software/controlador.py y software/estado.py.")

prs.save("Presentacion_estados.pptx")
