# 1. Narrativa ejecutiva y arquitectura de valor

## El problema: una Central de Turnos que no da abasto

La Clínica LoDeTincho (nombre anonimizado) recibe unas **250 gestiones por día**: sacar, cambiar, consultar y confirmar turnos, y preguntas sobre especialidades, horarios y estudios. Hoy las atienden **tres administrativas de 8 a 20 h**, que repiten las mismas tareas todo el día:

- **236 horas por mes** de trabajo repetitivo, equivalentes a **$ 2.360.000** mensuales.
- En los picos, **6 minutos de espera**; fuera de horario, **1 de cada 5 contactos** queda sin respuesta hasta el día siguiente.
- **5 % de los turnos** tiene datos incompletos o duplicados, y el error se descubre cuando el paciente llega.

## La promesa

**AgendaBot es una Central de Turnos digital que atiende las 24 horas, por el canal que el paciente ya usa, y libera al equipo para los casos que necesitan una persona.** Resultado medible en el piloto: **al menos 120 horas por mes liberadas**, respuestas en menos de 20 segundos y ningún contacto sin respuesta fuera de horario. Lo sensible (una urgencia, un reclamo, un tema de dinero) siempre llega a una persona, con el caso ya resumido.

## Cómo está organizado: un equipo, no un programa

AgendaBot funciona como un **equipo de analistas virtuales especializados**, coordinado por un supervisor y con un humano que tiene siempre la mano en el freno.

<svg viewBox="0 0 760 360" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif">
  <defs><marker id="f" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#4b5563"/></marker></defs>
  <rect x="10" y="20" width="150" height="160" rx="10" fill="#eef2f6" stroke="#0b3d5c"/>
  <text x="85" y="44" text-anchor="middle" font-size="13" font-weight="700" fill="#0b3d5c">El paciente escribe</text>
  <text x="85" y="72" text-anchor="middle" font-size="12">Chat web</text>
  <text x="85" y="96" text-anchor="middle" font-size="12">Email</text>
  <text x="85" y="120" text-anchor="middle" font-size="12">Telegram (texto</text>
  <text x="85" y="136" text-anchor="middle" font-size="12">o nota de voz)</text>
  <text x="85" y="164" text-anchor="middle" font-size="11" fill="#4b5563">24 h, 365 días</text>
  <rect x="215" y="60" width="160" height="80" rx="10" fill="#0b3d5c"/>
  <text x="295" y="92" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">Coordinador</text>
  <text x="295" y="112" text-anchor="middle" font-size="11" fill="#dbe7f0">entiende el pedido y</text>
  <text x="295" y="126" text-anchor="middle" font-size="11" fill="#dbe7f0">lo asigna al especialista</text>
  <line x1="160" y1="100" x2="213" y2="100" stroke="#4b5563" stroke-width="2" marker-end="url(#f)"/>
  <g font-size="12">
    <rect x="430" y="10" width="160" height="40" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="510" y="35" text-anchor="middle">Agenda: sacar y cambiar</text>
    <rect x="430" y="58" width="160" height="40" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="510" y="83" text-anchor="middle">Consulta de turnos</text>
    <rect x="430" y="106" width="160" height="40" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="510" y="131" text-anchor="middle">Confirmaciones</text>
    <rect x="430" y="154" width="160" height="40" rx="8" fill="#fff" stroke="#0b3d5c"/><text x="510" y="174" text-anchor="middle">Asistente de información</text><text x="510" y="188" text-anchor="middle" font-size="10" fill="#4b5563">cita la fuente o dice "no sé"</text>
  </g>
  <g stroke="#4b5563" stroke-width="1.5" marker-end="url(#f)">
    <line x1="375" y1="90" x2="428" y2="30"/><line x1="375" y1="96" x2="428" y2="78"/><line x1="375" y1="104" x2="428" y2="126"/><line x1="375" y1="112" x2="428" y2="172"/>
  </g>
  <rect x="215" y="215" width="160" height="70" rx="10" fill="#fff4e5" stroke="#c2410c"/>
  <text x="295" y="242" text-anchor="middle" font-size="13" font-weight="700" fill="#9a3412">Supervisor de calidad</text>
  <text x="295" y="260" text-anchor="middle" font-size="11">revisa cada respuesta</text>
  <text x="295" y="274" text-anchor="middle" font-size="11">informativa antes de salir</text>
  <line x1="510" y1="194" x2="377" y2="240" stroke="#c2410c" stroke-width="1.5" marker-end="url(#f)"/>
  <rect x="10" y="215" width="150" height="70" rx="10" fill="#fde8e8" stroke="#b91c1c"/>
  <text x="85" y="242" text-anchor="middle" font-size="13" font-weight="700" fill="#991b1b">Equipo humano</text>
  <text x="85" y="260" text-anchor="middle" font-size="11">aprueba, edita o toma</text>
  <text x="85" y="274" text-anchor="middle" font-size="11">el caso (aviso en Slack)</text>
  <line x1="213" y1="250" x2="162" y2="250" stroke="#b91c1c" stroke-width="1.5" marker-end="url(#f)"/>
  <text x="187" y="244" text-anchor="middle" font-size="10" fill="#991b1b">dudas</text>
  <rect x="620" y="10" width="130" height="275" rx="10" fill="#eef7f1" stroke="#15803d"/>
  <text x="685" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#166534">Herramientas</text>
  <g font-size="11.5" text-anchor="middle"><text x="685" y="62">Agenda de turnos</text><text x="685" y="90">CRM de pacientes</text><text x="685" y="118">Memoria del paciente</text><text x="685" y="146">Biblioteca oficial</text><text x="685" y="160" font-size="10" fill="#4b5563">de la clínica</text><text x="685" y="188">Email (borradores)</text><text x="685" y="216">Slack del equipo</text><text x="685" y="244">Registro de auditoría</text><text x="685" y="258" font-size="10" fill="#4b5563">(cada caso con su código)</text></g>
  <line x1="590" y1="100" x2="618" y2="100" stroke="#15803d" stroke-width="1.5" marker-end="url(#f)"/>
  <text x="380" y="330" text-anchor="middle" font-size="12" fill="#374151">Cada pedido lleva un código de seguimiento de punta a punta: se puede auditar quién hizo qué, cuándo y con qué resultado.</text>
</svg>

**Cómo interactúan.** El **Coordinador** lee el pedido, recuerda al paciente (su historial y sus datos) y lo deriva al especialista que corresponde. Los especialistas trabajan sobre las herramientas de la clínica: la agenda, el CRM y la biblioteca oficial de documentos. Un turno solo se registra con los datos completos (nombre, fecha, hora y email). Antes de que una respuesta informativa llegue al paciente, el **Supervisor de calidad** la contrasta con la fuente: si está bien, sale; si tiene un error, la manda a corregir; si hay dudas, la pasa al **equipo humano** por Slack, con botones para aprobar o editar.

## De la función al beneficio

| Lo que hace el sistema | Lo que gana la clínica |
|---|---|
| Un coordinador que deriva cada pedido a un especialista | Cada tarea la resuelve quien sabe hacerla: menos errores y un sistema fácil de mantener |
| Asistente que responde solo con la biblioteca oficial y cita la fuente | Información verificada en segundos, igual para todos los pacientes; si no está en los documentos, no inventa |
| Supervisor de calidad que revisa cada respuesta informativa | Control automático antes de llegar al paciente; las dudas pasan a una persona |
| Aprobación humana en Slack para lo sensible | El equipo decide en lo delicado, con el caso ya resumido y sin buscar datos |
| Memoria del paciente | Atención personalizada: no hay que repetir nombre, turno ni motivo |
| Atención por chat, email y notas de voz | El paciente usa el canal que ya tiene, a cualquier hora |
| Código de seguimiento en cada caso y registro en el CRM | Auditoría completa y medición del resultado sin discusiones |

## Business case

Números del análisis financiero previo, sin cambios. Son **supuestos razonables**, no datos reales de la clínica: se validan en la auditoría del primer mes.

| Por mes | Monto |
|---|---|
| Horas administrativas liberadas (183 de 236) | **$ 1.832.600** |
| Costo de operación: servicios en la nube, mensajería y 8 h de mantenimiento | $ 351.660 |
| **Beneficio neto** | **$ 1.480.940** |
| **Retorno** (beneficio neto sobre costo de operación) | **4,2 veces** |
| Implementación, una sola vez (80 h técnicas) | $ 1.600.000 |
| **Periodo de recupero (payback)** | **1,1 meses** |

Con el modelo comercial de la Sección 3, que suma el abono mensual y el pago por resultado, el beneficio neto para la clínica queda en **$ 1.058.240 por mes** y la implementación **se recupera en 1,5 meses**. Aun en el escenario conservador se recupera en 2,2 meses (detalle en la Sección 3). No se cuentan como ahorro los turnos nuevos que entran fuera de horario ni la baja del ausentismo con recordatorios: son ganancia adicional.

> **No vendemos despidos: vendemos capacidad.** Las horas liberadas permiten absorber más demanda en los picos sin sumar personal y dedicar al equipo a los casos que necesitan criterio humano.
