"""Lo que el profesor marca en LCSP_apuntes_fuente.html como muy preguntado, estrella o poco preguntado.

Cada marca se ata a artículos de la LCSP. Una pregunta recibe la marca si su precepto cita ese artículo
(o ese apartado: "145.4" atrapa "art. 145.4" y "art. 145.4.b", pero no "art. 145.2").
Si a una pregunta le tocan varias, gana la de más nivel: estrella, luego clave, luego poco.
Solo se aplica a preguntas de contratos (bloques lcsp-*).

Para añadir una marca: una línea más en MARCAS con (nivel, artículos, lo que dice el profesor).
Los artículos van separados por comas; "231-246" es un rango de artículos enteros.
"""
import re

NIVELES = {"estrella": 3, "clave": 2, "poco": 1}

MARCAS = [
    # ---------- Estrella: el profesor dice que es lo que más cae ----------
    ("estrella", "29", "El artículo con más preguntas de examen de todo el temario de contratos."),
    ("estrella", "150", "Artículo estrella: la secuencia de clasificación y adjudicación, con plazos muy preguntados."),
    ("estrella", "198.4", "La pregunta estrella del pago: los dos plazos de 30 días."),
    ("estrella", "9.2", "La pregunta estrella del art. 9: comprar o alquilar un edificio ya construido es un contrato excluido."),
    ("estrella", "62.2", "La pregunta estrella del art. 62: en obras, el responsable del contrato es el director facultativo."),

    # ---------- Clave de examen: recuadros «Pregunta de examen» y frases de «muy preguntado» ----------
    ("clave", "1.1", "Los principios de la contratación pública son la respuesta típica a esta pregunta."),
    ("clave", "11", "Lista variada, pero muy preguntada en su conjunto."),
    ("clave", "13-17", "La definición de cada contrato típico es lo que más se pregunta de estos contratos."),
    ("clave", "DA12", "Regla muy preguntada: salvo que se diga lo contrario, los plazos de la ley son días naturales."),
    ("clave", "122.1, 124", "Pregunta de examen: quién aprueba los pliegos y cuándo."),
    ("clave", "126", "Las reglas de las prescripciones técnicas: el profesor dice que las más preguntadas son cuatro."),
    ("clave", "131.4", "Pregunta literal de examen: asistencia sanitaria urgente por debajo de 30.000 €."),
    ("clave", "140.4", "Pregunta de examen: en qué momento hay que cumplir los requisitos para contratar."),
    ("clave", "145.2", "Pregunta de examen: los criterios cualitativos nunca van solos, siempre con uno de costes."),
    ("clave", "145.4", "Pregunta de examen: contratos en los que la calidad debe pesar al menos el 51 %."),
    ("clave", "146.2", "Pregunta de examen: primero se valora lo que va por juicio de valor y después las fórmulas."),
    ("clave", "152", "Pregunta de examen: renuncia y desistimiento solo caben antes de formalizar."),
    ("clave", "160", "Pregunta de examen: en el restringido está prohibida toda negociación."),
    ("clave", "162.1", "Pregunta de examen: en el restringido se invita como mínimo a 5."),
    ("clave", "169", "Pregunta de examen: en la licitación con negociación el mínimo es 3, no 5."),
    ("clave", "172", "Pregunta de examen: primas o compensaciones a los participantes del diálogo competitivo."),
    ("clave", "191.3", "Pregunta de examen: cuándo es preceptivo el dictamen del Consejo de Estado."),
    ("clave", "192.1", "Pregunta de examen: los topes de las penalidades."),
    ("clave", "193.2", "Pregunta de examen: el contratista cae en mora sin necesidad de intimación."),
    ("clave", "194.2", "Pregunta de examen: quién impone las penalidades."),
    ("clave", "195.2", "Pregunta de examen: cuánto se amplía el plazo de ejecución."),
    ("clave", "196.3", "Pregunta de examen: el requerimiento al órgano de contratación, dentro del año."),
    ("clave", "202.1", "Pregunta de examen: siempre al menos una condición especial de ejecución social o medioambiental."),
    ("clave", "204.1", "Pregunta de examen: las modificaciones previstas, hasta el 20 % del precio inicial."),
    ("clave", "208.2", "Pregunta de examen: solo se indemniza la suspensión documentada en el acta."),
    ("clave", "209, 210.2", "Pregunta de examen: cómo se extingue un contrato y plazo de la recepción."),
    ("clave", "212.8", "Pregunta de examen: la resolución se tramita en 8 meses como máximo."),
    ("clave", "215.2, 215.4", "Pregunta de examen: subcontratar se comunica, no se autoriza, y quién responde."),
    ("clave", "219.2, 219.3", "Pregunta de examen: cuánto dura un acuerdo marco y sus contratos basados."),
    ("clave", "223-224", "Pregunta de examen: cuánto dura un sistema dinámico de adquisición."),
    ("clave", "226", "Pregunta de examen: en el sistema dinámico siempre hay licitación."),
    ("clave", "229", "Pregunta de examen: quién declara la contratación centralizada y quién contrata."),
    # Obras es lo más preguntado de su título, pero marcar los arts. 231 a 246 enteros atrapaba 121 preguntas:
    # se marcan solo los recuadros de «Pregunta de examen» de obras.
    ("clave", "234", "Pregunta de examen: proyecto y obra adjudicados juntos siguen siendo un solo contrato de obras."),
    ("clave", "237", "Pregunta de examen: la ejecución empieza con el acta de comprobación del replanteo."),
    ("clave", "238", "Pregunta de examen: en obras manda el director facultativo."),
    ("clave", "240.1", "Pregunta de examen: certificaciones mensuales, en los diez primeros días."),
    ("clave", "242.2", "Pregunta de examen: quién fija los precios nuevos."),
    ("clave", "243", "Pregunta de examen: certificación final en 3 meses y garantía de al menos 1 año."),
    ("clave", "244", "Pregunta de examen: vicios ocultos, 15 años desde la recepción."),
    ("clave", "285", "Pregunta de examen: el estudio de viabilidad solo vincula si concluye que es inviable."),
    ("clave", "289.2", "Pregunta de examen: la tarifa es una prestación patrimonial de carácter público no tributario."),
    ("clave", "299", "Pregunta de examen: un suministro de fabricación con normas de obras."),
    ("clave", "301.2", "Pregunta de examen: con precios unitarios se puede ampliar hasta el 10 %."),
    ("clave", "304-305", "Pregunta de examen: los gastos de entrega y transporte son del contratista."),
    ("clave", "308.2", "Pregunta de examen: el contrato de servicios no sirve para contratar personal."),
    ("clave", "323", "Pregunta de examen: ministros y secretarios de Estado son órganos de contratación."),
    ("clave", "324.1, 324.5", "Pregunta de examen: cuándo hace falta la autorización del Consejo de Ministros."),
    ("clave", "327", "Pregunta de examen: al menos un tercio de la mesa especial, personas cualificadas."),
    ("clave", "335", "No se ha preguntado en el Estado, pero es habitual en otras Administraciones y muy fácil de hacer."),

    # ---------- Poco preguntado: el profesor dice que casi no cae ----------
    ("poco", "177-182", "Según el profesor, la AGE no ha usado nunca la asociación para la innovación y no es pregunta habitual."),
    ("poco", "218-230", "Según el profesor, este capítulo se pregunta bastante menos que los anteriores."),
    ("poco", "324.4", "El umbral de 900.000 € para la autorización de ministros: según el profesor, nunca se ha preguntado."),
]


def _specs(texto):
    """'122.1, 124' -> [('122', '1'), ('124', '')]; '231-246' -> un spec por artículo."""
    res = []
    for parte in texto.split(","):
        parte = parte.strip()
        m = re.fullmatch(r"(\d+)-(\d+)", parte)
        if m:
            res += [(str(a), "") for a in range(int(m.group(1)), int(m.group(2)) + 1)]
        elif parte == "DA12":
            res.append(("DA12", ""))
        else:
            art, _, ap = parte.partition(".")
            res.append((art, ap))
    return res


def citas(precepto):
    """Artículos y apartados que cita un precepto: 'arts. 145.4.b y 146' -> {('145','4.b'), ('146','')}."""
    res = set()
    if re.search(r"adicional\s+duod[eé]cima|\bD\.?\s?A\.?\s*12", precepto, re.I):
        res.add(("DA12", ""))
    for m in re.finditer(r"\barts?\b\.?\s*(.*)", precepto, re.I):
        resto = re.split(r"\sde\s(?!la LCSP)|[);]|\bLey\b|\bRD\b|\bReal\b|\bLGS\b", m.group(1))[0]
        for n in re.finditer(r"(\d+)((?:\.[\w]+)*)(?:\s*(?:a|-)\s*(\d+)(?:\.[\w]+)*)?", resto):
            a = int(n.group(1))
            if n.group(3) and not n.group(2):
                b = int(n.group(3))
                if b - a <= 40:
                    res.update((str(x), "") for x in range(a, b + 1))
                continue
            res.add((str(a), n.group(2).lstrip(".")))
    return res


def _toca(cita, spec):
    art, ap = cita
    s_art, s_ap = spec
    if art != s_art:
        return False
    return not s_ap or ap == s_ap or ap.startswith(s_ap + ".")


def marca(p):
    """Devuelve {'nivel': ..., 'nota': ...} o None."""
    if not p.get("bloque", "").startswith("lcsp-"):
        return None
    cs = citas(p.get("precepto") or "")
    mejor = None
    for nivel, arts, nota in MARCAS:
        if any(_toca(c, s) for c in cs for s in _specs(arts)):
            if not mejor or NIVELES[nivel] > NIVELES[mejor[0]]:
                mejor = (nivel, nota)
    return {"nivel": mejor[0], "nota": mejor[1]} if mejor else None
