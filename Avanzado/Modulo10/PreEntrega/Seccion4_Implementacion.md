# 4. Plan de implementación y control de metadatos

## Hitos de los primeros 30 días

Ejemplo con inicio el lunes 2 de noviembre de 2026. Las fechas se corren según la firma.

| Día | Fecha objetivo | Hito | Responsable |
|---|---|---|---|
| 1 | 02/11 | **Arranque.** Se firman los objetivos, el semáforo de riesgo y la regla de facturación | Dirección de la clínica (sponsor) + Asesor de IA |
| 3 | 04/11 | **Auditoría del proceso actual.** Se miden durante una semana los volúmenes, los tiempos y los errores reales: es el baseline que valida el business case | Coordinadora de la Central de Turnos |
| 5 | 06/11 | **Cuentas y accesos a nombre de la clínica** (correo, agenda, CRM, Slack, Telegram) y topes de gasto en los servicios de IA | Responsable de Sistemas |
| 8 | 09/11 | **Biblioteca oficial validada.** Se cargan los documentos vigentes (cartilla, horarios, estudios, políticas) y se descartan los vencidos | Dirección médica y administrativa (dueña del conocimiento) + Asesor de IA |
| 10 | 11/11 | **Trazabilidad lista.** Campos de origen en el CRM y columna de asistencia en la agenda (ver abajo). **Empieza la Fase 0, en modo sombra** | Asesor de IA + Responsable de Sistemas |
| 17 | 18/11 | **Capacitación del equipo:** cómo aprobar o editar en Slack, tomar un caso y usar el freno de mano | Asesor de IA + Coordinadora |
| 24 | 25/11 | **Comité de salida de la Fase 0.** Con el reporte de 200 casos se decide si se pasa a la Fase 1 | Dirección de la clínica + Coordinadora + Asesor de IA |
| 25 | 26/11 | **Empieza la Fase 1:** piloto de solo lectura con pacientes reales (consultas informativas) | Coordinadora |
| 30 | 01/12 | **Reporte de los 30 días:** indicadores contra el baseline, primera conciliación del CRM y plan para la Fase 2 | Asesor de IA → Dirección de la clínica |

## Trazabilidad: el CRM como única fuente de verdad

Cada conversación nace con un **código de seguimiento** único, que viaja con el pedido por todo el sistema. El mismo código queda en tres lugares, así que cualquier turno se puede reconstruir de punta a punta:

| Dónde | Qué se registra |
|---|---|
| **CRM** (ficha del paciente) | **Origen = AgendaBot**, código de seguimiento, canal (chat, email o Telegram), fecha de la última interacción del sistema, turno gestionado, resultado del Supervisor y si hubo escalado a una persona |
| **Agenda de turnos** | Código de seguimiento en cada turno que registró el sistema, estado (confirmado, reprogramado, cancelado) y **asistencia**, que marca la recepción |
| **Registro de auditoría** | Cada respuesta revisada por el Supervisor, con fecha y hora, la versión de las instrucciones, el puntaje y la decisión. Los datos personales se enmascaran |

**Cómo se factura sin discusiones.** El primer día hábil de cada mes se cruzan la agenda y el CRM. Se facturan solo los turnos con el código del sistema, **Origen = AgendaBot**, asistencia marcada y dentro de la ventana de 30 días. La lista se comparte con la clínica antes de facturar, y cualquier turno se puede verificar con su código. Si alguien del equipo reprograma o vuelve a cargar a mano un turno del sistema, el código original sigue en el CRM: nadie pierde la atribución por un cambio manual, y tampoco se cobra dos veces.

## Defensa ante el comité: tres objeciones

**"Esto ya lo hace mi CRM."**
El CRM **registra** lo que pasó; AgendaBot **hace el trabajo**. Conversa con el paciente a cualquier hora y por su canal, saca o cambia el turno, lo confirma y deja todo cargado en el CRM con su origen. Hoy 1 de cada 5 contactos fuera de horario espera hasta el día siguiente, y el CRM no los atiende. AgendaBot no reemplaza al CRM: lo alimenta con datos completos y trazables.

**"¿Y si el agente alucina y borra datos?"**
Tres barreras independientes:

1. **Despliegue por fases:** hasta el día 75 el sistema no escribe nada en la agenda ni en el CRM sin que una persona lo apruebe con un botón (Fases 0 a 2).
2. **Supervisor de calidad:** cada respuesta informativa se contrasta con la biblioteca oficial antes de salir. Si el dato no está en los documentos, el sistema responde que no lo sabe. En las pruebas, el 70,6 % de las respuestas salió aprobada de entrada; el resto se corrigió o pasó a una persona antes de llegar al paciente.
3. **Límites de escritura:** el sistema **no tiene permiso para borrar**. Solo registra turnos con los datos completos (nombre, fecha, hora y email) y actualiza su estado: una cancelación queda en el historial. Todo lo rojo (urgencias, reclamos, dinero, historia clínica) va siempre a una persona.

Y el freno de mano está siempre a disposición de la coordinadora.

**"Es caro para el ahorro que genera."**
Comparado contra el baseline, el sistema libera 183 horas por mes ($ 1.832.600) y cuesta $ 774.360 con todo incluido: servicios, abono y pago por resultado. La clínica gana **$ 1.058.240 netos por mes** y recupera la implementación en **1,5 meses**. Aun en el escenario conservador gana más de $ 700.000 por mes. Además, $ 332.700 de ese costo (el 43 %) es pago por resultado: solo se paga por turnos que los pacientes efectivamente usaron. Si el sistema no genera valor, la clínica no paga esa parte. No vendemos una herramienta: vendemos capacidad para absorber más pacientes sin sumar personal y menos fricción para el paciente.
