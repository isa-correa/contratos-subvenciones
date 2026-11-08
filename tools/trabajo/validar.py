#!/usr/bin/env python3
"""Uso: validar.py <NN>. Comprueba tools/respuestas/lote-NN.json contra el lote de entrada."""
import json,re,sys,os
S=os.path.dirname(os.path.abspath(__file__))
n=sys.argv[1].zfill(2)
L=json.load(open(f'{S}/lotes/lote-{n}.json',encoding='utf8'))
try: R=json.load(open(f'{S}/../respuestas/lote-{n}.json',encoding='utf8'))
except Exception as e: sys.exit(f'JSON no válido: {e}')
B={'lcsp-general','lcsp-disposiciones','lcsp-preparacion','lcsp-adjudicacion','lcsp-ejecucion','lcsp-tipos','lcsp-otros','subv-general','subv-concesion','subv-reintegro','subv-sanciones','fuera'}
err=[]
ids={q['id']:q for q in L['preguntas']}
for i in ids:
    if i not in R: err.append(f'{i}: falta')
for i,r in R.items():
    if i not in ids: err.append(f'{i}: id que no es de este lote'); continue
    q=ids[i]
    if r.get('bloque')=='fuera':
        if not isinstance(r.get('motivo'),str): err.append(f'{i}: bloque fuera necesita motivo')
        continue
    for k in ('bloque','precepto','correcta','justificaciones'):
        if k not in r: err.append(f'{i}: falta {k}')
    if err and err[-1].startswith(i): continue
    if r['bloque'] not in B: err.append(f'{i}: bloque {r["bloque"]}')
    if not isinstance(r['correcta'],int) or not 0<=r['correcta']<len(q['opciones']): err.append(f'{i}: correcta')
    if 'correctas' in r:
        c=r['correctas']
        if not (isinstance(c,list) and len(c)>=2 and c==sorted(set(c)) and all(isinstance(k,int) and 0<=k<len(q['opciones']) for k in c) and r['correcta']==c[0]): err.append(f'{i}: correctas no válidas')
    if len(r['justificaciones'])!=len(q['opciones']): err.append(f'{i}: {len(r["justificaciones"])} justificaciones, {len(q["opciones"])} opciones')
    if re.search('[—–]',json.dumps(r,ensure_ascii=False)): err.append(f'{i}: raya o semirraya')
    if 'revisar' in r and not isinstance(r['revisar'],str): err.append(f'{i}: revisar debe ser texto')
    for j,t in enumerate(r['justificaciones']):
        if len(t)<25: err.append(f'{i}: justificación {j} demasiado corta')
print('\n'.join(err) if err else f'OK lote {n}: {len(R)} respuestas')
