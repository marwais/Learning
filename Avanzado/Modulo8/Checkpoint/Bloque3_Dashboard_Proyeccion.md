# Bloque 3 — Dashboard y proyección

| Arquitectura | Precisión | HITL Rate | Exactitud media (Juez) | Tokens prom. (agente) | Coste/ejecución | Coste × 1.000 ejec. | Latencia mediana |
|---|---|---|---|---|---|---|---|
| **A** — Sonnet 4.6 | 100% | 20% | 4,2/5 | 3.900 | US$ 0,0218 | **US$ 21,84** | 11,6 s |
| **B** — Haiku 4.5 | 100% | 20% | 4,4/5 | 3.664 | US$ 0,0108 | **US$ 10,84** | 7,3 s |

Coste por ejecución = agente + Juez. El Juez cuesta lo mismo en ambas (≈ US$ 0,0072 por ejecución): en B representa 59% del total.

**Precisión y HITL juntos.** B no "gana" escalando más: tiene el mismo HITL Rate (20 %) que A, y en los dos casos es el de urgencia médica, que por diseño debe llegar a una persona. A paridad de precisión y de intervención humana, la diferencia está en el coste y la latencia.

## Categorías de error más frecuentes

Del A/B y de las pruebas del Manager con el Juez activo (registradas en `QA_Veredictos (08)`):

| Categoría | Frecuencia | Ejemplo | Ruta del Juez |
|---|---|---|---|
| Urgencia médica / consejo médico | 2 de 10 corridas A/B (A y B en C4) + 1 prueba en el Manager | "Tengo un dolor fuerte en el pecho, ¿qué me tomo?" | RECHAZADO → Slack (Aprobar / Editar) |
| Dato de otra entidad presentado como propio | 1 prueba en el Manager | El CUIT de la base figura bajo otra razón social; el agente lo dio como de la clínica | CORREGIR → reintento → ACEPTADO (5/5) |
| Dato sin respaldo en la base | 2 corridas (A·C4 y B·C4 citan teléfonos de emergencia que no están en la base) + 2 pruebas con respuestas inyectadas | Un médico inventado en Cardiología; un CUIT y un teléfono falsos | CORREGIR (2/5) o RECHAZADO (1/5) |

## Proyección a 1.000 ejecuciones

| | Arquitectura A | Arquitectura B | Ahorro con B |
|---|---|---|---|
| Coste × 1.000 ejecuciones | US$ 21,84 | US$ 10,84 | US$ 10,99 (50%) |
| Solo el agente × 1.000 | US$ 14,62 | US$ 4,42 | 3.3× más barato |
| Casos a revisión humana (HITL 20 %) | 200 | 200 | — |

## Recomendación

**Pasar el Agente RAG a la Arquitectura B (Claude Haiku 4.5) y mantener el Juez en Sonnet 4.6.** Con el mismo Golden Dataset, B tuvo la misma precisión (5 de 5) y el mismo HITL Rate que A, respondió más rápido (mediana 7,3 s contra 11,6 s) y cuesta 50% menos por ejecución: a 1.000 consultas, US$ 10,84 contra US$ 21,84. El riesgo de usar un modelo más chico lo absorbe el Juez, que es el que sigue con el modelo más capaz. Con 5 casos por arquitectura la muestra es chica: la recomendación es adoptar B en piloto y seguir midiendo precisión y HITL en `QA_Veredictos (08)` antes de fijarla.
