#!/usr/bin/env python3
"""Consulta de fuentes. Uso:
  consulta.py apuntes 211 212     artículos de los apuntes de la LCSP (los de la usuaria; fijan el tono y el enfoque)
  consulta.py lcsp 211            texto consolidado del BOE de la Ley 9/2017 (para comprobar la letra de la ley)
  consulta.py 38 12 13            artículos de la Ley 38/2003, General de Subvenciones (BOE)
  consulta.py buscar "texto"      busca una expresión en los apuntes
"""
import re, sys, os
B = os.path.dirname(os.path.abspath(__file__))
def leer(n):
    return open(B + "/" + n, encoding="utf8").read().replace("\xa0", " ")

if len(sys.argv) < 3:
    sys.exit(__doc__)
modo = sys.argv[1]

if modo == "apuntes":
    t = leer("apuntes.txt")
    cab = list(re.finditer(r"(?m)^=== (Arts?\.) (\d+)(?:\s*[-a-z ]*?(\d+))?[^=]*===$", t))
    for a in sys.argv[2:]:
        n = int(a)
        hit = [i for i, m in enumerate(cab) if int(m.group(2)) <= n <= int(m.group(3) or m.group(2))]
        if not hit:
            print("Art", a, "no está en los apuntes (usa lcsp para el BOE)"); continue
        i = hit[0]
        fin = cab[i + 1].start() if i + 1 < len(cab) else len(t)
        print(t[cab[i].start():fin].strip()[:9000]); print("=====")
    sys.exit()

if modo == "buscar":
    L = leer("apuntes.txt").split("\n")
    pat = sys.argv[2].lower()
    hits = [i for i, l in enumerate(L) if pat in l.lower()]
    last = -99
    for i in hits[:12]:
        if i - last < 6: continue
        # artículo al que pertenece la línea
        art = next((L[j] for j in range(i, -1, -1) if L[j].startswith("=== ")), "")
        print("[" + art + " | línea " + str(i) + "]", "\n".join(L[max(0, i - 1):i + 5])[:1100]); print("---"); last = i
    if not hits: print("sin resultados")
    sys.exit()

F = {"lcsp": "lcsp", "38": "lgs"}
t = leer(F[modo] + ".txt")
M = list(re.finditer(r"(?m)^\s*Art[íi]culo\s+(\d+)(?:\s+(bis|ter|quater))?\.?", t))
for a in sys.argv[2:]:
    hit = [k for k, m in enumerate(M) if m.group(1) == a]
    if not hit: print("Art", a, "no encontrado"); continue
    fin_de = lambda k: (M[k + 1].start() if k + 1 < len(M) else M[k].start() + 5000)
    # el índice del principio repite "Artículo N" sin título: nos quedamos con el del cuerpo, que sí lo lleva
    con_titulo = [k for k in hit if re.match(r"[^\n]*\.\s+\S", t[M[k].start():M[k].start() + 200])]
    k = (con_titulo or hit)[0]
    print(t[M[k].start():fin_de(k)].strip()[:7000]); print("=====")
