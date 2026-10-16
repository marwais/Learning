# Evaluación de modelos (batería de 16 casos, 15/10/2026)

| Corrida | Router | Agente RAG | Juez | Casos correctos | US$ por consulta informativa | US$ por acción | US$ promedio por pedido | Proceso en segundo plano (prom.) | Nota media del Juez (aceptados) |
|---|---|---|---|---|---|---|---|---|---|
| A | sonnet | sonnet | sonnet | 16/16 | 0.03499 | 0.01171 | 0.01310 | 8.6 s | 5.00/5 |
| B | haiku | sonnet | sonnet | 16/16 | 0.03271 | 0.00920 | 0.01115 | 9.0 s | 5.00/5 |
| C | haiku | haiku | sonnet | 16/16 | 0.01655 | 0.00919 | 0.00684 | 7.5 s | 4.83/5 |

**Decisión:** corrida C (Router y Agente RAG en Claude Haiku 4.5; Juez en Claude Sonnet 4.6). Misma tasa de acierto que A (16/16), mitad de costo por consulta informativa y menor tiempo de proceso. El modelo económico hace el trabajo y el modelo fuerte lo audita. Muestra chica (4 consultas informativas por corrida): se sigue midiendo con la revisión semanal de `QA_Veredictos (11)`.

Precios usados (US$ por millón de tokens, entrada / salida): Sonnet 4.6 = 3 / 15; Haiku 4.5 = 1 / 5. Costo por llamada = (tokens de entrada × precio de entrada + tokens de salida × precio de salida) / 1.000.000, con los tokens que registra n8n en cada ejecución (Manager + Juez).
