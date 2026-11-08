#!/usr/bin/env python3
"""Reparte las preguntas pendientes en lotes de ~25 en tools/trabajo/lotes/. Un caso nunca se parte.
Las repetidas (mismo enunciado y opciones) solo van en la primera aparición. Lo ya respondido no vuelve a salir.
Uso: python3 tools/trabajo/hacer_lotes.py [tamaño]"""
import glob, json, os, re, sys
R = os.path.dirname(os.path.abspath(__file__)) + "/.."
D = json.load(open(R + "/preguntas.json", encoding="utf8"))
tam = int(sys.argv[1]) if len(sys.argv) > 1 else 25
hechas = set()
for f in glob.glob(R + "/respuestas/*.json"):
    hechas |= set(json.load(open(f, encoding="utf8")))
usadas = set()
for f in glob.glob(R + "/trabajo/lotes/*.json"):
    usadas |= {p["id"] for p in json.load(open(f, encoding="utf8"))["preguntas"]}
norm = lambda x: re.sub(r"\W+", "", x.lower())
clave = lambda p: norm(p["enunciado"]) + "|" + "|".join(sorted(map(norm, p["opciones"])))
vistas = {}
for p in D["preguntas"]:
    vistas.setdefault(clave(p), p["id"])
# unidades: cada caso entero, o cada pregunta suelta
unidades, por_caso = [], {}
for p in D["preguntas"]:
    if p["id"] in hechas or p["id"] in usadas or vistas[clave(p)] != p["id"]:
        continue
    if "caso" in p:
        if p["caso"] not in por_caso:
            por_caso[p["caso"]] = []
            unidades.append(por_caso[p["caso"]])
        por_caso[p["caso"]].append(p)
    else:
        unidades.append([p])
n = max([0] + [int(re.search(r"(\d+)", os.path.basename(f)).group(1)) for f in glob.glob(R + "/trabajo/lotes/lote-*.json")])
lote = []
def volcar():
    global lote, n
    if not lote:
        return
    n += 1
    cs = {p["caso"] for p in lote if "caso" in p}
    cal = {p["calendario"] for p in lote if "calendario" in p}
    json.dump({"casos": {k: D["casos"][k] for k in cs}, "calendarios": {k: D["calendarios"][k] for k in cal},
               "preguntas": lote}, open(f"{R}/trabajo/lotes/lote-{n:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    lote = []
for u in unidades:
    if lote and len(lote) + len(u) > tam + 5:
        volcar()
    lote += u
    if len(lote) >= tam:
        volcar()
volcar()
print(n, "lotes en total")
