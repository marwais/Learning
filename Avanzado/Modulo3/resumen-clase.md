# Resumen de la clase — Módulo 3: Memoria y Persistencia

**Curso:** AI Automation Avanzado · **Duración del video:** 2 h 28 min
**Tema:** de la amnesia a la memoria persistente — darle al agente memoria de largo plazo externa.

> Nota: la clase del M3 fue **muy práctica** (screen-share de n8n, casi sin slides). El resumen conceptual
> se apoya en el material escrito del módulo (las 4 unidades); el barrido del video se usó para mapear la
> clase y capturar el armado real del circuito de memoria.

## Recorrido de la clase (barrido del video)

| Minuto | Contenido |
|--------|-----------|
| 00–55 | Práctica en vivo: AI Agent, `On form submission`, formulario de Registro, prompts de sistema. |
| ~60 | Teoría de memoria (ventana de contexto vs. persistencia; Estado/Memoria/Conocimiento). |
| ~70 | Se agrega el sub-nodo **Memory** al AI Agent (Simple/Postgres/Redis Chat Memory). |
| ~80–105 | ☕ Break. |
| ~110 | Dos AI Agents encadenados, cada uno con Simple Memory. |
| ~120 | Configuración de credenciales (OAuth Google Cloud) para la base externa. |
| ~130 | **Base relacional de memoria** (`Session_ID, Fecha, Resumen Consolidado, Estado, Datos Clave`). |
| ~140 | **Circuito de memoria**: `Get rows → Code → Filter → IF → AI Agent (+Memory) → Update row`. |

## Las 4 unidades

### 1. Ventana de contexto (corto plazo) vs. persistencia (largo plazo)
- Las ejecuciones de n8n son **efímeras**: sin base externa, la memoria muere al cerrar la sesión.
- Tres capas: **Estado** (situación del flujo), **Memoria** (histórico del usuario), **Conocimiento** (docs institucionales).
- Criterios: relevancia operativa, limpieza de contexto, latencia vs. fidelidad, gobernanza (no persistir tokens/passwords).

### 2. Memoria de largo plazo con herramientas no-code
- **Memoria integrada de n8n**: rápida (Window Buffer / Simple Memory), pero caja negra (no se ve ni edita).
- **Airtable / Sheets**: control total, estructura por columnas, auditable, escalable → opción profesional.
- Dos flujos clave: **escritura al cerrar** y **lectura al iniciar**, siempre filtrando por `Session_ID`.
- Errores: guardar la transcripción completa; no manejar el usuario nuevo; sobrecargar el prompt con todo el historial; no actualizar el registro (usar Update, no Create, en recurrentes).

### 3. Shared memory (contexto compartido entre agentes)
- Un **tablero central** (Airtable) como "sistema nervioso" que todos los agentes leen y escriben.
- Patrón por agente: **Leer → Actuar → Escribir**, filtrando por `ID del Caso`.
- Anti-colisión: orquestación secuencial, escritura por filas nuevas (historial acumulativo), o semáforo por `Estado` (IF/Switch).
- Regla: si otro agente no necesita ese dato, **no** se guarda en el tablero (evita el "depósito de basura textual").

### 4. Búsqueda semántica / Vector Store
- Para **documentos** largos (manuales, políticas): la búsqueda exacta falla ante sinónimos.
- **Vector Store** (LlamaCloud) entiende **significado**: fragmenta el doc en *chunks* y trae los 2–3 más cercanos.
- Regla de arquitectura: **Airtable/Sheets** para datos estructurados y dinámicos; **Vector Store** para conocimiento estático de texto libre. El patrón maestro combina ambos en paralelo.
- Errores: usar planillas como depósito de manuales; creer que el Vector Store reemplaza la base relacional; alimentarlo con documentos desactualizados o contradictorios.

## Síntesis

La memoria de largo plazo convierte un agente de demo en uno de producción: acumula contexto entre
sesiones y mejora cada interacción. El circuito robusto es **leer (por Session_ID) → inyectar contexto →
actuar → resumir y persistir (upsert idempotente)**, guardando siempre resúmenes accionables y nunca la
transcripción cruda.

> Para la consigna, el esquema de datos, los prompts y el checklist de la Pre-entrega 3, ver [`README.md`](./README.md).
