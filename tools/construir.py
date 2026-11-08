import re
#!/usr/bin/env python3
"""Une preguntas y respuestas razonadas en data/contratos.js.
Solo entran las preguntas con respuesta. Si algo no cuadra, avisa y para.
Uso (desde la raíz del proyecto): python3 tools/construir.py"""
import glob, json, re, sys
D = json.load(open("tools/preguntas.json", encoding="utf8"))
R = {}
for f in sorted(glob.glob("tools/respuestas/*.json")):
    R.update(json.load(open(f, encoding="utf8")))
BLOQUES = [("lcsp-general", "Contratos: objeto, ámbito y tipos (LCSP, arts. 1 a 27)"),
           ("lcsp-disposiciones", "Contratos: disposiciones generales, invalidez y recurso especial (LCSP, arts. 28 a 60)"),
           ("lcsp-preparacion", "Contratos: partes, objeto, precio y garantías (LCSP, arts. 61 a 130)"),
           ("lcsp-adjudicacion", "Contratos: adjudicación y procedimientos (LCSP, arts. 131 a 187)"),
           ("lcsp-ejecucion", "Contratos: efectos, ejecución y extinción (LCSP, arts. 188 a 230)"),
           ("lcsp-tipos", "Contratos: obras, concesiones, suministros y servicios (LCSP, arts. 231 a 315)"),
           ("lcsp-otros", "Contratos: organización administrativa (LCSP, arts. 316 a 347)"),
           ("subv-general", "Subvenciones: disposiciones generales y beneficiarios (LGS, arts. 1 a 21)"),
           ("subv-concesion", "Subvenciones: concesión y gestión (LGS, arts. 22 a 35)"),
           ("subv-reintegro", "Subvenciones: reintegro y control financiero (LGS, arts. 36 a 51)"),
           ("subv-sanciones", "Subvenciones: infracciones y sanciones (LGS, arts. 52 a 69)")]
validos = {b for b, _ in BLOQUES}
norm = lambda x: re.sub(r"\W+", "", x.lower())
clave = lambda p: norm(p["enunciado"]) + "|" + "|".join(sorted(map(norm, p["opciones"])))
ids = {p["id"] for p in D["preguntas"]}
err, fuera = [], set()
# Una pregunta repetida en otro test hereda la respuesta de la primera que se respondió.
primera = {}
for p in D["preguntas"]:
    if p["id"] in R:
        primera.setdefault(clave(p), p["id"])
for p in D["preguntas"]:
    if p["id"] not in R and clave(p) in primera:
        R[p["id"]] = R[primera[clave(p)]]
salida = []
for p in D["preguntas"]:
    r = R.get(p["id"])
    if not r:
        continue
    if r.get("bloque") == "fuera":  # no es de contratos ni de subvenciones
        fuera.add(p["id"])
        continue
    if len(r["justificaciones"]) != len(p["opciones"]):
        err.append(f"{p['id']}: {len(r['justificaciones'])} justificaciones para {len(p['opciones'])} opciones")
    if not 0 <= r["correcta"] < len(p["opciones"]):
        err.append(f"{p['id']}: correcta fuera de rango")
    if "correctas" in r:  # respuesta múltiple: solo se usa en supuestos concretos
        c = r["correctas"]
        if not (isinstance(c, list) and len(c) >= 2 and c == sorted(set(c)) and all(isinstance(i, int) and 0 <= i < len(p["opciones"]) for i in c) and r["correcta"] == c[0]):
            err.append(f"{p['id']}: correctas no válidas")
        if "caso" not in p:
            err.append(f"{p['id']}: la respuesta múltiple solo vale en supuestos")
    if r["bloque"] not in validos:
        err.append(f"{p['id']}: bloque {r['bloque']}")
    if re.search("[—–]", json.dumps(r, ensure_ascii=False)):
        err.append(f"{p['id']}: lleva raya o semirraya")
    salida.append({**p, **r})
grupos = {}
for p in salida:
    grupos.setdefault(clave(p), []).append(p)
for g in grupos.values():
    if len(g) > 1:
        if len({norm(p["opciones"][p["correcta"]]) for p in g}) > 1:
            err.append("respuesta distinta en la misma pregunta: " + ", ".join(p["id"] for p in g))
        for p in g:
            p["dup"] = g[0]["id"]
fantasma = set(R) - ids
if fantasma:
    err.append(f"ids desconocidos: {sorted(fantasma)}")
if err:
    sys.exit("\n".join(err))

# ---------- Formato del enunciado de los casos ----------
# El texto original viene en una sola línea. Aquí se parte en párrafos, viñetas y apartados.
ABREV = re.compile(r"(?:\b[A-ZÁÉÍÓÚ]|\bS\.L|\bS\.A|\bO\.A|\bS\.M\.E|\bA\.A\.I|\bF\.S\.P|\bE\.P\.E|\bart|\barts|\bnúm|\bSr|\bSra|\betc|\bnº)\.$")
CABECERAS = ["Servicio de calibración de equipos de medida", "Adquisición de uniformes",
             "Impresión de material educativo", "Obras de reparación de la oficina de asistencia en materia de registro"]
ARRANQUES = ("En primer lugar", "En segundo lugar", "En tercer lugar", "Además", "En relación con el supuesto",
             "En relación con la situación", "Otros contratos", "Por otro lado", "Finalmente", "Por último")

def frases(t):
    out, ini = [], 0
    for m in re.finditer(r"(?<=[.!?:;]) (?=[A-ZÁÉÍÓÚÑ¿¡«“])", t):
        if ABREV.search(t[ini:m.start()]):
            continue
        out.append(t[ini:m.start()]); ini = m.end()
    out.append(t[ini:])
    return out

def trocear(p, tope=420):
    if len(p) <= tope or p.startswith("- ") or re.match(r"[a-e]\) ", p):
        return [p]
    res, cur = [], ""
    for f in frases(p):
        if cur and len(cur) + len(f) > tope:
            res.append(cur); cur = f
        else:
            cur = (cur + " " + f).strip()
    res.append(cur)
    return res

def dar_formato(t):
    if "\n" in t:
        return t
    for c in CABECERAS:
        t = re.sub(r"(?<=\d\. )" + re.escape(c) + " ", c + "\n", t)
    t = re.sub(r" (?=Publicación \d )", "\n", t)
    t = re.sub(r"(Publicación \d) (?=[A-ZÁÉÍÓÚ])", r"\1\n", t)
    t = re.sub(r"(?<=[.:]) (?=- [A-ZÁÉÍÓÚÑ¿¡])", "\n", t)
    t = re.sub(r" (?=- [A-ZÁÉÍÓÚÑ¿¡])", "\n", t)
    t = re.sub(r"(?<=[:.;]) (?=a\) [A-ZÁÉÍÓÚ])", "\n", t)
    t = re.sub(r"(?<=[.;]) (?=[b-e]\) [A-ZÁÉÍÓÚ])", "\n", t)
    t = re.sub(r"(?<=[.:]) (?=\d\. [A-ZÁÉÍÓÚ])", "\n", t)
    t = re.sub(r"(?<=[.:]) (?=(?:" + "|".join(ARRANQUES) + r")\b)", "\n", t)
    partes = []
    for linea in t.split("\n"):
        partes += trocear(linea.strip())
    return "\n".join(x for x in partes if x)

# Un caso solo entra si todas sus preguntas (las que no son "fuera") están respondidas.
total, hechas = {}, {}
for p in D["preguntas"]:
    if "caso" in p and p["id"] not in fuera:
        total[p["caso"]] = total.get(p["caso"], 0) + 1
for p in salida:
    if "caso" in p:
        hechas[p["caso"]] = hechas.get(p["caso"], 0) + 1
casos = [c for k, c in D["casos"].items() if hechas.get(k) and hechas[k] == total.get(k)]
for c in casos:
    c["texto"] = dar_formato(c["texto"])
ok = {c["id"] for c in casos}
salida = [p for p in salida if "caso" not in p or p["caso"] in ok]
# ---------- Tres temas: contratos, subvenciones y supuestos mixtos ----------
# Examen: los bloques lcsp-* van a Contratos y los subv-* a Subvenciones.
# Supuestos: un caso va a Subvenciones si todas sus preguntas son de subvenciones, a Mixtos si mezcla leyes
# (lo marcas a mano aquí) y, si no, a Contratos.
MIXTOS = {"caso-67", "caso-69"}  # Ley 39 y Ley 40 con contratos
es_subv = lambda b: b.startswith("subv-")
bloques_caso = {}
for p in salida:
    if "caso" in p:
        bloques_caso.setdefault(p["caso"], set()).add(p["bloque"])
def destino(p):
    if "caso" in p:
        c = p["caso"]
        if c in MIXTOS:
            return "mixtos"
        return "subvenciones" if all(es_subv(b) for b in bloques_caso[c]) else "contratos"
    return "subvenciones" if es_subv(p["bloque"]) else "contratos"
dest_caso = {c["id"]: destino({"caso": c["id"]}) for c in casos}

# Cuestionarios de clase que también se practican en Supuestos. Siguen en Examen: sus preguntas no llevan "caso",
# el supuesto es solo una lista de ids. Entran los "Ejercicio N" sin enunciado y todos los "Examen nº N" de clase.
def como_supuesto(t):
    return bool(re.match(r"(Ejercicio \d+\.-|Examen nº ?\d+)", t))
por_test = {}
for p in salida:
    if "caso" not in p and p["origen"] == "practicas" and como_supuesto(p["test"]):
        por_test.setdefault(p["test"], []).append(p)
for t, ps in por_test.items():
    ps.sort(key=lambda p: p["n"])
    cid = "test-" + ps[0]["id"].split("-")[1]
    c = {"id": cid, "titulo": t, "texto": "", "corto": True, "ids": [p["id"] for p in ps]}
    casos.append(c)
    dest_caso[cid] = "subvenciones" if all(es_subv(p["bloque"]) for p in ps) else "contratos"
TEMAS = [("contratos", "Contratos del sector público (LCSP)", lambda b: not es_subv(b)),
         ("subvenciones", "Subvenciones (Ley 38/2003)", es_subv),
         ("mixtos", "Supuestos mixtos (Ley 39, contratos y otras leyes)", lambda b: True)]
total_p = 0
for id_, nombre, filtro in TEMAS:
    ps = [p for p in salida if destino(p) == id_]
    cs = [c for c in casos if dest_caso[c["id"]] == id_]
    if not ps:
        continue
    usados = {p["bloque"] for p in ps}
    # Mixtos solo se practica en Supuestos y comparte ids de bloque con Contratos: sin bloques propios, para no pisar la selección.
    bl = [] if id_ == "mixtos" else [{"id": a, "nombre": b} for a, b in BLOQUES if filtro(a) and a in usados]
    tema = {"id": id_, "nombre": nombre, "bloques": bl, "calendarios": D["calendarios"], "casos": cs, "preguntas": ps}
    with open(f"data/{id_}.js", "w", encoding="utf8") as f:
        f.write("window.BANCO = window.BANCO || [];\nwindow.BANCO.push(" + json.dumps(tema, ensure_ascii=False, separators=(",", ":")) + ");\n")
    total_p += len(ps)
    print(len(ps), "preguntas ·", len(cs), "casos → data/" + id_ + ".js")
print(total_p, "preguntas ·", len(casos), "supuestos (con los cuestionarios de clase) ·", len(fuera), "fuera de tema · de", len(D["preguntas"]))
