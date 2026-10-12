<div class="encabezado"><b>Pre-entrega Módulo 7 — Diseño arquitectónico de un sistema agéntico vertical (Salud)</b><br>Proyecto integrador AgendaBot · AI Automation Avanzado (Coderhouse) · Julio Martín Waisburd · {{FECHA}}</div>

# 1. Relevamiento del proceso y framework de priorización

**Industria:** salud ambulatoria privada: Clínica LoDeTincho (nombre anonimizado), con consultorios, diagnóstico por imágenes y guardia. **Proceso:** la **Central de Turnos** (sacar, modificar, consultar y confirmar turnos) y las consultas informativas (especialidades, profesionales, horarios, estudios, coberturas).

**Problema operativo.** La demanda entra por teléfono, email y mensajería y la atienden personas que repiten todo el día las mismas tareas. En los picos el teléfono se satura, fuera de horario nadie responde y los errores de carga (datos incompletos, turnos duplicados) se descubren cuando el paciente llega.

**Por qué agéntico.** Los pedidos llegan en lenguaje natural ("pasame el de mañana para el jueves a la tarde"), mezclan intenciones y dependen del contexto del paciente: un flujo con IF fijos no los interpreta; un sistema de especialistas acotados, bajo reglas de negocio y con un humano para lo delicado, sí.

## Framework de priorización del asesor (1 = bajo, 5 = alto; máximo 25)

En **accesos regulados**, 5 = poco dato regulado en juego; 1 = alto riesgo regulatorio (los datos de salud son *datos sensibles*, Ley 25.326, y la historia clínica tiene régimen propio, Ley 26.529).

| Proceso | Operación | Ingresos | Viabilidad no-code | Accesos regulados | Adopción | Total | Fundamento y decisión |
|---|---|---|---|---|---|---|---|
| Gestión de turnos | 5 | 4 | 5 | 4 | 4 | **22** | Grueso del volumen; cada turno es facturable y ya no se pierden los pedidos fuera de horario; ya funciona en n8n; solo datos personales y motivo. **Prioridad 1** |
| Consultas informativas (RAG) | 4 | 3 | 5 | 5 | 4 | **21** | ~40 % de los contactos; convierte consultas en turnos; información pública, sin datos del paciente. **Prioridad 1** |
| Recordatorios previos al turno | 3 | 4 | 4 | 4 | 5 | 20 | El ausentismo es un turno no facturado; no exige acción del paciente. Prioridad 2 |
| Facturación, reintegros, coberturas | 3 | 4 | 2 | 2 | 3 | 14 | Impacta en la caja, pero sin API y con datos financieros. **Escalar a humano** |
| Triaje de urgencias médicas | 5 | 2 | 2 | 1 | 2 | 12 | Riesgo clínico y legal máximo. **Solo detectar y derivar a humano** |

## Baseline: punto de partida manual

> **Supuestos** razonables para una clínica ambulatoria mediana, no datos reales: sirven para medir la mejora y se validan en el piloto (página 3).

| Tarea manual | Quién la hace | Volumen diario | Tiempo por gestión | Min/día |
|---|---|---|---|---|
| Sacar un turno nuevo | Administrativas de la Central de Turnos | 70 | 4 min | 280 |
| Modificar o cancelar un turno | Ídem | 38 | 3 min | 114 |
| Consulta informativa | Ídem | 72 | 2,5 min | 180 |
| Confirmación o recordatorio | Ídem | 70 | 1 min | 70 |
| **Total** | **3 administrativas, de 8 a 20 h** | **250** | | **644 (≈ 10,7 h)** |

**Por mes** (22 días hábiles): ≈ **236 h** de trabajo repetitivo. **Costo** (supuesto: $ 10.000 por hora): ≈ **$ 2.360.000 por mes**. **Calidad** (supuestos): 5 % de turnos con datos incompletos o duplicados, 6 minutos de espera en picos y 20 % de contactos fuera de horario sin respuesta hasta el día siguiente.
