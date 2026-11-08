#!/usr/bin/env python3
"""Convierte LCSP_apuntes_fuente.html en apuntes.txt, con una cabecera '=== Art. N ===' por artículo.
Uso: python3 tools/trabajo/apuntes2txt.py"""
import re, html, os
R = os.path.dirname(os.path.abspath(__file__)) + "/../.."
s = open(R + "/LCSP_apuntes_fuente.html", encoding="utf8").read()
b = s[s.find("<body"):]
b = re.sub(r"(?is)<(script|style).*?</\1>|<!--.*?-->", "", b)
# la tabla de contenidos no aporta
b = re.sub(r'(?is)<nav.*?</nav>|<ul class="toc.*?</ul>', "", b)
def limpia(h):
    h = re.sub(r"(?i)</t[hd]>", " | ", h)
    h = re.sub(r"(?i)</(p|h\d|div|li|tr|table|ul|ol)>|<br\s*/?>", "\n", h)
    h = html.unescape(re.sub(r"<[^>]+>", "", h))
    h = re.sub(r"[ \t]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n", h).strip()
partes = re.split(r'(?=<h1 class="articulo")', b)
out = [limpia(partes[0])]
for p in partes[1:]:
    m = re.match(r'<h1 class="articulo"[^>]*><span class="num">(.*?)</span>(.*?)</h1>', p, re.S)
    out.append("\n=== %s ===\n%s\n%s" % (limpia(m.group(1)), limpia(m.group(2)), limpia(p[m.end():])))
t = "\n".join(out)
open(os.path.dirname(os.path.abspath(__file__)) + "/apuntes.txt", "w", encoding="utf8").write(t)
print(len(t), "caracteres,", len(re.findall(r"(?m)^=== ", t)), "artículos")
