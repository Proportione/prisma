---
{{ pdf | yaml_property:"pdf" }}
{{ mmat.level | yaml_property:"mmat_nivel" }}
{{ mmat.total | yaml_property:"mmat_total" }}
{% for campo in campos | object:"keys" %}
{{ campos[campo] | split:"; " | compact | yaml_property:campo }}
{% endfor %}
---
# {{ pdf }}

## Calidad (MMAT 2018)

Nivel: {{ mmat.level ?? "sin evaluar" }} · Puntuación: {{ mmat.total ?? "-" }}

| Criterio | Respuesta |
| --- | --- |
| Q1 | {{ mmat.Q1 }} |
| Q2 | {{ mmat.Q2 }} |
| Q3 | {{ mmat.Q3 }} |
| Q4 | {{ mmat.Q4 }} |
| Q5 | {{ mmat.Q5 }} |

## Notas de lectura

