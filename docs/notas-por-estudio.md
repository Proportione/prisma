# Una nota por estudio para leer en Obsidian

`prisma extract` y `prisma quality` dejan dos tablas. Para la lectura cualitativa (anotar cada estudio mientras escribes la síntesis) es más cómodo tener una nota Markdown por estudio, con los datos en el frontmatter y espacio debajo para tus notas. Esta receta las genera con [knap](https://github.com/obsidianmd/knap) y las abre en [Obsidian](https://obsidian.md) con una vista de Bases que filtra por nivel MMAT.

Nada de esto es parte del toolkit: no hace falta instalar nada más en Python y Obsidian es opcional (las notas son Markdown normal). knap necesita Node.js 20 o posterior.

Los ficheros de esta receta están en `examples/obsidian/`:

- `estudio.knap.md`: la plantilla de cada nota.
- `estudios.base`: la vista de Bases, con una pestaña por nivel MMAT.

## 1. Unir las dos tablas

knap genera una nota por registro de un único fichero de datos, así que primero se juntan `extracted.csv` y `mmat.csv` por la columna `pdf`. Desde tu carpeta de trabajo:

```bash
python - <<'EOF'
import csv, json
with open("data/mmat.csv", encoding="utf-8") as f:
    mmat = {r["pdf"]: {**r, "total": float(r["total"])} for r in csv.DictReader(f)}
estudios = []
with open("data/extracted.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        pdf = r.pop("pdf")
        estudios.append({"pdf": pdf, "mmat": mmat.get(pdf, {}), "campos": r})
with open("data/estudios.json", "w", encoding="utf-8") as f:
    json.dump(estudios, f, ensure_ascii=False)
EOF
```

Cada estudio queda con su nombre de PDF, su evaluación MMAT y los campos de tu taxonomía. Un PDF que no esté en `mmat.csv` sale igualmente, con el nivel vacío.

## 2. Generar las notas

```bash
npx knap@0.6.0 batch examples/obsidian/estudio.knap.md \
  --data data/estudios.json \
  --output-dir boveda/estudios \
  --filename '{{ pdf | replace:".pdf":"" | safe_name }}.md'
cp examples/obsidian/estudios.base boveda/
```

Sale una nota por fila de `extracted.csv`. La plantilla recorre los campos de la taxonomía que haya, sea cual sea: no hay que adaptarla a cada revisión. Los campos con varios valores (separados por `; ` en el CSV) pasan a ser listas. Así queda el frontmatter de una nota:

```yaml
pdf: "10_1002_tl_20626.pdf"
mmat_nivel: "Medium"
mmat_total: 3
ai_stance:
  - "permit/integrate"
study_design:
  - "qualitative"
  - "conceptual/framework"
  - "review"
longitudinal: []
```

Debajo van la tabla con los cinco criterios MMAT y una sección «Notas de lectura» vacía para ti. Si vuelves a lanzar la orden con las notas ya creadas, knap se para con un error en lugar de escribir encima. Con `--overwrite` las regenera, pero se pierde lo que hayas escrito en ellas.

## 3. Abrir la carpeta en Obsidian

En Obsidian, «Abrir carpeta como bóveda» y elige `boveda/`. Abre `estudios.base`: la pestaña «Todos» lista los estudios y las pestañas «MMAT High», «MMAT Medium» y «MMAT Low» los filtran por nivel. Encima de la tabla aparece el recuento («35 resultados»), que tiene que coincidir con el de `mmat.csv`. Desde «Filtrar» puedes añadir filtros por cualquier campo de la taxonomía.

No guardes los PDF dentro de la bóveda si tienen licencia restringida, y no la publiques: las notas pueden incluir datos de artículos que no son tuyos.
