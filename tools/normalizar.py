#!/usr/bin/env python3
"""Limpia el JSON de origen y deja las preguntas con un id estable.
Uso: python3 tools/normalizar.py [ley-contratos-todo.json] [tools/preguntas.json]"""
import json, os, re, sys

ABBR = {"autoevaluacion": "au", "oficiales": "of", "votaciones": "vo", "practicas": "pr"}
# Casos con enunciado largo común: los supuestos de Bloque III y el supuesto mixto.
CASOS = re.compile(r"^(Bloque III\.- Supuesto|Ley 39 \+ Contratos - Supuesto práctico)")
# Ejercicios de clase: si todas sus preguntas comparten un enunciado de partida, van al modo Supuestos como casos cortos.
EJERCICIO = re.compile(r"^Ejercicio \d+")
MIN_CASO = 40  # caracteres mínimos del enunciado común para que un ejercicio sea un caso
ERRATAS = {}


def limpio(t):
    return re.sub(r"[ \t]+", " ", t.replace("\xa0", " ")).strip()


def sin_duplicar(e):
    """272 enunciados traen 'texto corrido\\ntexto con párrafos': nos quedamos con el segundo."""
    if "\n" not in e:
        return limpio(e)
    a, b = e.split("\n", 1)
    if re.sub(r"\W+", "", a) == re.sub(r"\W+", "", b):
        return "\n".join(limpio(x) for x in b.split("\n") if x.strip())
    return "\n".join(limpio(x) for x in e.split("\n") if x.strip())


def separar_caso(stems):
    """Caso = prefijo común, cortado en el último salto de línea o final de frase."""
    p = os.path.commonprefix(stems)
    if len(stems) > 1 and not all(s == p for s in stems):
        corte = max(p.rfind("\n"), p.rfind(": "), p.rfind(". "))
        p = p[: corte + 1] if corte > 0 else ""
    return p.strip(), [s[len(p):].strip() if p else s for s in stems]


def main(origen, destino):
    d = json.load(open(origen, encoding="utf8"))
    preguntas, casos = [], {}
    for grupo, tests in d.items():
        if grupo == "calendarios":
            continue
        for it, t in enumerate(tests, 1):
            stems = [sin_duplicar(q["enunciado"]) for q in t["preguntas"]]
            for prefijo, cambios in ERRATAS.items():
                if t["test"].startswith(prefijo):
                    for mal, bien in cambios:
                        stems = [st.replace(mal, bien) for st in stems]
            cid = None
            if grupo == "practicas" and (CASOS.match(t["test"]) or EJERCICIO.match(t["test"])):
                texto, resto = separar_caso(stems)
                if CASOS.match(t["test"]) or len(texto) >= MIN_CASO:
                    stems = resto
                    cid = f"caso-{it:02d}"
                    casos[cid] = {"id": cid, "titulo": t["test"], "texto": texto}
                    if EJERCICIO.match(t["test"]):
                        casos[cid]["corto"] = True
            for q, st in zip(t["preguntas"], stems):
                r = {"id": f"{ABBR[grupo]}-{it:02d}-{q['n']:03d}", "origen": grupo, "test": t["test"], "n": q["n"],
                     "enunciado": st, "opciones": [limpio(o) for o in q["opciones"]]}
                if cid:
                    r["caso"] = cid
                if q.get("calendario"):
                    r["calendario"] = q["calendario"]
                if re.search(r"pregunta anterior", st, re.I):
                    r["sigueA"] = f"{ABBR[grupo]}-{it:02d}-{q['n']-1:03d}"
                preguntas.append(r)
    json.dump({"calendarios": d["calendarios"], "casos": casos, "preguntas": preguntas},
              open(destino, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(len(preguntas), "preguntas,", len(casos), "casos,", sum("caso" in p for p in preguntas), "en casos")


main(*(sys.argv[1:3] or ["ley-contratos-todo.json", "tools/preguntas.json"]))
