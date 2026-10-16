# 4. Justificación financiera

Pregunta del comité: *¿esto realmente ahorra plata o es un gasto nuevo?* La respuesta compara el **costo real de operar el sistema**, medido en las pruebas, contra el **costo de la labor humana que libera**, proyectado sobre el baseline. Cada cifra va rotulada como **medida** o **proyectada**. El cálculo completo y reproducible está en `evaluacion/finanzas_m11.json`, generado por `scripts/finanzas_m11.py`.

## 4.1 Baseline: el costo del proceso manual (proyección, supuestos declarados)

| Tarea | Volumen por mes | Minutos por gestión | Horas por mes | Autonomía esperada | Horas evitadas | Ahorro mensual |
|---|---:|---:|---:|---:|---:|---:|
| Sacar un turno nuevo | 1.540 | 4,0 | 102,7 | 80 % | 82,1 | $ 821.333 |
| Modificar o cancelar un turno | 836 | 3,0 | 41,8 | 70 % | 29,3 | $ 292.600 |
| Consulta informativa | 1.584 | 2,5 | 66,0 | 70 % | 46,2 | $ 462.000 |
| Confirmación o recordatorio | 1.540 | 1,0 | 25,7 | 100 % | 25,7 | $ 256.667 |
| **Total** | | | **236,2** | | **183,3** | **$ 1.832.600** |

*Supuestos (Módulo 9): 22 días hábiles, hora administrativa a $ 10.000, tipo de cambio US$ 1 = $ 1.400. La autonomía esperada es una meta del piloto, no un resultado validado. En la batería de prueba, armada con más casos difíciles que los habituales, 11 de 15 pedidos se resolvieron sin intervención humana (73 %), en línea con el 70,6 % medido en el Módulo 9.*

## 4.2 El costo en inteligencia artificial: fórmula y valores medidos

Los proveedores de IA cobran por *tokens*: fragmentos de texto de unas tres cuartas partes de una palabra, que se cuentan al entrar (lo que lee el modelo) y al salir (lo que escribe).

**Fórmula** (precios de Anthropic en US$ por millón de tokens: Claude Haiku 4.5 = 1 de entrada / 5 de salida; Claude Sonnet 4.6 = 3 / 15):

> costo de una llamada = (tokens de entrada × precio de entrada + tokens de salida × precio de salida) / 1.000.000
>
> costo de un pedido = suma de sus llamadas (coordinador + agente o especialistas + Juez)

**Dos pedidos reales**, con los tokens que registró n8n en la ejecución:

| Pedido (`traceId`) | Modelos de trabajo (Haiku 4.5) | Juez (Sonnet 4.6) | Costo del pedido |
|---|---|---|---|
| Consulta informal, `trc-20261016024638-826-3ei7` | (6.245 × 1 + 314 × 5) / 10⁶ = US$ 0,007815 | (2.994 × 3 + 54 × 15) / 10⁶ = US$ 0,009792 | **US$ 0,017607** |
| Alta de turno, `trc-20261016024716-839-3wx4` | (986 × 1 + 124 × 5) / 10⁶ = US$ 0,001606 | (2.055 × 3 + 54 × 15) / 10⁶ = US$ 0,006975 | **US$ 0,008581** |

**Costo medido por tipo de pedido** (promedios de la batería, sin redondear):

| Tipo de pedido | Todo Sonnet 4.6 (corrida A) | **Configuración elegida** (corrida C) | Cada 1.000 pedidos (C) |
|---|---:|---:|---:|
| Consulta informativa (agente + Juez) | US$ 0,034994 | **US$ 0,016546** | US$ 16,55 |
| Alta o cambio de turno (coordinador + Juez de acciones) | US$ 0,011714 | **US$ 0,009194** | US$ 9,19 |
| Mensaje complementario (datos faltantes, consulta de turnos, turno existente) | US$ 0,004595 | **US$ 0,002003** | US$ 2,00 |
| Caso rojo o duplicado | US$ 0 | **US$ 0** | US$ 0 |

## 4.3 Optimización con modelos económicos

La consigna pide optimizar el costo con modelos económicos. Se probaron tres configuraciones con los mismos 16 casos:

| Configuración | Casos correctos | Costo promedio por pedido | Proceso en segundo plano |
|---|---|---:|---:|
| A · Todo Sonnet 4.6 | 16 / 16 | US$ 0,0131 | 8,6 s |
| B · Coordinador en Haiku 4.5 | 16 / 16 | US$ 0,0112 | 9,0 s |
| **C · Coordinador y agente de consultas en Haiku 4.5; Juez en Sonnet 4.6** | **16 / 16** | **US$ 0,0068** | **7,5 s** |

**Decisión: la configuración C.** El modelo económico hace el trabajo y el modelo fuerte lo audita. Con la misma tasa de acierto, la consulta informativa cuesta **la mitad** y el pedido promedio, **48 % menos**. La memoria se resume con Haiku 4.5 desde el Módulo 9. Además, el Juez revisa ahora también las acciones (es nuevo en el M11), y aun así el gasto mensual en IA baja respecto del Módulo 9 (US$ 68,90).

## 4.4 Costo total de operación contra labor evitada (proyección mensual)

**Tokens por mes** = consultas × costo por consulta × (1 + 15 % de reintentos del Juez) + gestiones × (acción + 1 mensaje complementario) + resúmenes de memoria
= 1.584 × 0,016546 × 1,15 + 2.376 × (0,009194 + 0,002003) + 3,17 = 30,139 + 26,604 + 3,17 = **US$ 59,91**

| Componente | US$ por mes |
|---|---:|
| Inteligencia artificial (Claude: coordinador, agente, Juez, resúmenes) | 59,91 |
| Transcripción de notas de voz (Whisper, 10 % de los pedidos por voz) | 1,90 |
| Respuestas por voz (ElevenLabs, plan Creator) | 22,00 |
| Búsquedas en la biblioteca (embeddings de Cohere) | 0,10 |
| Servidor para n8n (VPS de 2 vCPU y 4 GB; supuesto) | 24,00 |
| Memoria (Airtable Team; hoy en plan gratuito) | 20,00 |
| Base de conocimiento (Qdrant Cloud, plan gratuito), Gmail, Sheets, Slack, HubSpot CRM, Telegram, túnel | 0,00 |
| **Total servicios** | **127,91** (≈ $ 179.079) |

| Por mes | Conservador (60 % de autonomía) | **Base (78 %)** | Optimista (90 %) |
|---|---:|---:|---:|
| Horas liberadas | 141,0 | **183,3** | 211,5 |
| Beneficio (horas × $ 10.000) | $ 1.409.692 | **$ 1.832.600** | $ 2.114.538 |
| Costo total (servicios + 8 h de mantenimiento técnico, $ 160.000) | $ 339.079 | **$ 339.079** | $ 339.079 |
| **Beneficio neto** | $ 1.070.614 | **$ 1.493.521** | $ 1.775.460 |
| **Retorno** (neto sobre costo) | 3,16 veces | **4,40 veces** | 5,24 veces |
| **Recupero de la implementación** ($ 1.600.000, 80 h técnicas) | 1,49 meses | **1,07 meses** | 0,90 meses |

**Lectura para el comité:** con supuestos conservadores, el sistema cuesta menos de una cuarta parte de lo que libera y se paga en un mes y medio. Las horas liberadas no son despidos: son **capacidad** para absorber los picos, atender fuera de horario y dedicar al equipo a los casos que necesitan criterio humano.

## 4.5 Riesgos de costo y de mantenimiento

| Riesgo | Cómo se gestiona |
|---|---|
| **Saldo prepago de la API de IA agotado.** Ocurrió en las pruebas: el sistema lo alertó en castellano y lo que no depende de la IA siguió funcionando | Recarga automática con tope de gasto mensual y alerta de saldo bajo (en producción) |
| **Picos de reintentos del Juez** ("fat loop") | Tope de 2 correcciones por respuesta; el peor caso medido en el Módulo 9 fue de US$ 0,07 por consulta |
| **Cambios de los proveedores**: HubSpot avisó que la API que usa el nodo de n8n deja de estar disponible después de septiembre de 2027 | Lo cubre el mantenimiento mensual (8 h), que incluye adaptarse a los cambios de los proveedores |
| **Supuestos del baseline** | La auditoría del proceso en el primer mes reemplaza los supuestos por datos medidos |
