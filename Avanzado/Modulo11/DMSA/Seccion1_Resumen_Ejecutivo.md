# 1. Resumen ejecutivo

## El problema de negocio

La Clínica LoDeTincho (nombre anonimizado) recibe unas **250 gestiones por día**: sacar, cambiar, consultar y confirmar turnos, y preguntas sobre especialidades, horarios y estudios. Hoy las atienden tres administrativas de 8 a 20 h, que repiten las mismas tareas todo el día:

- **236 horas por mes** de trabajo repetitivo, equivalentes a **$ 2.360.000** mensuales (a $ 10.000 la hora).
- En los picos, **6 minutos de espera**; fuera de horario, **1 de cada 5 contactos** queda sin respuesta hasta el día siguiente.
- **5 % de los turnos** tiene datos incompletos o duplicados, y el error aparece cuando el paciente llega.

*Baseline con supuestos declarados (relevamiento del proceso de la Central de Turnos, detallado en la Sección 4.1). Se valida con la auditoría del primer mes.*

## La solución

**AgendaBot es una Central de Turnos digital que atiende las 24 horas por el canal que el paciente ya usa (Telegram, con texto o notas de voz; email; la web de turnos y el chat) y deja lo delicado en manos del equipo.** Funciona como un equipo de especialistas virtuales coordinados:

- Un **coordinador** entiende el pedido y lo deriva.
- **Especialistas** registran, cambian, confirman y consultan turnos, o responden con la biblioteca oficial de la clínica, citando la fuente o diciendo «No sé».
- Un **supervisor de calidad** (*AI-as-a-Judge*) revisa **cada respuesta informativa y cada acción antes de que se escriba en la agenda o en el CRM**. Lo dudoso queda congelado hasta que una persona lo aprueba en Slack.
- Las **urgencias, los temas de dinero, los reclamos legales y los pedidos de historia clínica** no los resuelve la inteligencia artificial: se responden con un texto fijo y pasan a una persona.

## Resultados

| | Medido en las pruebas (15/10/2026) | Proyección mensual |
|---|---|---|
| Pedidos resueltos como se esperaba | **48 de 48** (batería de 16 casos × 3 configuraciones) | — |
| Tiempo de respuesta al sistema que pide | **0,08 s** promedio (el proceso sigue en segundo plano: 7,5 s) | Respuesta en segundos, a cualquier hora |
| Casos rojos detectados y derivados | **9 de 9** | 100 % al equipo humano |
| Pedidos duplicados bloqueados | **3 de 3** (más los reintentos del canal) | Ningún turno ni mensaje repetido |
| Costo en inteligencia artificial | **US$ 0,0165** por consulta y **US$ 0,0092** por gestión de turno | **US$ 59,91** por mes (todo con el modelo potente: US$ 105,66) |
| Horas de trabajo liberadas | — | **183 h/mes ($ 1.832.600)** |
| Beneficio neto y recupero | — | **$ 1.493.521 por mes**; la implementación se recupera en **1,1 meses** |

*Las proyecciones parten del baseline y de los volúmenes de la Sección 4.1. Las cifras medidas salen de las ejecuciones registradas, cada una con su código de seguimiento (`traceId`).*

## Riesgos y cómo se controlan

| Riesgo | Control |
|---|---|
| Que el sistema invente un dato o escriba algo equivocado | El supervisor revisa antes de responder y antes de escribir. Con nota menor a 4/5, la acción se congela y decide una persona |
| Que una urgencia o un tema sensible quede en manos de la IA | Triaje con reglas fijas antes de la IA, respuesta inmediata con la guardia y el 107, escalado con los datos del paciente y freno de mano para pausar todo |
| Que una falla técnica deje al paciente sin respuesta o duplique registros | Respuesta inmediata con código de seguimiento, control de pedidos repetidos, reintentos, alertas en castellano al equipo y aviso de demoras al paciente |

## Dónde está cada criterio de la consigna

| Criterio de aceptación | Evidencia en este documento |
|---|---|
| Petición por webhook con respuesta inmediata y proceso asincrónico | Sección 2.3: Receptor (202 en 0,08 s) y Manager en segundo plano |
| Supervisor *AI-as-a-Judge* antes de consolidar datos o registrar en el CRM | Secciones 2.2 (etapas 5 y 7) y 3: el Juez revisa respuestas y acciones; umbral 4/5 y cola de aprobación en Slack |
| Resultado validado despachado por un canal externo | Sección 2.2 (etapa 10): Telegram (voz o texto), borradores de Gmail y Slack |
| Arquitectura modular Manager-Worker | Sección 2.1: 14 workflows independientes y un Manager que delega |
| RAG que cita fuentes con metadatos reales y responde «No sé» | Sección 2.6 y ejemplos de la Sección 3.3 |
| Reintentos y fallas sin duplicar registros ni envíos | Secciones 2.3 y 2.5: control de pedidos repetidos, escritura que actualiza en lugar de duplicar, ramas de error y alertas |
| Sin claves ni tokens expuestos | Anexo A: solo nombres de variables y credenciales |
