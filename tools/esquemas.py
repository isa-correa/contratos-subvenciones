#!/usr/bin/env python3
"""Convierte los PDF de esquemas a imagen y genera data/esquemas.js.

Uso: python3 -I tools/esquemas.py <carpeta con los PDF>     (la carpeta "ordenado")

Cada esquema se guarda como WebP (una imagen por página) en img/esquemas/.
data/esquemas.js lleva el catálogo (window.ESQUEMAS) y la relación entre cada
pregunta y sus esquemas (window.ESQ_PREG).

La relación se hace por artículo: cada esquema declara qué artículos de la LCSP
cubre (ARTICULOS) y una pregunta recibe los esquemas que cubren alguno de los
artículos de su precepto. Primero van los esquemas más concretos (menos artículos)
y no se pasa de MAX_POR_PREGUNTA. Solo se usan preguntas de la LCSP.
"""
import json, os, re, sys, glob
import fitz  # PyMuPDF
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHO = 2400          # píxeles de ancho: suficiente para acercar el zoom sin ver borroso
MAX_POR_PREGUNTA = 4  # esquemas como máximo en el botón de una pregunta
RANGO_MAX = 40        # un precepto con un rango más ancho ("arts. 188 a 347") no apunta a nada concreto

# ruta del PDF -> (id corto, título, artículos que cubre)
# Los artículos se escriben como "149", "100-102" o varios separados por comas.
ARTICULOS = [
    ("00_Mapas_generales/01_Que_plazo_corre_cuando.pdf", "plazos", "¿Qué plazo corre cuándo? Todos los plazos de un contrato", ""),
    ("00_Mapas_generales/02_Eje_De_la_necesidad_a_la_extincion.pdf", "eje-vida", "Eje cronológico: de la necesidad a la extinción", ""),
    ("01_Ambito_clasificacion_y_duracion/01_Eje_Duracion_y_prorrogas.pdf", "eje-duracion", "Eje cronológico: duración y prórrogas, art. 29", "29"),
    ("02_Perfeccion_nulidad_recurso_aptitud_precio_y_garantias/01_Objeto_lotes_y_fraccionamiento_art_99.pdf", "objeto-99", "Objeto, lotes y fraccionamiento, art. 99", "99"),
    ("02_Perfeccion_nulidad_recurso_aptitud_precio_y_garantias/02_PBL_valor_estimado_y_precio_arts_100-102.pdf", "pbl-100", "PBL, valor estimado y precio, arts. 100 a 102", "100-102"),
    ("02_Perfeccion_nulidad_recurso_aptitud_precio_y_garantias/03_Revision_de_precios_art_103.pdf", "revision-103", "Revisión de precios, art. 103", "103"),
    ("02_Perfeccion_nulidad_recurso_aptitud_precio_y_garantias/04_PBL_valor_estimado_y_precio_umbrales_y_cuantias.pdf", "pbl-umbrales", "PBL, valor estimado y precio: qué cifra mide cada umbral", "100-102"),
    ("03_Preparacion_del_contrato/01_Contrato_menor_art_118.pdf", "menor-118", "Contrato menor, art. 118", "118"),
    ("04_Adjudicacion_normas_generales/01_Ofertas_anormalmente_bajas_art_149.pdf", "oab-149", "Ofertas anormalmente bajas, art. 149", "149"),
    ("04_Adjudicacion_normas_generales/02_Eje_Recurso_especial_y_formalizacion.pdf", "eje-recurso", "Eje cronológico: recurso especial y formalización", "44-60,153"),
    ("05_Procedimientos_de_adjudicacion/01_Cual_es_el_mas_agil_arts_118_156-159.pdf", "agil", "Cuál es el procedimiento más ágil", "118,156-159"),
    ("05_Procedimientos_de_adjudicacion/02_Abierto_cuando_se_puede_usar_arts_156-159.pdf", "abierto-uso", "Abierto, simplificado y supersimplificado: cuándo se puede usar cada uno", "156-159"),
    ("05_Procedimientos_de_adjudicacion/03_Abierto_plazos_minimos_art_156.pdf", "abierto-plazos", "Abierto: plazos mínimos de presentación, art. 156", "156"),
    ("05_Procedimientos_de_adjudicacion/04_Abierto_plazo_de_presentacion_3_variantes.pdf", "abierto-3", "Plazo de presentación de las tres variantes del abierto", "156,159"),
    ("05_Procedimientos_de_adjudicacion/05_Abierto_linea_temporal_fases_y_plazos.pdf", "abierto-linea", "Abierto: línea temporal de fases y plazos", "156"),
    ("05_Procedimientos_de_adjudicacion/06_Abierto_especialidades_de_tramitacion.pdf", "abierto-espec", "Abierto: especialidades de tramitación", "156-159"),
    ("05_Procedimientos_de_adjudicacion/07_Restringido_y_extraordinarios_cual_uso_arts_160-182.pdf", "restringido-uso", "Restringido y extraordinarios: ¿cuál uso?, arts. 160 a 182", "160-182"),
    ("05_Procedimientos_de_adjudicacion/08_Los_5_procedimientos_cara_a_cara_arts_160-182.pdf", "cinco-proc", "Los 5 procedimientos, cara a cara", "160-182"),
    ("05_Procedimientos_de_adjudicacion/09_Cifras_y_trampas_de_examen_arts_160-182.pdf", "trampas-proc", "Cifras y trampas de examen", "160-182"),
    ("05_Procedimientos_de_adjudicacion/10_Dialogo_competitivo_arts_172-176.pdf", "dialogo", "Diálogo competitivo, arts. 172 a 176", "172-176"),
    ("05_Procedimientos_de_adjudicacion/11_Negociado_sin_publicidad_arts_168-171.pdf", "negociado", "Negociado sin publicidad, arts. 168 a 171", "168-171"),
    ("05_Procedimientos_de_adjudicacion/12_Eje_Abierto_simplificado_y_supersimplificado.pdf", "eje-simplificado", "Eje cronológico: abierto simplificado y supersimplificado", "159"),
    ("05_Procedimientos_de_adjudicacion/13_Eje_Restringido_dos_fases.pdf", "eje-restringido", "Eje cronológico: restringido, las dos fases", "160-165"),
    ("05_Procedimientos_de_adjudicacion/14_Eje_Negociacion_dialogo_negociado_y_asociacion.pdf", "eje-negociacion", "Eje cronológico: negociación, diálogo, negociado y asociación", "166-182"),
    ("06_Racionalizacion_tecnica/01_Contratos_basados_nueva_licitacion_art_221.pdf", "cb-221", "Art. 221, contratos basados: ¿hay nueva licitación?", "218-222"),
    ("06_Racionalizacion_tecnica/02_Sistema_dinamico_de_adquisicion_paso_a_paso_arts_223-226.pdf", "sda", "Sistema dinámico de adquisición, paso a paso, arts. 223 a 226", "223-226"),
    ("07_Ejecucion_del_contrato/01_Mapa_del_bloque_arts_190-215.pdf", "ejec-mapa", "La ejecución del contrato, de principio a fin: mapa del bloque", "190-215"),
    ("07_Ejecucion_del_contrato/02_Prerrogativas_de_la_Administracion_arts_190-191.pdf", "prerrogativas", "Prerrogativas de la Administración, arts. 190 y 191", "190-191"),
    ("07_Ejecucion_del_contrato/03_Cumplimiento_defectuoso_parcial_y_demora_art_192.pdf", "incumplimiento-192", "Cumplimiento defectuoso, incumplimiento parcial y demora, art. 192", "192"),
    ("07_Ejecucion_del_contrato/04_Demora_en_la_ejecucion.pdf", "demora-ejec", "Demora en la ejecución", "193"),
    ("07_Ejecucion_del_contrato/05_Computo_del_pago_tracto_sucesivo_art_198.pdf", "pago-198", "Cómputo del pago en un contrato de tracto sucesivo, art. 198", "198"),
    ("07_Ejecucion_del_contrato/06_Demora_de_la_Administracion_en_el_pago.pdf", "demora-pago", "Demora de la Administración en el pago", "198"),
    ("07_Ejecucion_del_contrato/07_Suspension_del_contrato_art_208.pdf", "suspension-208", "Suspensión del contrato, art. 208", "208"),
    ("07_Ejecucion_del_contrato/08_Quien_paga_danos_a_terceros_y_riesgo_y_ventura_arts_196-197.pdf", "danos-196", "¿Quién paga? Daños a terceros y riesgo y ventura, arts. 196 y 197", "196-197"),
    ("07_Ejecucion_del_contrato/09_Modificaciones_limites_arts_204-205.pdf", "modif-204", "Modificaciones: tipos y límites, arts. 204 y 205", "204-205"),
    ("07_Ejecucion_del_contrato/10_Modificacion_arbol_de_decision_arts_203-207.pdf", "modif-arbol", "Modificación del contrato: árbol de decisión, arts. 203 a 207", "203-207"),
    ("07_Ejecucion_del_contrato/11_Cumplimiento_plazo_de_garantia_y_liquidacion.pdf", "garantia-210", "Cumplimiento, plazo de garantía y liquidación", "210"),
    ("07_Ejecucion_del_contrato/12_Resolucion_I_causas_generales_arts_211-212.pdf", "resol-1", "Resolución (I): causas generales, arts. 211 y 212", "211-212"),
    ("07_Ejecucion_del_contrato/13_Resolucion_II_procedimiento_y_efectos_arts_212-213.pdf", "resol-2", "Resolución (II): procedimiento y efectos, arts. 212 y 213", "212-213"),
    ("07_Ejecucion_del_contrato/14_Resolucion_causas_especificas_obras_suministros_servicios.pdf", "resol-espec", "Resolución: causas específicas de obras, suministros y servicios", "245,246,306,307,313"),
    ("07_Ejecucion_del_contrato/15_Resolucion_indemnizacion_y_otras_reglas.pdf", "resol-indem", "Resolución: cómo se calcula la indemnización y otras reglas", "213"),
    ("07_Ejecucion_del_contrato/16_Cesion_y_subcontratacion_arts_214-215.pdf", "cesion", "Cesión y subcontratación, arts. 214 y 215", "214-215"),
    ("07_Ejecucion_del_contrato/17_Eje_Pago_y_demora_de_la_Administracion.pdf", "eje-pago", "Eje cronológico: pago y demora de la Administración", "198"),
    ("08_Por_tipo_de_contrato/01_Obras/01_Tipos_de_obra_mapa_art_232.pdf", "obra-tipos", "Tipos de obra: mapa de la clasificación, art. 232", "232"),
    ("08_Por_tipo_de_contrato/01_Obras/02_Tipos_de_obra_conservacion_mantenimiento_reparacion_art_232.pdf", "obra-conserv", "Tipos de obra: conservación, mantenimiento y reparación", "232"),
    ("08_Por_tipo_de_contrato/01_Obras/03_Proyecto_PESAR_arts_231-236.pdf", "obra-pesar", "Proyecto de obras: PESAR, quién hace cada paso", "231-236"),
    ("08_Por_tipo_de_contrato/01_Obras/04_Proyecto_contratacion_separada_arts_231-237.pdf", "obra-separada", "Proyecto de obras: contratación separada (regla general)", "231-237"),
    ("08_Por_tipo_de_contrato/01_Obras/05_Proyecto_contratacion_conjunta_arts_231-237.pdf", "obra-conjunta", "Proyecto de obras: contratación conjunta (excepcional)", "231-237"),
    ("08_Por_tipo_de_contrato/01_Obras/06_Ejecucion_de_la_formalizacion_a_la_terminacion_arts_237-244.pdf", "obra-ejec", "Ejecución de obras: de la formalización a la terminación", "237-244"),
    ("08_Por_tipo_de_contrato/01_Obras/07_Ejecucion_recepcion_y_sus_efectos_arts_237-244.pdf", "obra-recepcion", "Ejecución de obras: la recepción y sus efectos", "237-244"),
    ("08_Por_tipo_de_contrato/02_Concesion_de_obras/01_Concesion_de_obras_arts_247-283.pdf", "conc-obras", "Concesión de obras, arts. 247 a 283", "247-283"),
    ("08_Por_tipo_de_contrato/03_Concesion_de_servicios/01_Concesion_de_servicios_arts_284-297.pdf", "conc-serv", "Concesión de servicios, arts. 284 a 297", "284-297"),
    ("08_Por_tipo_de_contrato/04_Suministro/01_Suministro_arts_298-307.pdf", "suministro", "Contrato de suministro, arts. 298 a 307", "298-307"),
    ("08_Por_tipo_de_contrato/04_Suministro/02_Eje_Suministro_entrega_garantia_y_resolucion.pdf", "eje-suministro", "Eje cronológico: suministro, de la entrega a la garantía", "298-307"),
    ("08_Por_tipo_de_contrato/05_Servicios/01_Servicios_arts_308-315.pdf", "servicios", "Contrato de servicios, arts. 308 a 315", "308-315"),
    ("08_Por_tipo_de_contrato/05_Servicios/02_Eje_Servicios_ejecucion_garantia_y_resolucion.pdf", "eje-servicios", "Eje cronológico: servicios, ejecución, garantía y resolución", "308-315"),
    ("09_Organizacion_administrativa/01_Mesa_de_contratacion_art_326.pdf", "mesa-326", "Mesa de contratación, art. 326", "326"),
]


# Esquemas que solo existen como dibujo SVG dentro de LCSP_apuntes_fuente.html.
# número -> (título, artículos). Los 38 y 39 ya están como PDF (cb-221 y sda) y los 47, 48 y 49
# son duplicados exactos del 8, el 28 y el 41, así que no se repiten.
HTML = {
    1: ("Carácter básico y estructura de la ley", ""),
    2: ("Art. 2, ámbito de aplicación", "2"),
    3: ("Art. 3, ámbito subjetivo", "3"),
    4: ("Compraventa, donación, permuta y arrendamiento de bienes", "9"),
    5: ("Art. 12, calificación de los contratos (1)", "12"),
    6: ("Art. 12, calificación de los contratos (2)", "12"),
    7: ("Art. 19, contratos SARA", "19"),
    8: ("Arts. 24 a 27, administrativos y privados", "24-27"),
    9: ("Las prórrogas: reglas generales", "29"),
    10: ("Plazos máximos de duración por tipo de contrato", "29"),
    11: ("Art. 30, ejecución por la propia Administración", "30"),
    12: ("Cuatro requisitos del medio propio personificado", "32"),
    13: ("Art. 36, perfección", "36"),
    14: ("Art. 37, carácter formal", "37"),
    15: ("Art. 41, revisión de oficio", "41"),
    16: ("Art. 42, efectos de la nulidad", "42"),
    17: ("Art. 44, actos recurribles", "44"),
    18: ("Suspensión automática al recurrir", "49-53"),
    19: ("Recurso contencioso-administrativo posterior", "44,59"),
    20: ("Fases de la contratación y qué se publica en cada una", "63"),
    21: ("Art. 72, prohibiciones de contratar", "71-73"),
    22: ("Art. 82, vigencia de las clasificaciones", "82"),
    23: ("Art. 90, solvencia técnica en servicios", "90"),
    24: ("Arts. 106 a 111, garantías", "106-111"),
    25: ("Ordinaria, urgente o emergencia", "119-120"),
    26: ("Quién y cuándo (pliegos y autorización del gasto)", "116-117,122"),
    27: ("Adjudicación: normas generales", "131-155"),
    28: ("Criterios de adjudicación, la clasificación", "145-146"),
    29: ("Plazo para formalizar según el recurso especial", "153"),
    30: ("Abierto ordinario, paso a paso", "156"),
    31: ("Abierto simplificado, paso a paso", "159"),
    32: ("Abierto supersimplificado, paso a paso", "159"),
    33: ("Restringido, paso a paso", "160-165"),
    34: ("Licitación con negociación, paso a paso", "166-171"),
    35: ("Asociación para la innovación, paso a paso", "177-182"),
    36: ("Pago y demora de la Administración, paso a paso", "198"),
    37: ("La resolución del contrato, paso a paso", "211-213"),
    40: ("El proyecto de obras, paso a paso", "231-236"),
    41: ("Ejecución de obras en línea de tiempo", "237-246"),
    42: ("Preparación de un contrato estatal de 12 M€ o más, paso a paso", "324"),
    43: ("Mapa de las tres clasificaciones de un contrato", "12,24-27"),
    44: ("Los tres niveles del sector público", "3"),
    45: ("Escala de cuantías: menor, recurso especial, SARA", "19,44,118"),
    46: ("Los cinco contratos típicos", "13-18"),
}
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FUENTE = "LCSP_apuntes_fuente.html"
ESCALA = 3  # los dibujos son pequeños (unos 600 px): se pintan a 3x para que el zoom no se vea borroso


# Esquemas generales que no cuelgan de un artículo: se añaden por lo que dice la pregunta.
# (id del esquema, expresión sobre el enunciado y el precepto, dónde va, texto extra que exige el precepto)
REGLAS = [
    ("plazos", r"\bplazos?\b|\bd[ií]as\b", "final", None),
    ("eje-vida", r"cronol[oó]gic|orden de (las )?fases|fases? (del|de la) (contrat|licitaci)|ciclo|extinci[oó]n del contrato", "final", None),
    ("h1", r"car[aá]cter b[aá]sico|estructura de la ley|libro (primero|segundo|tercero|cuarto)|pre[aá]mbulo", "final", None),
    ("trampas-proc", r"\d+\s*(d[ií]as|%|euros|€|horas|meses|a[nñ]os)|\b(umbral|cuant[ií]a|importe)\b", "inicio", range(160, 183)),
]


# Cómo se ordenan en la pestaña Apuntes: bloques del temario, como en el índice de "ordenado".
BLOQUES = [
    ("00", "Mapas generales", "Los tres niveles del sector público, las clasificaciones, los cinco contratos típicos y las cuantías. Para empezar y para repasar."),
    ("01", "Ámbito, clasificación y duración", "Arts. 1 a 33. Qué contratos entran en la ley y de qué tipo son."),
    ("02", "Perfección, nulidad, recurso, aptitud, precio y garantías", "Arts. 36 a 111. La vida jurídica del contrato, quién puede contratar, cuánto cuesta y qué garantías hay."),
    ("03", "Preparación del contrato", "Arts. 115 a 130. Del expediente a los pliegos."),
    ("04", "Adjudicación: normas generales", "Arts. 131 a 155. Anuncios, plazos, criterios y formalización."),
    ("05", "Procedimientos de adjudicación", "Arts. 156 a 182. El abierto en sus tres variantes y los demás."),
    ("06", "Racionalización técnica", "Arts. 218 a 230. Acuerdo marco, sistema dinámico y centrales."),
    ("07", "Ejecución del contrato", "Arts. 188 a 215. Penalidades, pago, modificación, suspensión y resolución."),
    ("08", "Por tipo de contrato", "Arts. 231 a 315. Obras, concesiones, suministros y servicios."),
    ("09", "Organización administrativa", "Arts. 323 a 347. Quién contrata y quién asiste."),
]
# Bloque de cada dibujo HTML (los PDF lo toman del número de su carpeta).
HTML_BLOQUE = {}
for _n in (1, 43, 44, 45, 46, 20): HTML_BLOQUE[_n] = "00"
for _n in range(2, 13): HTML_BLOQUE[_n] = "01"
for _n in (13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24): HTML_BLOQUE[_n] = "02"
for _n in (25, 26): HTML_BLOQUE[_n] = "03"
for _n in (27, 28, 29): HTML_BLOQUE[_n] = "04"
for _n in range(30, 36): HTML_BLOQUE[_n] = "05"
for _n in (36, 37): HTML_BLOQUE[_n] = "07"
for _n in (40, 41): HTML_BLOQUE[_n] = "08"
HTML_BLOQUE[42] = "09"
# Dentro de "Por tipo de contrato" los esquemas se agrupan por tipo.
GRUPOS_08 = [("01_Obras", "Obras"), ("02_Concesion_de_obras", "Concesión de obras"), ("03_Concesion_de_servicios", "Concesión de servicios"),
             ("04_Suministro", "Suministro"), ("05_Servicios", "Servicios")]
# En "Mapas generales" el orden es el del índice y no el de los artículos.
ORDEN_00 = ["h1", "h43", "h44", "h45", "h46", "h20", "plazos", "eje-vida"]


def arts_de(spec):
    """'44-60,153' -> {44..60, 153}"""
    res = set()
    for t in filter(None, (x.strip() for x in spec.split(","))):
        if "-" in t:
            a, b = t.split("-"); res.update(range(int(a), int(b) + 1))
        else:
            res.add(int(t))
    return res


def convertir(carpeta, eid, ruta):
    doc = fitz.open(os.path.join(carpeta, ruta))
    salida = os.path.join(RAIZ, "img", "esquemas")
    os.makedirs(salida, exist_ok=True)
    paginas = []
    for n, pg in enumerate(doc, 1):
        zoom = ANCHO / pg.rect.width
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        archivo = "%s-%d.webp" % (eid, n)
        img.save(os.path.join(salida, archivo), "WEBP", quality=82, method=6)
        paginas.append({"src": "img/esquemas/" + archivo, "w": pix.width, "h": pix.height})
    return paginas


def dibujos(carpeta):
    """número de esquema -> código HTML de su diagrama, sacado del HTML fuente."""
    h = open(os.path.join(carpeta, FUENTE), encoding="utf-8").read()
    res = {}
    for m in re.finditer(r'<span id="esq-(\d+)"></span>', h):
        i = h.find('<div class="diagrama"', m.end()); prof = 0
        for t in re.finditer(r"<div\b|</div>", h[i:]):
            prof += 1 if t.group(0) == "<div" else -1
            if prof == 0:
                res[int(m.group(1))] = h[i:i + t.end()]; break
    return res


def convertir_html(num, codigo, eid, tmp):
    """Pinta un diagrama SVG con Chrome sin ventana y lo guarda como WebP recortado.
    Si existe un rediseño en tools/nuevos/<id>.png (hoja A4 apaisada hecha con generar.py), se usa ese."""
    import subprocess
    nuevo = os.path.join(RAIZ, "tools", "nuevos", "%s.png" % eid)
    if os.path.exists(nuevo):
        img = Image.open(nuevo).convert("RGB")
        salida = os.path.join(RAIZ, "img", "esquemas"); os.makedirs(salida, exist_ok=True)
        archivo = "%s-1.webp" % eid
        img.save(os.path.join(salida, archivo), "WEBP", quality=88, method=6)
        return [{"src": "img/esquemas/" + archivo, "w": img.width, "h": img.height}]
    vb = re.search(r'viewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"', codigo)
    ancho, alto = float(vb.group(1)), float(vb.group(2))
    # Quicksand no está en el equipo que pinta: se usa una fuente de ancho parecido.
    codigo = codigo.replace("Quicksand", "Arial")
    pagina = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:16px;background:#fff;'
              'font:14px/1.4 Arial,sans-serif;color:#111}.diagrama{text-align:center}'
              '.diagrama svg{max-width:100%%;height:auto}</style>%s' % codigo)
    html = os.path.join(tmp, "e%d.html" % num); png = os.path.join(tmp, "e%d.png" % num)
    open(html, "w", encoding="utf-8").write(pagina)
    W, H = int(max(ancho, 560) + 32), int(alto + 420)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--screenshot=" + png,
                    "--window-size=%d,%d" % (W, H), "--force-device-scale-factor=%d" % ESCALA,
                    "--default-background-color=FFFFFFFF", "file://" + html],
                   check=True, capture_output=True, timeout=60)
    img = Image.open(png).convert("RGB")
    # Se recorta el blanco sobrante y se deja un margen.
    from PIL import ImageChops
    caja = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    m = 12 * ESCALA
    caja = (max(0, caja[0] - m), max(0, caja[1] - m), min(img.width, caja[2] + m), min(img.height, caja[3] + m))
    img = img.crop(caja)
    salida = os.path.join(RAIZ, "img", "esquemas"); os.makedirs(salida, exist_ok=True)
    archivo = "%s-1.webp" % eid
    img.save(os.path.join(salida, archivo), "WEBP", quality=85, method=6)
    return [{"src": "img/esquemas/" + archivo, "w": img.width, "h": img.height}]


def respuestas():
    res = {}
    for f in sorted(glob.glob(os.path.join(RAIZ, "tools", "respuestas", "lote-*.json"))):
        res.update(json.load(open(f, encoding="utf-8")))
    return res


def articulos_citados(precepto):
    """Artículos que cita un precepto: 'arts. 118.1, 159.1 y 22.1' -> {118, 159, 22}."""
    res = set()
    for m in re.finditer(r"\barts?\b\.?\s*(.*)", precepto, re.I):
        resto = re.split(r"\sde\s|[);]|\bLey\b|\bLCSP\b|\bRD\b|\bReal\b", m.group(1))[0]
        for n in re.finditer(r"(\d+)(?:\.[\w]+)*(?:\s*(?:a|-)\s*(\d+)(?:\.[\w]+)*)?", resto):
            a = int(n.group(1))
            if n.group(2):
                b = int(n.group(2))
                if b - a > RANGO_MAX: continue
                res.update(range(a, b + 1))
            else:
                res.add(a)
    return res


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    carpeta = sys.argv[1]
    catalogo, cubre = {}, {}
    for ruta, eid, tit, arts in ARTICULOS:
        catalogo[eid] = {"titulo": tit, "paginas": convertir(carpeta, eid, ruta)}
        cubre[eid] = arts_de(arts)
    import tempfile
    tmp = tempfile.mkdtemp()
    dib = dibujos(carpeta)
    for num, (tit, arts) in HTML.items():
        eid = "h%d" % num
        catalogo[eid] = {"titulo": tit, "paginas": convertir_html(num, dib[num], eid, tmp)}
        cubre[eid] = arts_de(arts)
    orden = {eid: n for n, eid in enumerate(catalogo)}
    por_pregunta = {}
    for pid, r in respuestas().items():
        if not r.get("bloque", "").startswith("lcsp-"): continue
        txt = r.get("precepto", "") or ""
        if re.search(r"Ley \d+/\d+|LPAC|LRJSP|Constituci", txt) and "LCSP" not in txt and "9/2017" not in txt: continue
        cit = articulos_citados(txt)
        if not cit: continue
        # Primero los esquemas que mejor encajan: más artículos de la pregunta cubiertos y menos artículos en total.
        cand = [(-len(cit & cubre[e]), len(cubre[e]), orden[e], e) for e in cubre if cit & cubre[e]]
        if cand:
            por_pregunta[pid] = [c[3] for c in sorted(cand)[:MAX_POR_PREGUNTA]]
    # Reglas por contenido
    enun = {q["id"]: q.get("enunciado", "") for q in json.load(open(os.path.join(RAIZ, "tools", "preguntas.json"), encoding="utf-8"))["preguntas"]}
    for eid, rx, donde, arts in REGLAS:
        for pid, r in respuestas().items():
            if not r.get("bloque", "").startswith("lcsp-"): continue
            texto = (enun.get(pid, "") + " " + (r.get("precepto", "") or ""))
            if not re.search(rx, texto, re.I): continue
            lista = por_pregunta.setdefault(pid, [])
            if eid in lista: continue
            if arts is not None and not (articulos_citados(r.get("precepto", "") or "") & set(arts)): continue
            if donde == "inicio": lista.insert(0, eid); del lista[MAX_POR_PREGUNTA:]
            elif len(lista) < MAX_POR_PREGUNTA: lista.append(eid)
    por_pregunta = {k: v for k, v in por_pregunta.items() if v}
    # Ordenación para la pestaña Apuntes
    ficha = {}  # id -> (bloque, grupo, es_pdf)
    for ruta, eid, tit, arts in ARTICULOS:
        partes = ruta.split("/")
        grupo = None
        if partes[0][:2] == "08":
            grupo = dict(GRUPOS_08)[partes[1]]
        ficha[eid] = (partes[0][:2], grupo, 1)
    for num in HTML:
        ficha["h%d" % num] = (HTML_BLOQUE[num], "Obras" if HTML_BLOQUE[num] == "08" else None, 0)
    apuntes = []
    for bid, nombre, desc in BLOQUES:
        ids = [e for e in catalogo if ficha[e][0] == bid]
        if bid == "00":
            ids.sort(key=ORDEN_00.index)
        else:
            ids.sort(key=lambda e: (min(cubre[e]) if cubre[e] else 9999, ficha[e][2], orden[e]))
        grupos = []
        if bid == "08":
            for _, g in GRUPOS_08:
                gi = [e for e in ids if ficha[e][1] == g]
                if gi: grupos.append({"nombre": g, "ids": gi})
        else:
            grupos.append({"nombre": None, "ids": ids})
        apuntes.append({"id": bid, "nombre": nombre, "desc": desc, "grupos": grupos})
    for ruta, eid, tit, arts in ARTICULOS: catalogo[eid]["a"] = arts
    for num, (tit, arts) in HTML.items(): catalogo["h%d" % num]["a"] = arts
    with open(os.path.join(RAIZ, "data", "esquemas.js"), "w", encoding="utf-8") as f:
        f.write("window.APUNTES = " + json.dumps(apuntes, ensure_ascii=False) + ";\n")
        f.write("window.ESQUEMAS = " + json.dumps(catalogo, ensure_ascii=False) + ";\n")
        f.write("window.ESQ_PREG = " + json.dumps(por_pregunta, ensure_ascii=False) + ";\n")
    total = sum(1 for r in respuestas().values() if r.get("bloque", "").startswith("lcsp-"))
    print("esquemas:", len(catalogo), "· preguntas LCSP con esquema:", len(por_pregunta), "de", total)
    sin = [e for e in catalogo if not any(e in v for v in por_pregunta.values())]
    print("esquemas sin ninguna pregunta:", sin)


if __name__ == "__main__":
    main()
