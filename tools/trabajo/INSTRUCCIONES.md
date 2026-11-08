# Cómo responder y justificar las preguntas

Es una app de estudio para la oposición C1 (Cuerpo General Administrativo). La usuaria estudia con estas explicaciones, así que un error enseña algo falso. Prioridad: acertar la respuesta, y luego explicarla bien.

## Material
Rutas relativas a `SCRATCH` (`tools/trabajo`).
- `lotes/lote-NN.json`: tus preguntas, con `casos` y `calendarios` si los usan. No hay plantilla oficial de respuestas: las razonas tú con la norma.
- `python3 -I SCRATCH/consulta.py apuntes 211 212`: artículos de los apuntes de la usuaria (LCSP). Fijan el enfoque y el tono: léelos primero.
- `python3 -I SCRATCH/consulta.py lcsp 211`: texto consolidado del BOE de la Ley 9/2017, para comprobar la letra.
- `python3 -I SCRATCH/consulta.py 38 12 13`: artículos de la Ley 38/2003, General de Subvenciones (BOE).
- `python3 -I SCRATCH/consulta.py buscar "texto"`: busca una expresión en los apuntes.
- Si una pregunta cita otra norma (Ley 39/2015, un reglamento), mira el BOE; si no puedes comprobarla, márcala con `revisar`.

## Método, pregunta a pregunta
1. **Lee siempre el artículo antes de decidir** (apuntes y, para la letra exacta, BOE). Nada de responder de memoria: estas preguntas cambian una palabra, un plazo o un importe para pillarte. Compara cada opción con el texto, palabra a palabra.
2. Fíjate en si pide la correcta o la **incorrecta / falsa / NO**.
3. Si la ley ha cambiado desde que se escribió la pregunta, responde con el texto vigente y dilo en `ojo`.
4. En cómputo de plazos, cuenta sobre el calendario de verdad y con las reglas de la LCSP (no las de la Ley 39/2015 salvo que el enunciado lo diga). Comprueba el día de la semana con Python (`datetime`) y enseña las fechas clave.
5. En cálculos (valor estimado, garantías, IVA, prórrogas), enseña la cuenta paso a paso en la justificación de la correcta.
6. **Si la pregunta no es de contratos ni de subvenciones** (Ley 39/2015 pura, dependencia, igualdad...), no la razones: responde `{"bloque": "fuera", "motivo": "una frase"}`.
7. Si tras leerlo no estás seguro, si dos opciones parecen válidas o si ninguna encaja, elige la más defendible y añade `revisar` con la duda en una frase. Es mucho mejor marcar una duda que colar un error. Nunca inventes un artículo ni una cita.

## Salida
Escribe con la herramienta Write un JSON en `/Users/isabel.correaurda/Downloads/plataforma-test-main/tools/respuestas/lote-NN.json`, UTF-8, un objeto cuya clave es el id de cada pregunta:
```json
{"au-01-001": {
  "bloque": "lcsp-general",
  "precepto": "Art. 3.2 de la LCSP",
  "correcta": 3,
  "justificaciones": ["...", "...", "...", "..."],
  "ojo": "opcional",
  "revisar": "opcional, solo si hay duda real"
}}
```
- `correcta`: índice desde 0 de la opción correcta, en el orden en que vienen. **No reordenes las opciones.**
- `justificaciones`: una por opción, en el mismo orden, y tantas como opciones haya.
- `bloque`, según el tema de la pregunta, no del test: `lcsp-general` (LCSP arts. 1 a 27: objeto, ámbito, tipos de contrato) · `lcsp-disposiciones` (28 a 60: disposiciones generales, invalidez, recurso especial) · `lcsp-preparacion` (61 a 130: partes, objeto, precio, garantías, preparación) · `lcsp-adjudicacion` (131 a 187: adjudicación y procedimientos) · `lcsp-ejecucion` (188 a 230: efectos, ejecución, modificación y extinción) · `lcsp-tipos` (231 a 315: obras, concesiones, suministros, servicios) · `lcsp-otros` (316 a 347: organización administrativa) · `subv-general` (LGS arts. 1 a 21) · `subv-concesion` (LGS 22 a 35) · `subv-reintegro` (LGS 36 a 51) · `subv-sanciones` (LGS 52 a 69) · `fuera`.
- `precepto`: el artículo principal, por ejemplo "Art. 3.2 de la LCSP" o "Art. 2.1 de la Ley 38/2003". Con apartado si lo tiene.
- `ojo`: solo cuando aporte algo: trampa de la pregunta, palabra cambiada, confusión típica. Una o dos frases.
- Comillas tipográficas “así” dentro de los textos, para no romper el JSON.
- Al terminar: `python3 -I SCRATCH/validar.py NN` y corrige hasta que diga OK.

## El idioma de las explicaciones
Como unos buenos apuntes de una academia, para alguien que no es jurista: frases cortas, palabras de todos los días, tuteando. Traduce la jerga cuando aparezca.
- **La correcta** empieza por "Es esta." y explica por qué, con el artículo en **negrita** y con lo que dice en palabras sencillas. Si ayuda, un ejemplo o una forma de recordarlo.
- **Las incorrectas** empiezan por "No." y dicen **qué falla exactamente en esa opción**: qué palabra o plazo te han cambiado y cuál es el bueno. Citan el artículo si es otro distinto. Nunca "No, porque no es lo que dice la ley": eso no enseña nada. Cada opción tiene su razón propia.
- **Si pide la incorrecta**: en la que hay que marcar di "Esta es la falsa, y por eso es la que hay que marcar." y explica qué falla; en las demás, "Es verdadera, así que no se marca." y por qué es verdadera.
- **Si es un supuesto o caso**: razona con los datos del enunciado (nombres, fechas, cantidades). "Como Dª Clotilde recibe la notificación el 10 de enero..."
- Si una opción es "todas son correctas" o "ninguna", explícalo en función de las otras.
- Solo se usa `**negrita**` (para el artículo o la idea clave), sin otro formato.
- Prohibido usar raya (—) o semirraya (–) como puntuación: usa coma, dos puntos, paréntesis o punto. Rangos: "de 1 a 12". El validador las rechaza.
- Nada de relleno ("cabe señalar", "es importante destacar") ni de mencionar que eres una IA. No copies textos largos del BOE: explica, y cita entre comillas solo la frase corta que importa.
- Largo orientativo: la correcta de 2 a 4 frases, cada incorrecta de 1 a 2.

## Ejemplos del tono buscado
```json
{
 "enunciado": "En relación con las fuentes del derecho, y de conformidad con lo establecido en el artículo 1 del Código Civil, señale cuál de las siguientes opciones no es correcta: (ADMVO-P.I. 2021)",
 "opciones": [
  "Carecerán de validez las disposiciones que contradigan otra del mismo rango.",
  "La costumbre solo regirá en defecto de ley aplicable, siempre que no sea contraria a la moral o al orden público, y que resulte probada.",
  "Los principios generales del derecho se aplicarán en defecto de ley o costumbre, sin perjuicio de su carácter informador del ordenamiento jurídico.",
  "Los usos jurídicos que no sean meramente interpretativos de una declaración de voluntad tendrán la consideración de costumbre."
 ],
 "vo-01-002": {
  "bloque": "fuentes",
  "precepto": "Art. 1.2 del Código Civil",
  "correcta": 0,
  "justificaciones": [
   "Esta es la falsa, y por eso es la que hay que marcar. El **art. 1.2 del Código Civil** dice que carecen de validez las disposiciones que contradigan otra de **rango superior**, no del mismo rango. Entre normas del mismo rango no se anulan: la posterior deroga a la anterior.",
   "Es verdadera, así que no se marca. Es el art. 1.3 CC: la costumbre va detrás de la ley y además tiene que ser conforme a la moral y al orden público, y probarse.",
   "Es verdadera, así que no se marca. Es el art. 1.4 CC: los principios se aplican si no hay ley ni costumbre, y además “informan” todo el ordenamiento.",
   "Es verdadera, así que no se marca. Es el párrafo segundo del art. 1.3 CC."
  ],
  "ojo": "Lee bien el enunciado: pide la que “no es correcta”. Te han cambiado “rango superior” por “mismo rango”, y eso es lo único que falla."
 }
}
```
```json
{
 "enunciado": "El 10 de enero, Dª Clotilde recibe la notificación de una resolución que pone fin a la vía administrativa. ¿Qué día finaliza el plazo para interponer recurso potestativo de reposición?\nNota: el plazo de interposición del recurso potestativo de reposición es 1 mes (art. 124 Ley 39/2015).",
 "opciones": [
  "10 de febrero.",
  "9 de febrero.",
  "11 de febrero.",
  "13 de febrero."
 ],
 "pr-05-001": {
  "bloque": "plazos",
  "precepto": "Arts. 30.4 y 124.1 de la Ley 39/2015",
  "correcta": 0,
  "justificaciones": [
   "Es esta. Los plazos por meses van **de fecha a fecha**: si te notifican un 10, el plazo acaba el 10 del mes de vencimiento (**art. 30.4**). Así que acaba el 10 de febrero, que en el calendario de 2023 es viernes, hábil.",
   "No. Es la confusión de restar un día. El plazo empieza a contar el día siguiente, pero acaba el mismo número de día que el de la notificación.",
   "No. Es la confusión de sumar un día por empezar al día siguiente. En los plazos por meses, el final es la misma fecha.",
   "No. El 13 de febrero es lunes. Solo se pasaría al siguiente hábil si el día 10 fuera inhábil (art. 30.5), y no lo es."
  ],
  "ojo": "Comparación rápida: por meses, de fecha a fecha. Por días, se cuentan uno a uno empezando el día siguiente."
 }
}
```
```json
{
 "enunciado": "Comprobado el riesgo de inundación de los terrenos, ¿qué vía tiene la Confederación Hidrográfica para dejar sin efecto la resolución de autorización de construcción de la vivienda en zona de policía de cauces otorgada a favor de Doña Clara Hevia?",
 "opciones": [
  "La declaración de oficio de la anulabilidad de la autorización.",
  "La revocación de la autorización.",
  "La rectificación de errores.",
  "La declaración de lesividad de la autorización."
 ],
 "pr-30-003": {
  "bloque": "revision",
  "precepto": "Arts. 107 y 109 de la Ley 39/2015",
  "correcta": 3,
  "justificaciones": [
   "No. La revisión de oficio es para actos **nulos** (art. 106). Un acto favorable que solo es anulable no puede anularlo la Administración por sí misma.",
   "No. La revocación es para actos de gravamen o desfavorables (art. 109.1). Esta autorización beneficia a doña Clara.",
   "No. Rectificar es para errores materiales, de hecho o aritméticos que se ven a simple vista (art. 109.2). Un error en un estudio hidrológico no es una errata.",
   "Es esta. La autorización es un acto favorable y el caso apunta a un vicio de anulabilidad por errores en el estudio. Para esos actos, la vía es declararlos lesivos y pedir la anulación a los tribunales (**art. 107**)."
  ],
  "ojo": "Si favorece al ciudadano y es anulable, la Administración no puede quitarlo sola: tiene que ir al juez."
 }
}
```
```json
{
 "enunciado": "¿Cuáles de los siguientes actos son nulos de pleno derecho?",
 "opciones": [
  "Todos los dictados por órgano incompetente.",
  "Los que se dicten como consecuencia de infracción penal.",
  "Aquellos cuyo contenido sea de dificil ejecución.",
  "Los que lesionen derechos y libertades constitucionales."
 ],
 "au-09-001": {
  "bloque": "nulidad",
  "precepto": "Art. 47.1 de la Ley 39/2015",
  "correcta": 1,
  "justificaciones": [
   "No. La palabra “todos” lo estropea: solo si es manifiestamente incompetente por materia o territorio (art. 47.1.b).",
   "Es esta. Es el **art. 47.1.d)**: los constitutivos de infracción penal o dictados como consecuencia de ella. Por ejemplo, una licencia concedida a cambio de un soborno.",
   "No. Difícil no es lo mismo que imposible. Lo que hace nulo un acto es un contenido **imposible** (art. 47.1.c).",
   "No. Se queda demasiado amplio. Solo los susceptibles de amparo constitucional (art. 47.1.a)."
  ]
 }
}
```


## Reglas de trabajo
- Responde a TODAS las preguntas del lote, con el mismo cuidado la última que la primera.
- Las preguntas con `sigueA` dependen de la anterior; las de un `caso` comparten el texto de `casos`: léelo entero antes.
- Trabaja solo con estos archivos y escribe solo tu `lote-NN.json`.
- Tu respuesta final, una sola línea: `lote NN: X respuestas, Y marcadas revisar`. Nada más.
