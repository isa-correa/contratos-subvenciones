"""Genera las hojas HTML de los esquemas nuevos (estilo de los PDF de ordenado).
Uso: python3 generar.py [id ...]   (sin ids: todos). Cada hoja se pinta con Chrome a PNG."""
import os, sys, subprocess, html
AQUI = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AVISO = '<div class="aviso"><svg viewBox="0 0 24 24"><path d="M12 2 1 21h22z" fill="#c98a00"/><path d="M12 9v6m0 2.5v.5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg><span>%s</span></div>'
FLECHA = '<defs><marker id="f" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9z" fill="#374151"/></marker></defs>'

def caja(x, y, w, h, txt, cls="", sub=""):
    s = '<div class="b %s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx"><div>%s' % (cls, x, y, w, h, txt)
    if sub: s += "<small>%s</small>" % sub
    return s + "</div></div>"
def lin(pts, flecha=True, dash=False):
    d = "M" + " L".join("%d,%d" % p for p in pts)
    return '<path d="%s" fill="none" stroke="#374151" stroke-width="2.6"%s%s/>' % (d, ' marker-end="url(#f)"' if flecha else "", ' stroke-dasharray="9 7"' if dash else "")
def lab(x, y, t):
    return '<div class="lab %s" style="left:%dpx;top:%dpx">%s</div>' % ("si" if t == "Sí" else "no", x, y, t)
def stage(piezas, lineas=""):
    return '<div class="stage"><svg class="lin">%s%s</svg>%s</div>' % (FLECHA, lineas, piezas)
def pagina(nombre, titulo, sub, cuerpo, aviso=None):
    h = ('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="base.css"><div class="hoja">'
         '<h1>%s</h1><p class="sub">%s</p>%s%s<div class="pie">1 / 1</div></div>') % (titulo, sub, cuerpo, AVISO % aviso if aviso else "")
    open(os.path.join(AQUI, nombre + ".html"), "w").write(h)

# ---------- plantillas ----------
def arbol(top, q1, fuera1, q2, izq, der, aviso=None, nombre=None, titulo="", sub="", et1=("No", "Sí")):
    """top -> q1 (No: fuera1; Sí: q2) -> q2 (izq/der = (texto, sub, clase, etiqueta))"""
    p = caja(263, 0, 500, 62, top, "gr") + caja(303, 100, 420, 82, q1, "q")
    p += caja(0, 250, 300, 100, fuera1[0], fuera1[2], fuera1[1])
    p += caja(530, 232, 480, 104, q2, "q")
    p += caja(430, 430, 300, 96, izq[0], izq[2], izq[1]) + caja(760, 430, 267, 96, der[0], der[2], der[1])
    l = lin([(513, 62), (513, 100)]) + lin([(303, 141), (150, 141), (150, 250)]) + lin([(723, 141), (770, 141), (770, 232)])
    l += lin([(770, 336), (770, 383), (580, 383), (580, 430)]) + lin([(770, 383), (893, 383), (893, 430)])
    p += lab(226, 141, et1[0]) + lab(747, 141, et1[1]) + lab(675, 383, izq[3]) + lab(832, 383, der[3])
    pagina(nombre, titulo, sub, stage(p, l), aviso)

def circulos(nombre, titulo, sub, aviso):
    h = open(os.path.join(AQUI, "circulos.html")).read()
    open(os.path.join(AQUI, nombre + ".html"), "w").write(h.replace("@@T@@", titulo).replace("@@S@@", sub).replace("@@A@@", aviso))

def dos_ramas(nombre, titulo, sub, top, izq, der, aviso=None):
    p = caja(333, 0, 360, 70, top, "q")
    xs = [(30, 440), (557, 440)]
    l = ""
    for (x, w), col in zip(xs, (izq, der)):
        y = 170
        for i, (txt, cls, s) in enumerate(col):
            p += caja(x, y, w, 150 if i == 0 else 140, txt, cls, s)
            y += 150 + 80 if i == 0 else 0
        l += lin([(513, 70), (513, 105), (x + w // 2, 105), (x + w // 2, 170)])
        l += lin([(x + w // 2, 320), (x + w // 2, 400)])
    pagina(nombre, titulo, sub, stage(p, l), aviso)

# ---------- hojas del lote 1 ----------
def lote1():
    # 1. estructura de la ley
    p = ""
    cols = [("Preámbulo", "", "gr", 0), ("Título Preliminar", "Arts. 1 a 27", "az", 1), ("Libro I", "Configuración general", "", 2),
            ("Libro II", "Contratos de las Administraciones Públicas", "", 3), ("Libro III", "Contratos de otros entes del sector público", "", 4),
            ("Libro IV", "Organización administrativa", "", 5)]
    w, g = 150, 25
    l = ""
    for t, s, c, i in cols:
        x = i * (w + g)
        p += caja(x, 40, w, 270, '<b class="t">%s</b>' % t, c, s)
        if i: l += lin([(x - g + 2, 175), (x - 2, 175)])
    l += lin([(20, 410), (1000, 410)])
    p += '<div style="position:absolute;left:0;right:0;top:430px;text-align:center;color:var(--gris);font-size:20px">De lo general (Título Preliminar) a lo específico de cada Libro</div>'
    pagina("h1", "Estructura de la LCSP", "Cómo está ordenada la <b>Ley de Contratos del Sector Público</b>", stage(p, l))

    # 2. ámbito de aplicación
    arbol("Negocio o contrato celebrado por alguien", "¿Lo celebra una entidad del sector público? <small style='color:#cfd6e4'>art. 3</small>",
          ('<b class="t">Fuera de la LCSP</b>', "Derecho privado", "gr"), "¿Es un contrato oneroso? <small style='color:#cfd6e4'>art. 2</small>",
          ('<b class="t">Fuera del ámbito objetivo</b>', "art. 2", "no", "No"), ('<b class="t">DENTRO de la LCSP</b>', "", "az", "Sí"),
          "<b>Excepción:</b> contrato subvencionado por un poder adjudicador y sujeto a regulación armonizada (art. 23)",
          "h2", "Ámbito de aplicación", "Art. 2 LCSP: dos preguntas para saber si un contrato entra en la ley")

    # 3. y 44. niveles del sector público
    circulos("h3", "Ámbito subjetivo del sector público", "Art. 3 LCSP: tres niveles, cada uno <b>dentro</b> del siguiente",
             "<b>Idea clave:</b> toda Administración Pública es poder adjudicador, y todo poder adjudicador es sector público. Al revés, no.")

    # 4. bienes inmuebles
    dos_ramas("h4", "Contratos sobre bienes inmuebles", "Art. 9 LCSP: ¿el inmueble ya existe o hay que construirlo?",
              "Bien inmueble <small style='color:#cfd6e4'>edificio, terreno...</small>",
              [("Ya existe: se compra, alquila o permuta", "", ""), ('<b class="t">EXCLUIDO</b>', "no", "Legislación patrimonial")],
              [("Hay que construirlo: se contrata la obra", "", ""), ('<b class="t">INCLUIDO</b>', "si", "Contrato de obras")])

    # 5. calificación (1)
    dos_ramas("h5", "Calificación de los contratos (1)", "Art. 12 LCSP: qué normas se aplican a cada contrato",
              "Contrato del sector público",
              [("Obras, concesión de obras, concesión de servicios, suministro o servicios", "", ""), ('<b class="t">Se califican</b>', "az", "Según los arts. 13 a 17 LCSP")],
              [("Resto de contratos del sector público", "", ""), ('<b class="t">Normas aplicables</b>', "gr", "De Derecho administrativo o privado (supletorio)")])

    # 6. calificación (2)
    p = ""; l = ""
    xs = [0, 355, 710]; w = 317
    cab = [("Bien inmueble", "OBRAS", "art. 13"), ("Bien mueble", "SUMINISTRO", "art. 16"), ("Hacer algo", "SERVICIOS", "art. 17")]
    subc = ["", "", "actividad o resultado"]
    for x, (a, b, c), s in zip(xs, cab, subc):
        p += caja(x, 0, w, 110, '<b class="t">%s</b>' % a, "q", s)
        p += caja(x, 180, w, 120, '<b class="t">%s</b>' % b, "az", c)
        l += lin([(x + w // 2, 110), (x + w // 2, 180)])
    p += caja(0, 400, w, 140, '<b class="t">CONCESIÓN DE OBRAS</b>', "si", "art. 14 · explotación y riesgo")
    p += caja(710, 400, w, 140, '<b class="t">CONCESIÓN DE SERVICIOS</b>', "si", "art. 15 · explotación; solo poder adjudicador")
    for x in (0, 710):
        l += lin([(x + w // 2, 300), (x + w // 2, 400)]); p += lab(x + w // 2 + 0, 350, "se explota").replace(' si"', ' gr"').replace("lab no", "lab si")
    p += caja(355, 400, w, 140, "Si además se <b>explota</b> el resultado y el contratista asume el <b>riesgo</b>, pasa a ser concesión", "gr")
    pagina("h6", "Calificación de los contratos (2)", "Art. 12 LCSP: los cinco contratos típicos y cuándo hay <b>concesión</b>", stage(p, l))

    # 7. SARA
    p = ""; l = ""
    req = [("1", "Contrato típico", "obras, concesión de obras, concesión de servicios, suministro o servicios"),
           ("2", "Adjudicado por un poder adjudicador", "nivel 1 o nivel 2"),
           ("3", "Valor estimado igual o superior al umbral aplicable", "")]
    for i, (n, t, s) in enumerate(req):
        x = i * 355
        p += caja(x, 10, 317, 230, '<span class="num">%s</span><b class="t">%s</b>' % (n, t), "", s)
        l += lin([(x + 158, 240), (x + 158, 290), (513, 290), (513, 330)]) if i != 1 else lin([(513, 240), (513, 330)])
    p += caja(298, 335, 430, 120, '<b class="t" style="font-size:24px">CONTRATO SARA</b>', "az", "sujeto a regulación armonizada")
    pagina("h7", "Contratos SARA", "Art. 19 LCSP: tienen que cumplirse los <b>tres requisitos</b>", stage(p, l),
           "<b>Si falta alguno de los tres:</b> contrato NO SARA. Igualmente debe respetar los principios de la contratación pública.")

    # 8. administrativos y privados
    arbol("Contrato celebrado por un ente del sector público", "¿Lo celebra una Administración Pública (nivel 1)?",
          ('<b class="t">PRIVADO</b>', "Niveles 2 y 3, sin excepción", "no"),
          "¿El objeto es financiero (salvo valores), arte y literatura, espectáculos públicos o suscripciones a revistas y bases de datos?",
          ('<b class="t">PRIVADO</b>', "Excepción dentro del nivel 1", "no", "Sí"), ('<b class="t">ADMINISTRATIVO</b>', "Típico, especial u otro que la ley determine", "az", "No"),
          None, "h8", "Contratos administrativos y privados", "Arts. 24 a 27 LCSP: qué naturaleza tiene el contrato")

    # 9. prórrogas
    p = ""; l = ""
    qs = ["¿La prórroga estaba prevista en el pliego (PCAP)?", "¿Se preavisó con al menos 2 meses de antelación (o el plazo del pliego)?",
          "¿Concurre causa de resolución del art. 198.6 (impago de la Administración de más de 6 meses)?"]
    ex = [("NO cabe prórroga", "No estaba prevista"), ("NO obligatoria", "Falta el preaviso"), ("NO obligatoria", "Hay causa de resolución")]
    for i in range(3):
        y = i * 135
        p += caja(360, y, 470, 84, qs[i], "q")
        p += caja(10, y, 270, 84, '<b class="t">%s</b>' % ex[i][0], "no", ex[i][1])
        l += lin([(360, y + 42), (282, y + 42)])
        p += lab(321, y + 42, "No" if i < 2 else "Sí")
        if i < 2:
            l += lin([(595, y + 84), (595, y + 135)]); p += lab(595, y + 110, "Sí")
    l += lin([(595, 354), (595, 405)]); p += lab(595, 380, "No")
    p += caja(360, 405, 470, 90, '<b class="t">OBLIGATORIA</b>', "si", "para el contratista")
    pagina("h9", "Las prórrogas: reglas generales", "Art. 29 LCSP: cuándo el contratista <b>está obligado</b> a aceptar la prórroga", stage(p, l),
           "<b>Solo es obligatoria</b> si estaba prevista, hubo preaviso y no hay causa de resolución.")

    # 10. plazos máximos
    filas = [("Contratos menores", 1, "1 año", "sin prórroga"), ("Suministro y servicios sucesivos", 5, "5 años", "incluidas las prórrogas"),
             ("Concesión de servicios sanitarios, sin obra", 10, "10 años", ""), ("Concesión de servicios genérica, sin obra", 25, "25 años", ""),
             ("Concesión de obras y de servicios con obra previa", 40, "40 años", "")]
    p = ""
    for i, (t, n, v, s) in enumerate(filas):
        y = i * 92
        p += '<div style="position:absolute;left:0;top:%dpx;width:330px;height:70px;display:flex;align-items:center;font-size:18px;font-weight:600">%s</div>' % (y, t)
        wb = max(int(n / 40 * 560), 22)
        p += '<div style="position:absolute;left:350px;top:%dpx;width:%dpx;height:70px;border-radius:14px;background:var(--azul);opacity:%s"></div>' % (y, wb, 0.45 + 0.1375 * i)
        p += '<div style="position:absolute;left:%dpx;top:%dpx;height:70px;display:flex;align-items:center;gap:10px;font-size:24px;font-weight:700;color:var(--azul)">%s<span style="font-size:15px;font-weight:500;color:var(--gris)">%s</span></div>' % (350 + wb + 14, y, v, s)
    pagina("h10", "Plazos máximos de duración por tipo de contrato", "Art. 29 LCSP: de menos a más años", stage(p, ""),
           "<b>Los 5 años</b> de suministros y servicios sucesivos incluyen las prórrogas.")

    # 11. ejecución por la propia Administración
    p = caja(0, 0, 500, 70, '<b class="t" style="font-size:20px">OBRAS Y SUMINISTRO (fabricación)</b>', "az")
    p += caja(0, 70, 500, 400, "", "")
    p += '<div style="position:absolute;left:20px;top:92px;width:460px"><b style="font-size:20px;color:var(--azul)">La Administración PUEDE</b> usar medios propios, <b>solo en supuestos tasados</b>:<ul style="margin:12px 0 0 22px;font-size:19px;line-height:1.55"><li>Talleres propios.</li><li>Ahorro: más del 5 % en obras o más del 20 % en muebles.</li><li>Licitación desierta.</li><li>Emergencia.</li><li>Precio no fijable de antemano.</li><li>Sustitución del contratista en unidades de obra modificadas.</li></ul></div>'
    p += caja(527, 0, 500, 70, '<b class="t" style="font-size:20px">SERVICIOS</b>', "no")
    p += caja(527, 70, 500, 400, "", "no")
    p += '<div style="position:absolute;left:547px;top:92px;width:460px;font-size:20px"><b style="font-size:20px;color:var(--rojo)">La Administración DEBE</b> prestar el servicio con medios propios si los tiene cualificados.<p style="margin-top:18px">Solo puede contratar fuera cuando <b>carezca de medios suficientes</b>, y lo justifica con el <b>informe de insuficiencia de medios</b>.</p></div>'
    pagina("h11", "Ejecución por la propia Administración", "Art. 30 LCSP: depende del tipo de contrato", stage(p, ""))

    # 12. medio propio personificado
    req = [("1", "Control análogo", "El poder adjudicador puede conferirle encargos de ejecución obligatoria, igual que sobre sus propios servicios"),
           ("2", "Más del 80 %", "De la actividad del ente se realiza para los poderes adjudicadores que lo controlan"),
           ("3", "Capital 100 % público", "Si es una entidad de derecho privado, todo su capital debe ser de titularidad pública"),
           ("4", "Constar en estatutos", "Su condición de medio propio personificado debe figurar expresamente en sus estatutos")]
    p = ""; l = ""; w = 233
    for i, (n, t, s) in enumerate(req):
        x = i * (w + 31.7)
        p += caja(int(x), 20, w, 330, '<span class="num">%s</span><b class="t" style="font-size:19px">%s</b>' % (n, t), "", s)
        l += lin([(int(x) + w // 2, 350), (int(x) + w // 2, 390), (513, 390), (513, 420)]) if i in (0, 3) else lin([(int(x) + w // 2, 350), (int(x) + w // 2, 390)], False)
    l += lin([(int(1 * (w + 31.7)) + w // 2, 310), (int(1 * (w + 31.7)) + w // 2, 385)]) if False else ""
    p += caja(263, 425, 500, 100, '<b class="t" style="font-size:22px">MEDIO PROPIO PERSONIFICADO</b>', "az")
    pagina("h12", "Requisitos del medio propio personificado", "Art. 32 LCSP: tienen que cumplirse <b>los cuatro</b>", stage(p, l))


def ramas(nombre, titulo, sub, q, cols, aviso=None, alto=270):
    """q = pregunta (o None). cols = [(etiqueta o None, cabecera, cuerpo, clase)]"""
    n = len(cols); g = 30; w = (1027 - g * (n - 1)) // n
    y0 = 200 if q else 20
    p = ""; l = ""
    if q:
        p += caja(213, 0, 600, 110, '<span style="font-size:24px">%s</span>' % q, "q")
    for i, (et, cab, cuerpo, cls) in enumerate(cols):
        x = i * (w + g)
        txt = '<b class="t" style="font-size:25px">%s</b>' % cab
        if cuerpo: txt += '<div style="font-weight:400;font-size:23px;margin-top:14px;line-height:1.4">%s</div>' % cuerpo
        p += caja(x, y0, w, alto, txt, cls)
        if q:
            cx = x + w // 2
            l += lin([(513, 110), (513, 150), (cx, 150), (cx, y0)]) if cx != 513 else lin([(513, 110), (513, y0)])
            if et: p += lab(cx, 150 if cx != 513 else 160, et)
    pagina(nombre, titulo, sub, stage(p, l), aviso)

def tres_req(nombre, titulo, sub, reqs, destino, dsub, aviso):
    p = ""; l = ""
    for i, (n, t, s) in enumerate(reqs):
        x = i * 355
        p += caja(x, 10, 317, 230, '<span class="num">%s</span><b class="t">%s</b>' % (n, t), "", s)
        l += lin([(x + 158, 240), (x + 158, 290), (513, 290), (513, 330)]) if i != 1 else lin([(513, 240), (513, 330)])
    p += caja(248, 335, 530, 120, '<b class="t" style="font-size:26px">%s</b>' % destino, "az", dsub)
    pagina(nombre, titulo, sub, stage(p, l), aviso)

def lote2():
    ramas("h13", "Perfección del contrato", "Art. 36 LCSP: ¿cuándo nace el contrato?", None, [
        (None, "REGLA GENERAL", "El contrato se perfecciona con su <b>FORMALIZACIÓN</b><br>(la firma del documento por ambas partes)", "az"),
        (None, "EXCEPCIONES", "Se perfeccionan con la <b>ADJUDICACIÓN</b>:<ul style='text-align:left;margin:14px 0 0 24px;font-size:22px;line-height:1.5'><li>Contratos basados en un acuerdo marco.</li><li>Contratos específicos de un sistema dinámico de adquisición.</li><li>Contratos menores (no se formalizan; no lo dice expresamente la ley).</li></ul>", "")], alto=470)
    ramas("h14", "Carácter formal del contrato", "Art. 37 LCSP: cómo se formaliza según quién lo celebra", "¿Quién celebra el contrato?", [
        (None, "Administración Pública", "Se formaliza en un <b>documento administrativo</b> (art. 153)", "az"),
        (None, "PANAP (nivel 2)", "Se formaliza, pero <b>NO</b> en documento administrativo (no es Administración)", ""),
        (None, "Contrato menor", "<b>NO</b> se formaliza (expediente simplificado, remisión al art. 118)", "gr")],
        "<b>Si cabe recurso especial:</b> espera de 15 días hábiles entre la adjudicación y la formalización.", alto=320)
    ramas("h15", "Revisión de oficio", "Art. 41 LCSP: quién es competente para declarar la nulidad", "¿Quién adjudicó el contrato viciado?", [
        (None, "Administración Pública", "Competente: el <b>ÓRGANO DE CONTRATACIÓN</b>", "az"),
        (None, "PANAP o nivel 3", "Competente: el <b>TITULAR del departamento de tutela</b>", "")],
        "<b>Ejemplo:</b> RENFE → el ministerio con competencia en transporte.", alto=300)
    ramas("h16", "Efectos de la nulidad", "Art. 42 LCSP: depende de la fase en la que se produjo la causa", "¿En qué fase se produjo la causa de nulidad?", [
        (None, "Actos preparatorios o adjudicación", "Nulidad de <b>TODO</b> el contrato.<br>Pasa a fase de liquidación: restitución recíproca (o su valor) + indemnización a cargo del culpable", "no"),
        (None, "Efectos, modificación o extinción", "Solo afecta a esos actos concretos y a sus consecuencias.<br>Ej.: solo a las 20 sillas de más, no a las 100 ya suministradas", "az")], alto=330)
    tres_req("h17", "Recurso especial en materia de contratación", "Art. 44 LCSP: tienen que cumplirse los <b>tres requisitos</b>", [
        ("1", "El contrato lo adjudica un poder adjudicador", "nivel 1 o nivel 2"),
        ("2", "Se impugna un acto recurrible", "art. 44.2"),
        ("3", "El contrato supera el umbral de cuantía", "el aplicable a su tipo")], "RECURSO ESPECIAL", "",
        "<b>Si falta alguno de los tres:</b> recursos ordinarios (alzada o reposición potestativo) y, después, contencioso-administrativo.")
    ramas("h18", "Suspensión automática al recurrir", "Arts. 49 a 53 LCSP: depende del acto que se recurre", "¿Qué acto se recurre?", [
        (None, "El acuerdo de ADJUDICACIÓN", "<b>SUSPENSIÓN AUTOMÁTICA</b><br>(salvo acuerdo marco o SDA)", "si"),
        (None, "Otro acto (pliegos, anuncio...)", "<b>NO</b> hay suspensión automática<br>(cabe pedirla como cautelar)", "no")], alto=300)
    # 19
    p = ""; l = ""
    cajas = [("Acto recurrible", "art. 44.2", ""), ("Recurso especial", "TACRC u órgano autonómico", "az"), ("Contencioso-administrativo", "Audiencia Nacional o TSJ", "")]
    for i, (t, s, c) in enumerate(cajas):
        p += caja(i * 368, 230, 290, 190, '<b class="t">%s</b>' % t, c, s)
    l += lin([(292, 325), (366, 325)]) + lin([(660, 325), (734, 325)])
    l += lin([(145, 230), (145, 110), (882, 110), (882, 230)], True, True)
    p += '<div class="b bl" style="left:230px;top:62px;width:570px;height:96px;border-style:dashed;border-color:var(--gris);font-size:22px"><div><b>Vía potestativa:</b> se puede saltar el recurso especial e ir directo al contencioso</div></div>'
    pagina("h19", "Recurso contencioso posterior", "Arts. 44 y 59 LCSP: qué vías hay contra un acto recurrible", stage(p, l))
    ramas("h21", "Prohibiciones de contratar", "Art. 72 LCSP: quién aprecia el alcance y la duración", "¿La sentencia o resolución fija expresamente alcance y duración?", [
        ("Sí", "Lo aprecia el órgano de contratación", "Directamente el <b>ÓRGANO DE CONTRATACIÓN</b>", "si"),
        ("No", "Procedimiento del Ministro de Hacienda", "A propuesta de la <b>JCCPE</b>", "az")], alto=300)
    # 22 vigencia de clasificaciones
    p = caja(0, 0, 480, 140, '<b class="t">Cada año</b>', "", "Justificar la solvencia económica y financiera")
    p += caja(547, 0, 480, 140, '<b class="t">Cada 3 años</b>', "", "Justificar la solvencia técnica o profesional")
    p += caja(213, 220, 600, 120, "¿Se aporta declaración responsable o documentación actualizada a tiempo?", "q")
    p += caja(213, 430, 600, 130, '<b class="t">Si NO se aporta</b>', "no", "Suspensión automática de la clasificación + expediente de revisión")
    l = lin([(240, 140), (240, 180), (513, 180), (513, 220)]) + lin([(787, 140), (787, 180), (513, 180)], False) + lin([(513, 340), (513, 430)])
    p += lab(513, 385, "No")
    pagina("h22", "Vigencia de las clasificaciones", "Art. 82 LCSP: hay que mantenerlas al día", stage(p, l))
    # 23 solvencia técnica en servicios
    filas = [("Relación de obras, suministros o servicios previos + aval", "5 años", "3 años", "3 años"),
             ("Personal técnico disponible", "s", "s", "s"), ("Instalaciones, medidas de calidad e I+D", "x", "s", "s"),
             ("Títulos académicos y profesionales", "s", "n", "s"), ("Medidas de gestión medioambiental", "s", "n", "s"),
             ("Plantilla media anual y directivos (3 años)", "s", "n", "s"), ("Maquinaria, material y equipo técnico", "s", "n", "s"),
             ("Control de capacidad de producción o técnica", "x", "s (producción)", "s (técnica)"),
             ("Muestras, descripciones y fotografías", "n", "s", "n"), ("Parte del contrato a subcontratar", "n", "n", "s")]
    def cel(v):
        if v == "s": return '<td><span class="s">✓</span></td>'
        if v == "n": return '<td><span class="n">✗</span></td>'
        if v == "x": return '<td><span class="x">n/a</span></td>'
        if v.startswith("s "): return '<td><span class="s">✓</span> <span class="x" style="font-size:15px">%s</span></td>' % v[2:]
        return '<td><b>%s</b></td>' % v
    t = '<table class="t"><tr><th>Medio de solvencia técnica</th><th>Obras</th><th>Suministro</th><th>Servicios</th></tr>'
    for f in filas: t += "<tr><td>%s</td>%s%s%s</tr>" % (f[0], cel(f[1]), cel(f[2]), cel(f[3]))
    t += "</table>"
    pagina("h23", "Solvencia técnica según el contrato", "Art. 90 LCSP: qué medios se admiten en obras, suministro y servicios",
           '<div class="stage">%s</div>' % t, "<b>✓</b> se admite · <b>✗</b> no se admite · <b>n/a</b> no aplica")
    # 24 garantías
    p = ""; l = ""
    barras = [(0, 330, "FASE DE PREPARACIÓN", "gr"), (345, 410, "FASE DE ADJUDICACIÓN", ""), (770, 257, "EJECUCIÓN DEL CONTRATO", "az")]
    for x, w, t, c in barras: p += caja(x, 0, w, 80, '<b class="t">%s</b>' % t, c)
    l += lin([(0, 330), (1015, 330)])
    pts = [(100, "Informe de necesidad"), (370, "Anuncio de licitación"), (700, "Selección de la mejor oferta"), (930, "Formalización o perfección")]
    for x, t in pts:
        l += lin([(x, 314), (x, 346)], False)
        p += '<div style="position:absolute;left:%dpx;top:362px;width:200px;transform:translateX(-50%%);text-align:center;font-size:21px">%s</div>' % (x, t)
    p += caja(250, 170, 240, 80, '<b class="t">Garantía provisional</b>', "")
    l += lin([(370, 250), (370, 322)])
    p += caja(580, 170, 240, 80, '<b class="t">Garantía definitiva</b>', "si")
    l += lin([(700, 250), (700, 322)])
    pagina("h24", "Garantías", "Arts. 106 a 111 LCSP: cuándo se exige cada una", stage(p, l))

import re as _re
def negrita(t):
    t = _re.sub(r"(\b\d+(?:[.,]\d+)?\s*(?:días hábiles|días|hábiles|meses|mes|años|sobres?|candidatos|días HÁBILES)\b)", r"<b>\1</b>", t)
    return _re.sub(r"\b(NO|SIN|NUNCA|MÍNIMO|SÍ|SOLO|HÁBILES|COMÚN)\b", r"<b>\1</b>", t)

def serpiente(nombre, titulo, sub, pasos, aviso=None):
    """pasos = [(titulo, texto, clase)]; 3 por fila, en serpentina."""
    n = len(pasos); filas = (n + 2) // 3; w = 317; g = 38
    h = 215 if filas == 2 else 168; gv = 70 if filas == 2 else 44
    pos = []
    for i in range(n):
        r, c = divmod(i, 3)
        if r % 2: c = 2 - c
        pos.append((c * (w + g), r * (h + gv), r))
    p = ""; l = ""
    for i, ((t, txt, cls), (x, y, r)) in enumerate(zip(pasos, pos)):
        cab = ('<div style="display:flex;align-items:center;justify-content:center;gap:10px;width:100%%">'
               '<span class="num" style="margin:0;flex:none">%d</span><b class="t" style="font-size:%dpx;text-align:left;line-height:1.15">%s</b></div>') % (i + 1, 22 if filas == 2 else 20, t)
        cuerpo = '<div style="margin-top:9px;font-size:%dpx;line-height:1.3;width:100%%">%s</div>' % (20 if filas == 2 else 18, negrita(txt))
        p += caja(x, y, w, h, cab + cuerpo, cls)
        if i < n - 1:
            nx, ny, nr = pos[i + 1]
            if nr == r:
                if r % 2 == 0: l += lin([(x + w + 2, y + h // 2), (nx - 2, y + h // 2)])
                else: l += lin([(x - 2, y + h // 2), (nx + w + 2, y + h // 2)])
            else:
                l += lin([(x + w // 2, y + h + 2), (x + w // 2, ny - 2)])
    pagina(nombre, titulo, sub, stage(p, l), aviso)

def lote3():
    arbol("Tramitación del expediente", "¿Catástrofe, grave peligro o necesidad de defensa nacional?",
          ('<b class="t">EMERGENCIA</b>', "Tramitación de emergencia (art. 120)", "no"),
          "¿Hay necesidad inaplazable, o hay que acelerar la adjudicación por interés público?",
          ('<b class="t">URGENTE</b>', "Tramitación urgente (art. 119)", "az", "Sí"), ('<b class="t">ORDINARIA</b>', "Tramitación ordinaria", "", "No"),
          None, "h25", "Tramitación ordinaria, urgente o de emergencia", "Arts. 119 y 120 LCSP: qué tramitación corresponde", et1=("Sí", "No"))
    # 26 pliegos y gasto
    p = ""; l = lin([(0, 190), (1015, 190)])
    pts = [(160, "Aprobación de los pliegos particulares", ""), (420, "Autorización del gasto", "aprobación del expediente"), (680, "Licitación", "ofertas"), (910, "Adjudicación", "")]
    for i, (x, t, sb) in enumerate(pts):
        p += '<div style="position:absolute;left:%dpx;top:%dpx;width:210px;height:40px;margin:-0px 0 0 -105px;border-radius:50%%;"></div>' % (x, 0)
        l += '<circle cx="%d" cy="190" r="13" fill="%s" stroke="#fff" stroke-width="3"/>' % (x, "#1466d9")
        p += '<div style="position:absolute;left:%dpx;top:50px;width:230px;transform:translateX(-50%%);text-align:center;font-size:21px;font-weight:700">%s%s</div>' % (x, t, '<div style="font-weight:400;font-size:18px;color:var(--gris)">%s</div>' % sb if sb else "")
    p += caja(10, 330, 300, 120, "Antes o <b>a la vez</b> que el gasto", "")
    l += lin([(160, 330), (160, 210)])
    p += caja(340, 330, 450, 150, "<b>Límite absoluto:</b> antes de licitar. Si no hay licitación, antes de adjudicar", "no")
    l += lin([(420, 330), (420, 210)])
    pagina("h26", "Pliegos y autorización del gasto", "Arts. 116, 117 y 122 LCSP: qué va antes y qué va después", stage(p, l))
    serpiente("h27", "Adjudicación: normas generales", "Arts. 131 a 155 LCSP: de la licitación a la formalización", [
        ("Anuncio de licitación", "Perfil de contratante (+ BOE, + DOUE), salvo negociado sin publicidad", ""),
        ("Presentación", "Oferta (o solicitud de participación) + declaración responsable (DEUC)", ""),
        ("Mesa de contratación", "Califica el DEUC (3 días para subsanar) y valora ofertas (+ subasta, si se prevé)", ""),
        ("Requerimiento al mejor", "10 días hábiles: documentos justificativos + garantía definitiva", ""),
        ("Adjudicación", "Al licitador de la mejor oferta", ""),
        ("Formalización", "Y comienzo de la ejecución", "si")])
    # 28 criterios
    p = caja(313, 0, 400, 80, '<b class="t" style="font-size:23px">CRITERIOS DE ADJUDICACIÓN</b>', "q")
    p += caja(0, 150, 470, 100, '<b class="t">ECONÓMICOS</b>', "az", "relacionados con los costes")
    p += caja(557, 150, 470, 100, '<b class="t">CUALITATIVOS</b>', "az", "relacionados con la calidad")
    p += caja(0, 320, 470, 190, '<b class="t">Siempre OBJETIVOS</b><div style="font-weight:400;font-size:21px;margin-top:10px">Fórmula. Precio (lo habitual) o planteamiento de rentabilidad: coste del ciclo de vida</div>', "")
    p += caja(557, 320, 225, 190, '<b class="t">OBJETIVOS</b><div style="font-weight:400;font-size:20px;margin-top:10px">Fórmula: plazos, garantía, posventa...</div>', "")
    p += caja(802, 320, 225, 190, '<b class="t">SUBJETIVOS</b><div style="font-weight:400;font-size:20px;margin-top:10px">Juicio de valor: estética...</div>', "gr")
    l = lin([(513, 80), (513, 115), (235, 115), (235, 150)]) + lin([(513, 115), (792, 115), (792, 150)])
    l += lin([(235, 250), (235, 320)]) + lin([(792, 250), (792, 285), (670, 285), (670, 320)]) + lin([(792, 285), (914, 285), (914, 320)])
    pagina("h28", "Criterios de adjudicación", "Arts. 145 y 146 LCSP: la clasificación", stage(p, l))
    ramas("h29", "Plazo para formalizar", "Art. 153 LCSP: depende de si cabe recurso especial", "Notificación de la adjudicación: ¿contrato susceptible de recurso especial?", [
        ("Sí", "Espera de 15 días hábiles", "Las CCAA pueden ampliarlo, sin exceder de un mes.<br>Después, requerimiento al adjudicatario: formaliza en un máximo de 5 días (naturales)", "az"),
        ("No", "Formalizar sin espera", "No más tarde de 15 días hábiles desde la notificación", "")],
        "<b>FORMALIZACIÓN = perfección del contrato</b>", alto=290)
    serpiente("h30", "Procedimiento abierto, paso a paso", "Art. 156 LCSP", [
        ("Anuncio de licitación", "Perfil + BOE (AGE) + DOUE (SARA)", ""),
        ("Presentación de ofertas", "SARA: 35 días (obras, suministros, servicios) o 30 (concesiones), desde el envío al DOUE. No SARA: 15 (suministros, servicios) o 26 (obras, concesiones)", ""),
        ("Sobre 1: requisitos previos", "Declaración responsable (DEUC) + garantía provisional, si se exige. Subsanación: 3 días", ""),
        ("Apertura de las ofertas", "Máximo 20 días desde el fin de plazo. Acto público (salvo electrónica). Primero juicio de valor, luego fórmulas", ""),
        ("Propuesta y «adjudicación»", "Desde la apertura: 15 días (solo precio) o 2 meses (varios criterios o ciclo de vida); +15 hábiles si hay anormales", ""),
        ("Requerimiento al mejor", "10 días hábiles: documentación + garantía definitiva", ""),
        ("Adjudicación", "5 días hábiles desde la documentación. Publicación en perfil: 15 días", ""),
        ("Formalización", "Con recurso especial: espera 15 hábiles + 5 días tras requerimiento. Sin recurso especial: máx. 15 hábiles", "si")])
    serpiente("h31", "Abierto simplificado, paso a paso", "Art. 159 LCSP", [
        ("Anuncio de licitación", "SOLO en el perfil de contratante. Documentación electrónica desde el día 1", ""),
        ("Presentación de ofertas", "15 días (suministros y servicios) o 20 días (obras), desde la publicación en el perfil", ""),
        ("Requisitos para licitar", "Inscripción en ROLECSP (o solicitud). Sin garantía provisional. Solo en el registro del anuncio", ""),
        ("Sobres y valoración", "1 sobre (sin juicio de valor) o 2 sobres (con juicio de valor). Juicio de valor: 7 días, antes de fórmulas", ""),
        ("Requerimiento al mejor", "7 días hábiles: garantía definitiva + medios adscritos. Oferta anormal: máx. 5 días hábiles", ""),
        ("Adjudicación", "Máximo 5 días (no 5 hábiles)", ""),
        ("Formalización", "Régimen general. Urgencia: NO reduce a la mitad", "si")])
    serpiente("h32", "Abierto supersimplificado, paso a paso", "Art. 159 LCSP", [
        ("Anuncio de licitación", "SOLO en el perfil de contratante", ""),
        ("Presentación de ofertas", "10 días HÁBILES (obras, suministros, servicios). 5 días HÁBILES: compras corrientes de bienes disponibles en el mercado", ""),
        ("Un único sobre", "Solo criterios de fórmula (cero juicio de valor). Declaración responsable incluida", ""),
        ("Valoración", "Automática (informática) o con unidad técnica. SIN acto público de apertura", ""),
        ("Adjudicación", "Sin acreditar solvencia. Sin garantía provisional ni definitiva", ""),
        ("Formalización", "Firma de aceptación por el contratista de la resolución de adjudicación", "si")])
    serpiente("h33", "Restringido, paso a paso", "Arts. 160 a 165 LCSP", [
        ("Anuncio de licitación", "Perfil + BOE (AGE) + DOUE (SARA). Criterios de solvencia ya fijados", ""),
        ("Solicitud de participación", "Cualquier empresa interesada + DEUC. SARA 30 (15 urgencia) / No SARA 15. Sin garantía provisional", ""),
        ("Selección por solvencia", "Criterios objetivos y previos. MÍNIMO 5 candidatos (si hay menos, los que cumplan). Máximo, opcional", ""),
        ("Invitación", "Simultánea y por escrito. Solo a los seleccionados", ""),
        ("Proposiciones", "SARA 30 (10 con anuncio previo o urgencia; 25 si electrónica). No SARA 10. Desde la invitación", ""),
        ("Mesa: clasifica y propone", "SIN NEGOCIACIÓN. Adjudicación: reglas del abierto, 15 días o 2 meses", ""),
        ("Requerimiento y formalización", "10 días hábiles: documentación + garantía definitiva. Adjudicación en 5 hábiles. Formalización: art. 153", "si")])
    serpiente("h34", "Licitación con negociación, paso a paso", "Arts. 166 a 171 LCSP", [
        ("Anuncio de licitación", "Obligatorio (en el negociado sin publicidad NO hay)", ""),
        ("Solicitudes de participación", "Y selección por solvencia (supletorio: restringido)", ""),
        ("Invitación", "MÍNIMO 3 candidatos (en el restringido eran 5). Solo a los que cumplan", ""),
        ("Ofertas iniciales", "Presentadas por los invitados (todavía no se adjudica)", ""),
        ("Negociación", "Ofertas iniciales y ulteriores. Fases sucesivas para reducir ofertas. No negociable: mínimos ni criterios", "az"),
        ("Fin de la negociación", "Se informa a todos los licitadores. Plazo COMÚN para ofertas definitivas (ya no se negocian)", ""),
        ("La mesa", "Verifica requisitos del pliego, valora y eleva la propuesta", ""),
        ("El órgano de contratación", "Adjudica el contrato (requerimiento y formalización)", "si")])
    serpiente("h35", "Asociación para la innovación, paso a paso", "Arts. 177 a 182 LCSP", [
        ("Selección", "Anuncio + solicitudes. SARA 30 / No SARA 20 días. Invitación: mínimo 3", ""),
        ("Proyectos y negociación", "Proyectos de I+D, no producto. Hasta la oferta definitiva", ""),
        ("Adjudicación: la asociación", "Uno o varios socios. Mejor relación calidad-precio (único criterio posible)", ""),
        ("Fases de I+D", "Al final de cada fase: resolver o reducir socios. NUNCA indemniza; sí se paga el trabajo realizado", ""),
        ("Análisis de resultados", "¿Se alcanzan los niveles de rendimiento y costes acordados?", ""),
        ("Adquisición derivada", "Según el PCAP, si el órgano decide comprar. Prestaciones sucesivas: máximo 4 años", "si")])
    serpiente("h36", "Pago y demora de la Administración", "Art. 198 LCSP: del pago a las consecuencias de la mora", [
        ("Entrega o prestación", "Bienes entregados, servicio prestado u obra certificada", ""),
        ("Aprobar los documentos", "Certificación de obra o conformidad de la Administración: 30 días desde la entrega", ""),
        ("Pagar el precio", "30 días desde la aprobación (nunca 60). Pago total o parcial", "si"),
        ("Desde el día 31: mora", "Intereses de demora e indemnización por costes de cobro (Ley 3/2004)", "no"),
        ("Demora superior a 4 meses", "El contratista puede suspender (aviso con 1 mes de antelación)", "no"),
        ("Demora superior a 6 meses", "El contratista puede resolver y reclamar los perjuicios", "no")])

def lote4():
    serpiente("h37", "La resolución del contrato, paso a paso", "Arts. 211 a 213 LCSP", [
        ("Causa de resolución", "Art. 211 (generales) o específicas de cada tipo de contrato", ""),
        ("Inicio del expediente", "De oficio o a instancia del contratista; acuerda el órgano de contratación", ""),
        ("Trámites preceptivos", "Audiencia al contratista, siempre. Consejo de Estado si hay oposición", ""),
        ("Plazo máximo: 8 meses", "Para instruir y resolver el expediente (no son 6 meses)", "no"),
        ("Efectos (art. 213)", "Pronunciamiento expreso sobre la garantía: pérdida, devolución o cancelación", ""),
        ("Nueva licitación", "Puede iniciarse a la vez que el expediente; adjudicación condicionada", "si")])
    # 40 proyecto de obras
    cols = [("1", "ELABORACIÓN", "<b>Quién:</b> un contratista<br><br><b>Regla:</b> contrato de servicios separado del de obras.<br><br><b>Excepción (art. 234):</b> adjudicación conjunta con la obra, motivada por razones técnicas o dimensión y dificultad singular. Requiere anteproyecto previo."),
            ("2", "SUPERVISIÓN", "<b>Quién:</b> oficinas o unidades de supervisión<br><br><b>Preceptiva si:</b><ul><li>PBL ≥ 500.000 € (sin IVA), o</li><li>afecta a estabilidad, seguridad o estanqueidad.</li></ul><br>En los demás casos: <b>facultativa</b>."),
            ("3", "APROBACIÓN", "<b>Quién:</b> el órgano de contratación<br><br>Salvo que una norma jurídica atribuya la competencia a otro órgano."),
            ("4", "REPLANTEO", "<b>Quién:</b> personal técnico de la Administración<br><br><b>Comprueba:</b><ul><li>la realidad geométrica,</li><li>la disponibilidad de terrenos.</li></ul><br><b>Sin contratista:</b> aún no se ha aprobado el expediente.")]
    p = ""; l = ""; w = 240; g = 22
    for i, (n, t, c) in enumerate(cols):
        x = i * (w + g)
        p += caja(x, 0, w, 460, '<span class="num">%s</span><b class="t" style="font-size:21px">%s</b><div style="font-size:18px;margin-top:12px;text-align:left;width:100%%;line-height:1.35">%s</div>' % (n, t, c), "top")
        if i: l += lin([(x - g + 1, 230), (x - 1, 230)])
    pagina("h40", "El proyecto de obras, paso a paso", "Arts. 231 a 236 LCSP", stage(p, l),
           "El proyecto se incorpora al expediente de contratación: el órgano de contratación aprueba el expediente y el gasto, y sigue la adjudicación, la formalización y la ejecución.")
    # 41 línea de tiempo de obras
    p = ""; l = lin([(0, 225), (1018, 225)])
    hitos = [(90, 10, 160, 100, "Formalización", "del contrato", ""), (290, 195, 190, 150, "Acta de comprobación del replanteo", "Inicio de la ejecución (con el contratista)", ""),
             (500, 415, 170, 100, "Terminación", "de la obra", ""), (700, 595, 200, 175, "Acto formal de recepción", "Dentro del mes siguiente. Contrato cumplido. Empieza la garantía. Corren los 15 años.", "az"),
             (940, 812, 215, 205, "Fin del plazo de garantía", "Informe favorable: se extingue la responsabilidad (salvo vicios ocultos), se devuelve la garantía, liquidación y pago (60 días)", "")]
    for x, bx, bw, bh, t, s_, c in hitos:
        top = 195 - bh
        p += caja(bx, top, bw, bh, '<b class="t" style="font-size:18px">%s</b>' % t, c, s_).replace("<small>", '<small style="font-size:16px">')
        l += lin([(x, 195), (x, 225)], False) + '<circle cx="%d" cy="225" r="9" fill="#1f2d44"/>' % x
    def corchete(x1, x2, y):
        return lin([(x1, y), (x1, y + 14), (x2, y + 14), (x2, y)], False)
    l += corchete(90, 290, 252) + corchete(290, 500, 252) + corchete(700, 940, 252) + corchete(700, 860, 372)
    p += '<div style="position:absolute;left:30px;top:285px;width:230px;text-align:center;font-size:19px"><b>≤ 1 mes</b><br>desde la formalización</div>'
    p += '<div style="position:absolute;left:280px;top:285px;width:270px;text-align:center;font-size:19px"><b>Ejecución material</b><br>Certificaciones mensuales (primeros 10 días del mes siguiente) = pagos a cuenta</div>'
    p += '<div style="position:absolute;left:716px;top:280px;width:311px;font-size:17px"><b>Plazo de garantía: ≥ 1 año</b><br>Informe del director facultativo: 15 días antes</div>'
    p += '<div style="position:absolute;left:716px;top:398px;width:311px;font-size:17px"><b>Certificación final: 3 meses desde la recepción</b><br>Hasta 5 si VE > 12 M€ y medición compleja</div>'
    l += lin([(700, 232), (700, 520)], False, True)
    p += caja(700, 520, 327, 80, '<b class="t">Vicios ocultos: 15 años</b>', "q", "Contados desde la recepción, no desde el fin de la garantía")
    pagina("h41", "Ejecución de obras en línea de tiempo", "Arts. 237 a 246 LCSP: de la formalización al fin de la garantía", stage(p, l))
    # 42
    p = ""; l = ""; w = 233; g = 31.7
    cards = [("1", "Expediente", "Necesidad, pliegos, certificado de crédito, informe jurídico", ""), ("2", "Informe de Hacienda", "Solo concesiones de obras o servicios con VE ≥ 12 M€. Preceptivo y vinculante", "disc"),
             ("3", "Autorización del Consejo de Ministros", "VE ≥ 12 M€, arrendamiento financiero > 4 años...", "az"), ("4", "Órgano de contratación", "Aprueba el expediente y el gasto. Después, licitación y adjudicación", "si")]
    for i, (n, t, sx, c) in enumerate(cards):
        x = int(i * (w + g))
        p += caja(x, 0, w, 290, '<span class="num">%s</span><b class="t" style="font-size:21px">%s</b><div style="font-size:19px;margin-top:10px;font-weight:400;line-height:1.35">%s</div>' % (n, t, sx), (c + " top").strip())
        if i: l += lin([(x - 31, 145), (x - 1, 145)])
    notas = ["Todo lo de los pasos 2 y 3 es <b>previo</b> a la aprobación del expediente y del gasto, que sigue siendo del órgano de contratación.",
             "El paso 2 (borde discontinuo) solo existe en las concesiones; en un contrato de obras, suministro o servicios se pasa del 1 al 3.",
             "Si el Consejo de Ministros autorizó el contrato, también autorizará sus modificaciones no previstas de más del 10 % y su resolución."]
    for i, t in enumerate(notas):
        p += caja(0, 330 + i * 80, 1027, 68, t, "gr izq")
    pagina("h42", "Contrato estatal de 12 M€ o más", "Art. 324 LCSP: la preparación, paso a paso", stage(p, l))
    # 43 mapa de clasificaciones
    p = caja(263, 0, 500, 70, '<b class="t" style="font-size:22px">CONTRATO DEL SECTOR PÚBLICO</b>', "q")
    ejes = [("Según su OBJETO", "arts. 12 a 18", ["Obras (art. 13)", "Concesión de obras (art. 14)", "Suministro (art. 16)", "Servicios (art. 17)", "Concesión de servicios (art. 15)", "Contratos mixtos (art. 18)"]),
            ("Según su CUANTÍA", "arts. 19 a 23", ["<b>SARA</b><br>sujeto a regulación armonizada", "<b>No SARA</b>"]),
            ("Según su NATURALEZA", "arts. 24 a 27", ["<b>Administrativo</b><br>solo si lo celebra una Administración Pública", "<b>Privado</b>"])]
    l = ""; w = 330; g = 18
    for i, (t, a, items) in enumerate(ejes):
        x = i * (w + g + 1)
        p += caja(x, 130, w, 90, '<b class="t">%s</b>' % t, "az", a)
        l += lin([(513, 70), (513, 100), (x + w // 2, 100), (x + w // 2, 130)])
        hh = 56 if len(items) == 6 else 150
        for j, it in enumerate(items):
            p += caja(x, 250 + j * (hh + 12), w, hh, it, "")
    pagina("h43", "Mapa de las tres clasificaciones de un contrato", "Un mismo contrato se clasifica por su objeto, su cuantía y su naturaleza", stage(p, l))
    # 45 escala de cuantías
    p = ""; l = ""
    filas = [("OBRAS Y CONCESIONES", [("< 40.000 €", "menor"), ("> 3.000.000 €", "recurso especial"), ("≥ 5.404.000 €", "SARA")]),
             ("SUMINISTRO Y SERVICIOS (AGE)", [("< 15.000 €", "menor"), ("> 100.000 €", "recurso especial"), ("≥ 140.000 €", "SARA")])]
    for r, (t, pts) in enumerate(filas):
        y0 = r * 290
        p += '<div style="position:absolute;left:0;top:%dpx;font-size:23px;font-weight:700">%s</div>' % (y0, t)
        l += lin([(0, y0 + 150), (1018, y0 + 150)])
        for i, (v, e) in enumerate(pts):
            x = 150 + i * 360
            l += '<circle cx="%d" cy="%d" r="11" fill="#1466d9"/>' % (x, y0 + 150)
            p += '<div style="position:absolute;left:%dpx;top:%dpx;width:300px;transform:translateX(-50%%);text-align:center;font-size:30px;font-weight:700;color:var(--azul)">%s</div>' % (x, y0 + 80, v)
            cls = "az" if e == "SARA" else ""
            p += caja(x - 105, y0 + 185, 210, 56, '<b class="t">%s</b>' % e, cls)
    pagina("h45", "Escala de cuantías", "Arts. 19, 44 y 118 LCSP: menor, recurso especial y SARA", stage(p, l))
    # 46 cinco contratos típicos
    cab = [("OBRAS", "art. 13"), ("CONCESIÓN DE OBRAS", "art. 14"), ("SUMINISTRO", "art. 16"), ("SERVICIOS", "art. 17"), ("CONCESIÓN DE SERVICIOS", "art. 15")]
    filas = [("Objeto", ["Bien inmueble", "Bien inmueble", "Bien mueble", "Hacer algo", "Gestionar un servicio"]),
             ("Riesgo y explotación", ["No", "Sí", "No", "No", "Sí"]),
             ("Adjudica", ["Cualquier ente del sector público"] * 4 + ["SOLO poder adjudicador (niveles 1 y 2)"])]
    t = '<table class="t g"><tr><th></th>' + "".join('<th>%s<br><span style="font-weight:500;font-size:16px">%s</span></th>' % c for c in cab) + "</tr>"
    for n, vs in filas:
        t += "<tr><td>%s</td>" % n
        for v in vs:
            cl = "si" if v == "Sí" else "no" if v == "No" else ""
            t += '<td><span class="%s">%s</span></td>' % (cl, v) if cl else "<td>%s</td>" % v
        t += "</tr>"
    t += "</table>"
    pagina("h46", "Los cinco contratos típicos", "Arts. 13 a 18 LCSP: qué cambia de uno a otro", '<div class="stage">%s</div>' % t,
           "<b>Solo la concesión de servicios</b> la adjudica únicamente un poder adjudicador (niveles 1 y 2).")

HOJAS = {"h37": 0, "h40": 0, "h41": 0, "h42": 0, "h43": 0, "h45": 0, "h46": 0, "h25": 0, "h26": 0, "h27": 0, "h28": 0, "h29": 0, "h30": 0, "h31": 0, "h32": 0, "h33": 0, "h34": 0, "h35": 0, "h36": 0, "h13": 0, "h14": 0, "h15": 0, "h16": 0, "h17": 0, "h18": 0, "h19": 0, "h21": 0, "h22": 0, "h23": 0, "h24": 0, "h1": lote1, "h2": lote1, "h3": lote1, "h4": lote1, "h5": lote1, "h6": lote1, "h7": lote1, "h8": lote1, "h9": lote1, "h10": lote1, "h11": lote1, "h12": lote1}

def pintar(nombre):
    png = os.path.join(AQUI, nombre + ".png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2.14",
                    "--window-size=1123,794", "--screenshot=" + png, "file://" + os.path.join(AQUI, nombre + ".html")],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

if __name__ == "__main__":
    lote1(); lote2(); lote3(); lote4()
    for n in (sys.argv[1:] or HOJAS):
        pintar(n)
    print("hecho")
