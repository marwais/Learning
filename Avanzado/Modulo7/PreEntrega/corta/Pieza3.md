# 3. Propuesta de valor y semáforo de riesgo (HITL)

**Propuesta de valor.** La Central de Turnos atiende las 24 horas, por el canal que el paciente ya usa (chat, email o un audio de Telegram), y el equipo administrativo deja de repetir tareas para ocuparse de los casos que necesitan una persona. Las preguntas frecuentes se contestan con la información oficial de la clínica, citando la fuente, y todo lo sensible (una urgencia, un reclamo, un tema de dinero) llega a un humano con el caso ya resumido.

## KPIs (definidos antes de implementar; piloto de 4 semanas)

| KPI | Línea de base (supuesta) | Meta del piloto |
|---|---|---|
| Tasa de resolución autónoma (gestiones sin intervención humana) | 0 % | ≥ 60 % |
| Horas administrativas liberadas | 0 h | ≥ 120 h por mes (≈ $ 1.200.000) |
| Respuestas informativas correctas (muestra auditada) | — | ≥ 95 % |
| Escalados correctos ante señales críticas | — | 100 % |
| Turnos con datos incompletos o duplicados | 5 % | < 1 % |
| Tiempo de respuesta | 6 min en picos (prototipo: 15–21 s) | ≤ 20 s texto y voz |
| Contactos fuera de horario sin respuesta | 20 % | 0 % |
| Turnos sacados fuera de horario (ingresos) | 0 % | ≥ 10 % del total |
| Ausentismo (ingresos) | 15 % (supuesto) | ≤ 10 % con recordatorios |

## Semáforo operativo de riesgo

| Nivel | Acciones | Autonomía |
|---|---|---|
| 🟢 Verde | Logs y memoria; consultas informativas validadas; consultar turnos propios; alta de turno con datos completos; actualizar contacto; avisos fijos | **100 % autónomas** |
| 🟡 Amarillo | Reprogramar o cancelar un turno; confirmación por email (queda como **borrador**); respuesta rechazada por el validador | **100 % autónomas, sin congelamiento**; auditoría humana diaria posterior |
| 🔴 Rojo | **Urgencia médica** ("dolor en el pecho", "no puedo respirar"); **reclamos o amenazas legales**; **dinero** (reintegros, cobros, coberturas); pedidos de **historia clínica** o datos de terceros; **riesgo de abandono (churn)**: más de 2 cancelaciones en 30 días; 2 fallas de comprensión seguidas | **Congelamiento + supervisión humana obligatoria** |

**Frontera taxativa:** solo el rojo congela y exige un humano. En rojo, el bot no resuelve: responde una frase fija ("Tu consulta la tiene que ver una persona del equipo; ya le avisé") y, ante una urgencia, indica de inmediato la **guardia 24 h**.

## Protocolo de escalado forzado (Slack con botones)

1. **Detección:** nodos IF y Switch (sin código) previos al Router buscan las señales rojas y el Router marca `riesgo: "alto"` cuando las infiere; cualquiera de los dos escala.
2. **Congelamiento:** el flujo se detiene en **Slack › Send and Wait for Response** a `#soporte`, con el resumen del caso, la señal y los últimos 3 mensajes.
3. **Botones:** **Tomar el caso** (el bot deja de responder) · **Responder con plantilla** · **Descartar** (falso positivo, queda registrado).
4. **Sin respuesta en 15 min:** se reenvía a coordinación por email; fuera de horario, el paciente recibe el teléfono de la guardia.
5. **Trazabilidad:** cada escalado queda en la memoria del paciente y en el log, para auditar sesgos y falsos positivos.
