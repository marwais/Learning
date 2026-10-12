# 3. Propuesta de valor y semáforo de riesgo (HITL)

## Propuesta de valor

**La Central de Turnos atiende las 24 horas, por el canal que el paciente ya usa, y el equipo administrativo deja de repetir tareas para ocuparse de los casos que necesitan una persona.** El paciente saca, cambia o consulta su turno por chat, email o un audio de Telegram, y recibe la respuesta en segundos; las preguntas frecuentes se contestan con la información oficial de la clínica, citando la fuente; y todo lo sensible (una urgencia, un reclamo, un tema de dinero) llega a un humano con el caso ya resumido.

## KPIs (definidos antes de implementar)

Línea de base: el baseline supuesto de la pieza 1. Se miden durante un piloto de 4 semanas con los logs de n8n y la planilla de turnos.

| KPI | Cómo se mide | Línea de base (supuesta) | Meta del piloto |
|---|---|---|---|
| Tasa de resolución autónoma | Gestiones cerradas sin intervención humana / total | 0 % | ≥ 60 % |
| Horas administrativas liberadas | (gestiones autónomas × minutos del baseline) / 60 | 0 h | ≥ 120 h por mes |
| Respuestas informativas correctas | Muestra semanal auditada contra la base documental | — | ≥ 95 % (en el M5: 5 de 5 en validación ciega) |
| Escalados correctos | Casos con señal crítica que llegaron a un humano / casos con señal crítica | — | 100 % |
| Turnos con datos incompletos o duplicados | Revisión de la planilla | 5 % | < 1 % |
| Tiempo de respuesta | Del mensaje a la respuesta | 6 min de espera en picos (hoy, en el prototipo: 15 a 21 s) | ≤ 20 s en texto y en voz |
| Contactos fuera de horario sin respuesta | Mensajes fuera de 8–20 h sin contestar | 20 % | 0 % |
| Turnos sacados fuera de horario (impacto en ingresos) | Turnos registrados entre las 20 y las 8 h / total | 0 % | ≥ 10 % |
| Ausentismo (impacto en ingresos) | Turnos sin presentación / turnos dados | Supuesto: 15 % | ≤ 10 % con recordatorios (prioridad 2) |

## Semáforo operativo de riesgo

| Nivel | Acciones | Autonomía |
|---|---|---|
| 🟢 **Verde** | Registrar logs y memoria; responder consultas informativas validadas; consultar los turnos propios; dar de alta un turno con datos completos; actualizar un contacto en HubSpot; avisos fijos (fuera de alcance, audio ilegible) | **100 % autónomas** |
| 🟡 **Amarillo** | Reprogramar o cancelar un turno; enviar una confirmación por email (queda como **borrador** en Gmail); respuesta que el validador rechazó | **100 % autónomas, sin congelamiento**; además quedan en un reporte que un humano audita una vez por día |
| 🔴 **Rojo** | Señales de **urgencia médica** ("dolor en el pecho", "no puedo respirar"); **reclamos o amenazas legales**; **dinero**: reintegros, cobros, diferencias de cobertura; pedidos de **historia clínica** o datos de otra persona; **riesgo de abandono (churn)**: más de 2 cancelaciones del mismo paciente en 30 días; 2 fallas de comprensión seguidas | **Congelamiento + supervisión humana obligatoria** |

**Frontera taxativa:** solo las acciones rojas congelan el flujo y exigen a un humano; las verdes y amarillas se ejecutan solas (el amarillo, con auditoría posterior).

**En rojo, el bot no resuelve:** responde una frase fija ("Tu consulta la tiene que ver una persona del equipo; ya le avisé") y, ante una urgencia médica, indica de inmediato la **guardia 24 h** sin esperar a nadie.

## Protocolo de escalado forzado (Slack con botones)

1. **Detección:** antes del Router, nodos IF y Switch (sin código) buscan las señales rojas (lista de palabras y patrones) y el Router marca `riesgo: "alto"` cuando las infiere. Cualquiera de los dos dispara el escalado; no se le deja al modelo la decisión de **no** escalar.
2. **Congelamiento:** el flujo se detiene en un nodo **Slack › Send and Wait for Response** dirigido a `#soporte`, con el resumen del caso, la señal detectada y los últimos 3 mensajes.
3. **Botones:** **Tomar el caso** (una persona contacta al paciente y el bot no responde más en esa conversación), **Responder con plantilla** (el bot envía el texto aprobado) o **Descartar** (falso positivo; queda registrado para mejorar la detección).
4. **Tiempo de espera:** si nadie responde en 15 minutos en horario laboral, se reenvía a la coordinación por email; fuera de horario, el paciente recibe el teléfono de la guardia.
5. **Trazabilidad:** cada escalado y su decisión quedan en la memoria del paciente (Airtable) y en el log, para auditar sesgos y falsos positivos cada semana.

*Estado:* el log a Slack, el borrador de Gmail y el validador ya funcionan en el M6; el nodo de aprobación con botones es la incorporación propuesta en este diseño.
