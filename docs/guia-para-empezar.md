# Guía para empezar con PRISMA

Esta guía acompaña una primera revisión sistemática de literatura con el toolkit, paso a paso. Está pensada para quien conoce el método (PRISMA 2020, criterios de inclusión, evaluación de calidad) y no programa a diario.

Lo que el toolkit hace por ti es dejar constancia de cada decisión: qué artículos entraron, cuáles salieron y por qué regla. Lo que no hace es decidir por ti. Los criterios los escribes tú, y la lectura a texto completo sigue siendo tuya.

## Antes de empezar

Necesitas tres cosas:

1. **Python 3.10 o posterior.** Para comprobarlo, abre una terminal y escribe `python3 --version`.
2. **Una terminal.** En macOS es la aplicación Terminal; en Windows, PowerShell.
3. **Una carpeta de trabajo** para la revisión, por ejemplo `mi-revision`.

Si es la primera vez que usas una terminal, un asistente de programación (Claude Code, Codex u otro) puede ejecutar estos pasos contigo y explicarte cada salida. Al final de la guía hay un texto para pedírselo.

## 1. Instalar

```bash
cd mi-revision
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install "git+https://github.com/Proportione/prisma@v0.2.0"
prisma --help
```

Si el último comando muestra la lista de órdenes (`ingest`, `screen`, `extract`, `quality`, `report`, `correlate`), la instalación ha funcionado.

El paquete todavía no está en PyPI: `pip install proportione-prisma` a secas no lo encuentra.

## 2. Reunir el corpus

```bash
prisma ingest openalex \
  --query "google trends forecasting" \
  --max 200 \
  --mailto tu-correo@universidad.es \
  --out data/openalex.ris
```

- `--query` es tu expresión de búsqueda.
- `--max` limita el número de registros.
- `--mailto` es tu correo. OpenAlex lo pide como cortesía para dar mejor servicio; no se publica.
- El resultado es un fichero RIS, que también abren Zotero, Mendeley o EndNote.

Si además tienes exportaciones de Scopus o Web of Science, guárdalas en formato RIS en la carpeta `data/`.

## 3. Quitar duplicados

```bash
prisma ingest dedup \
  -s openalex=data/openalex.ris \
  -s scopus=data/scopus.ris \
  --out data/
```

Cada `-s` es una fuente, con una etiqueta y su fichero. La orden compara por DOI y por parecido de título, y al terminar escribe cuántos registros había, cuántos son únicos y cuántos duplicados. Esas tres cifras son las primeras casillas del diagrama PRISMA: apúntalas.

El corpus sin duplicados queda en `data/corpus-deduplicated.ris`.

## 4. Cribar por título y resumen

El cribado se define en un fichero de reglas, no en el código. En `examples/screening_rules_signal_kpi.yaml` hay uno completo que puedes copiar y adaptar. Tiene dos partes:

- **Exclusión:** reglas que descartan un registro en cuanto aparecen (por ejemplo, estudios secundarios o temas ajenos).
- **Inclusión:** grupos de reglas que deben cumplirse todos a la vez (en el ejemplo: método empírico, señal digital y un indicador de negocio).

Cada regla lleva un identificador, un código y una descripción. Son los que aparecerán después junto a cada decisión.

```bash
prisma screen \
  --in data/corpus-deduplicated.ris \
  --rules mis-reglas.yaml \
  --out data/screening/
```

La orden muestra cuántos registros quedan en cada decisión y guarda en `data/screening/` el resultado registro a registro, con la regla que lo decidió. Ese registro es lo que te permite responder a un revisor que pregunte por qué un artículo entró y otro no.

Revisa una muestra a mano antes de darlo por bueno. Si una regla excluye de más, corrígela y vuelve a ejecutar: el resultado se regenera entero.

## 5. Extraer datos de los textos completos

Descarga los PDF de los artículos que pasaron el cribado y ponlos en `data/pdfs/`.

```bash
prisma extract \
  --pdfs data/pdfs/ \
  --taxonomy examples/extraction_taxonomy_signal_kpi.yaml \
  --out data/extracted.csv
```

La taxonomía es otro fichero de reglas: dice qué campos buscar en cada artículo. El resultado es una tabla CSV con una fila por PDF, que puedes abrir en Excel o en R.

## 6. Evaluar la calidad

```bash
prisma quality --pdfs data/pdfs/ --out data/mmat.csv
```

Aplica los cinco criterios de MMAT 2018 para estudios cuantitativos descriptivos y da un nivel (alto, medio o bajo) por artículo. Es una primera pasada automática a partir del texto: sirve para ordenar la revisión manual, no para sustituirla.

## 7. Dibujar el diagrama PRISMA 2020

Copia `examples/prisma_counts_demo.json`, sustituye las cifras por las tuyas y ejecuta:

```bash
prisma report --counts mis-cifras.json --out reports/prisma-flow.png
```

## Ver el proceso sin escribir órdenes

El toolkit incluye una aplicación que recorre los mismos pasos en el navegador:

```bash
pip install "proportione-prisma[streamlit] @ git+https://github.com/Proportione/prisma@v0.2.0"
streamlit run streamlit_app/Home.py
```

Para esta parte hace falta tener descargado el repositorio, porque la aplicación vive en la carpeta `streamlit_app/`.

## Si prefieres que te acompañe un asistente

Con un asistente de programación abierto en tu carpeta de trabajo, puedes empezar así:

> Quiero hacer una revisión sistemática con el toolkit PRISMA de Proportione (github.com/Proportione/prisma). Sigue la guía `docs/guia-para-empezar.md` del repositorio. Instálalo en un entorno virtual, ejecuta cada paso conmigo y explícame en una frase qué ha hecho cada orden y dónde ha dejado el resultado. Mi pregunta de investigación es: […]. No cambies mis criterios de inclusión sin preguntarme.

## Qué citar

Si el toolkit te sirve en una publicación, cita el software con el DOI general, que siempre lleva a la última versión: [10.5281/zenodo.19883808](https://doi.org/10.5281/zenodo.19883808). El fichero `CITATION.cff` del repositorio tiene la referencia completa.

El toolkit ayuda a cumplir el estándar PRISMA 2020, pero no está afiliado al PRISMA Statement Group ni a la red EQUATOR. La lista de comprobación oficial sigue siendo tu referencia.

## Dudas y errores

Abre una incidencia en [github.com/Proportione/prisma/issues](https://github.com/Proportione/prisma/issues) con la orden que ejecutaste y el mensaje que obtuviste.
