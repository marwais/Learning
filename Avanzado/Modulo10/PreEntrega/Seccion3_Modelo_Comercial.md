# 3. Modelo comercial e incentivos

Un sistema como AgendaBot **no se entrega y se olvida: se opera, se mide y se mejora**. Por eso proponemos un modelo **híbrido**: un pago inicial por construirlo, un abono mensual por mantenerlo sano y un pago por resultado que solo se cobra cuando el sistema genera valor medible.

## Los tres componentes

| Componente | Monto | Qué cubre |
|---|---|---|
| **1. Implementación** (una sola vez) | **$ 1.600.000** | Auditoría del proceso actual (baseline medido), diseño, configuración sobre las cuentas de la clínica, carga y validación de la biblioteca oficial, pruebas, capacitación del equipo, documentación y acompañamiento de la Fase 0 |
| **2. Abono mensual de soporte** | **$ 250.000 por mes** | Mejora continua del sistema (ver el alcance abajo). Cubre nuestro costo operativo: no depende de los resultados |
| **3. Pago por resultado** | **$ 300 por turno** atribuible | Solo los turnos que el sistema gestionó de punta a punta y que el paciente efectivamente usó (KPI abajo) |

Los servicios en la nube y de mensajería (**US$ 136,90 por mes**, unos **$ 191.660**) se contratan a nombre de la clínica, con topes de gasto: los datos y las cuentas son siempre del cliente.

## KPI de facturación

**Turno atribuible:** un turno nuevo o reprogramado que el sistema registró de punta a punta y al que **el paciente asistió**.

Cuenta solo si se cumplen las tres condiciones:
1. El turno está en la agenda con el **código de seguimiento** del sistema.
2. El contacto en el CRM tiene **origen = AgendaBot** y ese mismo código.
3. La recepción marcó la **asistencia** en la agenda.

**No cuentan:** los turnos que tomó una persona por un escalado (casos rojos), los duplicados, los cancelados y las inasistencias. El indicador es **atribuible** (lo registra el propio sistema), **auditable** (el código une la conversación, la agenda y el CRM) y **escalable** (crece con el volumen de la clínica).

## Ventana de conversión: 30 días

Un turno se atribuye al sistema si el paciente **asiste dentro de los 30 días posteriores a la última interacción del sistema** con ese paciente. Si en ese plazo una persona del equipo reprograma el turno, sigue contando: el código de seguimiento original queda en el CRM. Pasados los 30 días, el turno es de la clínica. La ventana cubre la anticipación habitual de un turno ambulatorio y evita discutir conversiones de meses atrás.

## Alcance del abono mensual

| Incluye | Detalle |
|---|---|
| **Ajuste de instrucciones** | Revisión mensual de los registros de conversación para corregir respuestas flojas o mal derivadas |
| **Actualización de la biblioteca** | Carga de los documentos que cambian (cartilla, horarios, novedades) y baja de los vencidos, según el plan de gobernanza |
| **Gestión de proveedores de IA** | Adaptación a cambios de los proveedores y prueba de alternativas más baratas o rápidas sin perder calidad |
| **Revisión de indicadores** | Reporte mensual: resolución autónoma, exactitud del Supervisor, escalados, costo por consulta y turnos atribuibles |
| **Soporte** | Respuesta en el día hábil ante una falla y freno de mano disponible las 24 h |

**No incluye:** nuevos canales ni nuevos procesos (por ejemplo, facturación o reintegros). Se cotizan aparte.

## Qué paga la clínica y qué gana

Escenarios por mes. El beneficio son las horas liberadas a $ 10.000 la hora. Los turnos atribuibles salen de los turnos nuevos que el sistema resuelve solo (sobre 1.540 por mes según el baseline), descontando un 10 % de inasistencias (la meta con recordatorios).

| Por mes | Conservador | **Base** | Optimista |
|---|---|---|---|
| Autonomía (gestiones sin intervención humana) | 60 % | **78 %** | 90 % |
| Horas liberadas | 142 h | **183 h** | 213 h |
| **Beneficio** | $ 1.417.200 | **$ 1.832.600** | $ 2.125.800 |
| Servicios en la nube y mensajería | $ 191.660 | $ 191.660 | $ 191.660 |
| Abono de soporte | $ 250.000 | $ 250.000 | $ 250.000 |
| Pago por resultado (turnos asistidos × $ 300) | $ 249.600 (832) | **$ 332.700 (1.109)** | $ 374.100 (1.247) |
| **Costo total** | $ 691.260 | **$ 774.360** | $ 815.760 |
| **Beneficio neto** | $ 725.940 | **$ 1.058.240** | $ 1.310.040 |
| **Recupero de la implementación** | 2,2 meses | **1,5 meses** | 1,2 meses |

**Incentivos alineados.** El abono garantiza que el sistema se mantenga sano aunque baje la demanda. El pago por resultado nos pone del lado de la clínica: ganamos más solo si más pacientes sacan y usan sus turnos sin pasar por el teléfono. En el escenario conservador la clínica sigue ganando más de $ 700.000 por mes.
