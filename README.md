# Test de oposición C1 AGE: contratos y subvenciones

Exámenes tipo test con todas las respuestas explicadas. Tres acordeones: Contratos (Ley 9/2017, LCSP), Subvenciones (Ley 38/2003) y Supuestos mixtos (casos que mezclan Ley 39, contratos y otras leyes; solo en Supuestos).

Se publica tal cual en GitHub Pages: no necesita compilar nada. Solo hay que subir `index.html`, `css`, `js` y `data`.

## Añadir o actualizar preguntas

1. `tools/normalizar.py` limpia `ley-contratos-todo.json` y crea `tools/preguntas.json`.
2. Las respuestas razonadas van en `tools/respuestas/*.json`, por id de pregunta (método en `tools/trabajo/INSTRUCCIONES.md`).
3. `python3 tools/construir.py` valida y genera `data/contratos.js`, `data/subvenciones.js` y `data/mixtos.js`. Un supuesto que mezcla leyes se añade a `MIXTOS` en `construir.py`. Solo entran las preguntas con respuesta.

## Estadísticas

Cada tema y bloque muestra preguntas dominadas, falladas y pendientes. Se puede repasar solo lo fallado y reiniciar las estadísticas. Todo se guarda en el navegador con claves `contratos-*`, para no mezclarse con otros tests publicados en el mismo dominio.

## Cuestionarios de clase en Supuestos

Los "Ejercicio N" sin enunciado y los "Examen nº N" de clase salen en Examen y también en Supuestos. Se elige cuáles en `como_supuesto()` de `tools/construir.py`. Sus preguntas son las mismas, así que las estadísticas se comparten.

## Consultar apuntes

La pantalla principal tiene tres pestañas: Examen, Supuestos y Apuntes. En Apuntes están todos los esquemas ordenados por bloques del temario, con un buscador por tema o por artículo (por ejemplo 149 o plazos). Al abrir uno, la ventana permite pasar al siguiente de su bloque o de la búsqueda. El orden sale de `BLOQUES` en `tools/esquemas.py`.

En la justificación de cada pregunta de contratos puede aparecer el botón "Consultar apuntes". Abre los esquemas del tema en una ventana con zoom y arrastre (rueda y ratón en escritorio, pellizco y un dedo en móvil). En móvil de pie, la ventana se gira para ver el esquema apaisado a pantalla completa.

Los esquemas salen de dos sitios: los PDF de la carpeta `ordenado` (57) y los dibujos de `LCSP_apuntes_fuente.html` (44 que no tienen PDF). Se regeneran con:

```
python3 -I tools/esquemas.py /ruta/a/ordenado
```

Hace falta PyMuPDF y Pillow, y Google Chrome instalado para pintar los dibujos. El script guarda las imágenes en `img/esquemas/` y escribe `data/esquemas.js`. Cada esquema declara en `tools/esquemas.py` qué artículos de la LCSP cubre, y cada pregunta recibe los esquemas que cubren los artículos de su precepto (hasta 4, primero los más concretos). Para los esquemas generales (plazos, eje cronológico) hay unas reglas por contenido al principio del script.

Para añadir un esquema nuevo: ponlo en la carpeta, añade una línea a la lista `ARTICULOS` (o a `HTML`) y vuelve a ejecutar el script. Sube el número `?v=` en `index.html` para que el móvil no use la versión antigua guardada.

## Esquemas rediseñados (tools/nuevos)

Los 44 esquemas que venían del HTML de apuntes están rehechos en el estilo de los PDF de `ordenado`
(hoja A4 apaisada, color con significado, título serif). Se generan con:

```bash
python3 tools/nuevos/generar.py          # todas las hojas, a PNG con Chrome
python3 tools/nuevos/generar.py h24 h41  # solo algunas
python3 tools/esquemas.py <carpeta ordenado>   # los pasa a WebP y regenera data/esquemas.js
```

`tools/esquemas.py` usa `tools/nuevos/<id>.png` en lugar del dibujo antiguo si existe. Para cambiar un esquema,
se edita su bloque en `tools/nuevos/generar.py` (los estilos comunes están en `tools/nuevos/base.css`).
