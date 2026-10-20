# Contexto vivo: Proyecto Final AgendaBot (M11)

Último guardado: **2026-10-16**, con el commit c577cea en `main`.
El detalle técnico y las pruebas están en `Avanzado/Modulo11/README.md`. Las devoluciones de P1 a P10 y su impacto están en `Avanzado/Modulo11/devoluciones.md`.

## Estado actual
- El **M10 está entregado y cerrado**.
- **Componente A (n8n)**: está en producción, con nombres sin sufijos del curso ("AgendaBot · …"), 15 workflows y todos publicados.
  - **Prioridad 1, hecha**:
    - webhook asincrónico con el Receptor (`POST /webhook/agendabot` responde 202 con traceId, 200 si es duplicado y 400 si es inválido);
    - idempotencia con la Data Table `pedidos_procesados`;
    - el Juez revisa las acciones antes de consolidar y congela en Slack;
    - Error Workflow;
    - workflows modulares;
    - HITL en los emails, que quedan como borrador.
  - **Prioridad 2, hecha**:
    - triaje rojo y escalado humano por Slack con "Tomo el caso" y respuesta al paciente; por defecto, en Telegram: "Nos estaremos comunicando en breve para continuar.";
    - freno de mano (`/webhook/freno-de-mano` con un token del `.env`);
    - metadatos `agendabot_*` en HubSpot (upsert);
    - columna Asistencia;
    - aviso de demora por email;
    - dos fallas de comprensión pasan a una persona;
    - KB anonimizada y nombre enmascarado en el log;
    - alertas en castellano con la identidad del paciente.
  - **Mensajes del canal Telegram**:
    - "Faltan datos que son necesarios para poder agendar turnos: …", con voseo.
    - Si falta el email, se pide directo por escrito. Si el paciente habló, por voz con la aclaración por texto.
    - El pedido queda guardado en la Data Table `pendientes`.
  - **Modelos (configuración C)**: Router y Agente RAG en `claude-haiku-4-5-20251001`, Juez en `claude-sonnet-4-6`.
  - **Batería de 16 casos**: A, B y C dieron 16/16. C cuesta US$ 0,0166 por consulta y US$ 0,0092 por acción.
  - **Batería E** (confirmación con los nombres de producción, después de reconectar Sheets): 16/16, con el mismo costo.
  - **Estado del Caso en Airtable** (`scripts/estado_caso_m11.py`): ahora se calcula según el resultado (antes siempre quedaba "En Progreso"). La ruta informativa ahora actualiza la memoria. El filtro de Gmail frena los rebotes y los correos propios. Las baterías F y G dieron 16/16.
- **Componente B (DMSA)**: tiene un borrador completo, con 4 secciones y los anexos A a C. Sale en 35 páginas como `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf`.
  - Ya no hace referencias a módulos, pre-entregas ni devoluciones (verificado sobre el texto del PDF).
  - Sin sección de video ni "Cómo se levanta el sistema" (decisiones del usuario, 20/10): el Anexo C es solo el inventario de workflows con sus capturas. El Anexo B ya no cita los archivos de la batería.
  - **Finanzas, escenario base**:
    - costo de US$ 127,91 por mes, unos $339.079;
    - beneficio neto de $1.493.521;
    - retorno de 4,40 y recupero en 1,07 meses.

## Decisiones
- **Decisiones del usuario**:
  - **No-Code híbrido**: no se migran los 32 nodos Code; lo nuevo va con nodos visuales.
    - Se descartó migrarlo todo por el costo y el riesgo, con poca ganancia en la rúbrica.
    - En el DMSA no se dice "low-code" ni "código personalizado".
  - **Router y RAG en Haiku, Juez en Sonnet**: la calidad es igual en la batería (16/16) y el costo de tokens baja de US$ 105,66 a US$ 59,91 por mes.
  - **Nombres de producción sin sufijos del curso**: el documento final no puede mostrar artefactos del curso. Rompe a propósito la convención de duplicar cada módulo.
  - **El documento final no tiene referencias a módulos, pre-entregas ni devoluciones**. El criterio del usuario: "lo que no está en este documento, no está".
  - **Nombre del PDF**: `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf`.
  - **Sin video por ahora** (20/10): el usuario no lo va a grabar; se sacó el C.3 del documento. El guion queda en `Avanzado/Modulo11/DMSA/guion_video.md` (con Carlos Demo) por si se retoma.
  - **Sin comando `/nueva`** para separar sesiones de Telegram (propuesto y descartado por el usuario).
- **Decisiones técnicas** (motivo en cada punto):
  - **Túnel por ngrok con dominio fijo**: el quick tunnel de Cloudflare se caía con cada corte de red y la red pública bloquea el puerto 7844.
  - **Idempotencia en el Receptor y en las Data Tables**, no en el staticData del Manager, porque el staticData se guarda recién al terminar la ejecución.
  - **Escalados encadenados en serie**: en una rama paralela no se ejecutaban.

## Restricciones y gotchas de esta etapa
- **Credenciales renombradas**: como la API no permite renombrarlas, se crearon nuevas ("n8n API (alertas)", "Freno de mano"). Las viejas siguen existiendo hasta que el usuario las borre.
- **Links de Slack**: los mensajes de antes del cambio a ngrok tienen links muertos. Para la demo hay que generar casos nuevos.
- **Voz**: ElevenLabs con estabilidad 0,8; con menos, salían voces distintas.
- **Pedidos por voz**: si la nota de voz dicta un email, el pedido se guarda en `pendientes` y se une con el email escrito si llega dentro de los 30 minutos.
- **Herramienta RAG**: cuando no sabe, responde el literal «No sé». La frase "No cuento con ese dato" se eliminó.
- **PDF abierto**: si el usuario tiene el PDF abierto, `build_pdf.py` no lo puede regenerar. Hay que pedirle que lo cierre.
- **Restos de prueba**: quedó el contacto `prueba.m11@example.com` en HubSpot y quedaron borradores de prueba en Gmail.

## Pendientes (por prioridad)
1. **Usuario: revisar el DMSA** (35 páginas), con atención a la diagramación de los Anexos B y C. Claude no pudo ver las páginas: en esta PC no hay con qué convertir el PDF a imagen.
2. **Opcional (Claude):** renombrar los JSON exportados de los workflows en `Avanzado/Modulo11/`, que tienen nombres de archivo viejos ("AI Automation Avanzado - M11.json", "SUPERVISOR_Judge (M11).json"…). El contenido ya está al día. No forman parte de la entrega, que es solo el PDF.
3. El usuario sube la entrega antes del 13/11/2026 a las 20:59.

## Recursos clave
- **Ids**:
  - workflows: `Avanzado/Modulo11/_ids_m11.json` (claves: manager, receptor, canal_telegram, juez, escalado_humano, respuesta_voz, etc.);
  - Data Tables y credenciales: `Avanzado/Modulo11/_aux_m11.json`.
- **Secretos**: están en `Avanzado/Modulo5/scripts/.env`, fuera de git. Ahí están la API key de n8n, NGROK_AUTHTOKEN, NGROK_DOMAIN, FRENO_TOKEN y QDRANT_COLLECTION.
- **Planillas y bases**: Agenda_Turnos `19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk`, QA_Veredictos `1IYqouMdEh8s0ecJEdDMWjtObglgDA1Nd8E84nWdSEQk` y la tabla de Airtable Memoria_Pacientes `tblaIZxUOLY1T8g40`.
- **Drive**:
  - carpeta "Trabajo Final" `15y6JMd_aVrDFc_hL_yMcVolUFcXkUcV7`, con "Del Profe", la consigna y la teoría;
  - doc de Devoluciones `1PagfRWzjIB3s697JLFEM3PI9-Ui-D74KT0F7Q3XR8hg`.
- **Evaluación**:
  - `Avanzado/Modulo11/evaluacion/`: `bateria_A`…`D.json`, `comparacion_modelos.md` y `finanzas.json`;
  - `scripts/finanzas.py` recalcula el ROI.
- **DMSA**: `Avanzado/Modulo11/DMSA/`:
  - `Seccion1` a `4` y `AnexoA` a `C`;
  - `estructura.md`;
  - `evidencias/`: los ejemplos del Juez;
  - `capturas/`.
