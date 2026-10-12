# 1. Relevamiento del proceso y framework de priorización

**Industria:** salud ambulatoria privada. **Organización:** Clínica LoDeTincho (nombre anonimizado), con consultorios de varias especialidades, diagnóstico por imágenes y guardia. **Proceso:** la **Central de Turnos**: sacar, modificar, consultar y confirmar turnos, y responder consultas informativas (especialidades, profesionales, horarios, estudios, preparación, coberturas).

**Problema operativo.** La demanda entra por teléfono, email y mensajería, y la atienden personas que repiten todo el día las mismas tareas: buscar un hueco en la agenda, anotar los datos del paciente, confirmar por email y contestar preguntas cuya respuesta está en documentos internos. En los picos, el teléfono se satura; fuera de horario, nadie responde; y los errores de carga (datos incompletos, turnos duplicados) se detectan recién cuando el paciente llega.

**Por qué una solución agéntica y no una automatización lineal.** Los pedidos llegan en lenguaje natural ("pasame el de mañana para el jueves a la tarde"), mezclan intenciones y dependen del contexto del paciente. Un flujo con IF fijos no los interpreta; un agente con especialistas acotados sí, siempre que trabaje bajo reglas de negocio y con un humano para lo delicado.

## Framework de priorización del asesor

Escala 1 a 5; todos los vectores pesan igual (máximo 25). En **accesos regulados**, 5 significa poco dato regulado en juego y 1, datos o decisiones de alto riesgo regulatorio: en salud, los datos de salud son **datos sensibles** (Ley 25.326 de Protección de Datos Personales) y la historia clínica tiene un régimen propio (Ley 26.529 de Derechos del Paciente).

| Proceso candidato | Impacto en la operación | Impacto en ingresos | Viabilidad no-code | Accesos regulados | Adopción probable | Total | Decisión |
|---|---|---|---|---|---|---|---|
| **Gestión de turnos** (sacar, modificar, consultar, confirmar) | 5 — es el grueso del volumen de la central | 4 — cada turno es una prestación facturable; se dejan de perder los pedidos fuera de horario | 5 — ya funciona en n8n con Sheets | 4 — nombre, contacto y motivo: datos personales, con el motivo como dato de salud mínimo | 4 — el paciente ya escribe por mensajería | **22** | **Prioridad 1** |
| **Consultas informativas** con base documental (RAG) | 4 — ~40 % de los contactos | 3 — convierte consultas en turnos | 5 — RAG con validador funcionando | 5 — información pública de la clínica, sin datos del paciente | 4 — respuestas con cita de fuente | **21** | **Prioridad 1** |
| Recordatorios previos al turno | 3 — reduce llamadas de confirmación | 4 — el ausentismo es un turno no facturado | 4 — disparo programado | 4 — solo datos del turno | 5 — no requiere acción del paciente | 20 | Prioridad 2 |
| Facturación, reintegros y coberturas | 3 | 4 — impacta directo en la caja | 2 — sistemas de facturación sin API | 2 — datos de cobertura y financieros | 3 | 14 | No automatizar; escalar a humano |
| Triaje de urgencias médicas | 5 | 2 | 2 — requiere protocolo médico | 1 — riesgo clínico y legal máximo | 2 — baja confianza del paciente | 12 | **Fuera de la autonomía**: solo detectar y derivar a humano |

## Baseline: punto de partida manual

> **Supuestos.** Los números de esta sección no provienen de la clínica real: son supuestos razonables para una clínica ambulatoria mediana, declarados para poder medir la mejora. Se validan en el piloto (pieza 3, KPIs).

| Tarea manual | Quién la hace hoy | Volumen diario (supuesto) | Tiempo por gestión (supuesto) | Minutos por día |
|---|---|---|---|---|
| Sacar un turno nuevo | Administrativas de la Central de Turnos | 70 | 4 min | 280 |
| Modificar o cancelar un turno | Ídem | 38 | 3 min | 114 |
| Consulta informativa (horarios, profesionales, estudios) | Ídem | 72 | 2,5 min | 180 |
| Confirmación o recordatorio manual | Ídem | 70 | 1 min | 70 |
| **Total** | **3 administrativas, de 8 a 20 h** | **250 contactos** | | **644 min ≈ 10,7 h por día** |

- **Horas por mes** (22 días hábiles): ≈ **236 h** de trabajo administrativo repetitivo.
- **Costo** (supuesto, a efectos de la muestra: $ 10.000 por hora administrativa): 236 h × $ 10.000 ≈ **$ 2.360.000 por mes** solo en estas tareas.
- **Calidad** (supuestos): 5 % de los turnos con datos incompletos o duplicados; espera telefónica promedio de 6 minutos en picos; 20 % de los contactos fuera de horario quedan sin respuesta hasta el día siguiente.
