# Contexto: curso cerrado, Proyecto Final AgendaBot completado

Último guardado: **2026-10-20**, en `main`.

**El curso "AI Automation Avanzado" está terminado.** El usuario dio por completados el M11 (Proyecto Final) y su entrega el 20/10/2026. M1 a M10 ya estaban entregados.

El detalle técnico y las pruebas están en `Avanzado/Modulo11/README.md`. Las devoluciones de P1 a P10 y su impacto están en `Avanzado/Modulo11/devoluciones.md`.

## Estado final
- **Componente A (n8n)**: en producción en LOBO, con 15 workflows "AgendaBot · …", todos publicados salvo Ingesta KB, que es manual.
  - **Exportaciones**: `Avanzado/Modulo11/workflows/AgendaBot · <nombre>.json`, al día al 20/10. Los scripts exportan ahí.
  - **Asincronía e idempotencia**:
    - el Receptor (`POST /webhook/agendabot`) responde 202 con traceId, 200 si es duplicado y 400 si es inválido;
    - la idempotencia vive en la Data Table `pedidos_procesados`.
  - **Supervisión**:
    - el Juez revisa respuestas y acciones antes de consolidar; si duda, congela la acción en Slack;
    - los emails quedan como borrador (HITL).
  - **Seguridad y operación**:
    - triaje rojo y escalado humano por Slack, con respuesta al paciente por su canal;
    - freno de mano (`/webhook/freno-de-mano`, con token);
    - Error Workflow con alertas en castellano y aviso de demora al paciente;
    - dos fallas de comprensión pasan a una persona.
  - **Memoria (Airtable `Memoria_Pacientes`)**: el *Estado del Caso* se calcula según el resultado: Cerrado, Pendiente (faltan datos) o En Revisión (congelada o derivada). La ruta de consultas también actualiza la memoria.
  - **Filtro de Gmail**: frena auto-replies, rebotes (mailer-daemon, postmaster) y los correos del propio sistema.
  - **Log del Juez (QA_Veredictos)**:
    - enmascara nombre, email, CUIL, DNI y teléfono;
    - conserva el CUIT de la clínica y los códigos de turno.
  - **Modelos (configuración C)**: Router y Agente RAG en `claude-haiku-4-5-20251001`, Juez en `claude-sonnet-4-6`.
  - **Batería de 16 casos**: las corridas A, B, C, E, F y G dieron 16/16; la D falló por la credencial de Sheets vencida. Cuesta US$ 0,0166 por consulta y US$ 0,0092 por acción.
- **Componente B (DMSA)**: `Avanzado/Modulo11/DMSA/Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf`.
  - Tiene 35 páginas: 4 secciones y los anexos A (gobernanza), B (pruebas y evidencias) y C (inventario de workflows con capturas).
  - No tiene video ni "Cómo se levanta el sistema", y no hace referencias a módulos, pre-entregas ni devoluciones.
  - **Finanzas, escenario base**: costo de US$ 127,91 por mes (unos $339.079), beneficio neto de $1.493.521, retorno de 4,40 y recupero en 1,07 meses.

## Decisiones
- **Decisiones del usuario**:
  - **No-Code híbrido**: no se migraron los 32 nodos Code heredados; lo nuevo se hizo con nodos visuales.
    - Se descartó migrarlo todo por costo y riesgo, con poca ganancia en la rúbrica.
    - En el DMSA no se dice "low-code" ni "código personalizado".
  - **Router y RAG en Haiku, Juez en Sonnet**: la calidad es igual (16/16) y los tokens bajan de US$ 105,66 a US$ 59,91 por mes.
  - **Nombres de producción sin sufijos del curso**: rompe a propósito la convención de duplicar cada módulo.
  - **El documento final se sostiene solo**: sin referencias a módulos, pre-entregas ni devoluciones. El criterio: "lo que no está en este documento, no está".
  - **Sin video** (20/10). El guion quedó en `DMSA/guion_video.md`, con Carlos Demo, por si se retoma.
  - **Sin C.2 "Cómo se levanta el sistema"** (20/10): la consigna no lo pide.
  - **Sin comando `/nueva`** para separar sesiones de Telegram: Claude lo propuso y el usuario lo descartó.
- **Decisiones técnicas**:
  - **Túnel por ngrok con dominio fijo**: el quick tunnel de Cloudflare se caía con cada corte de red y la red pública bloquea el puerto 7844.
  - **Idempotencia en el Receptor y en las Data Tables**: el staticData del Manager se guarda recién al terminar la ejecución.
  - **Escalados en serie**: en una rama paralela no se ejecutaban.

## Restricciones y gotchas
- **Credenciales de Google**: vencen cada 7 días (cliente OAuth en modo Testing). Si el sistema se vuelve a usar, hay que reconectar "Gmail account" y "Google Sheets account" desde `localhost:5678`.
- **Túnel**: si el dominio de ngrok da ERR_NGROK_3200, se corre `Avanzado\scripts\levantar_ngrok.ps1`.
- **Credenciales renombradas**: la API no permite renombrarlas, así que se crearon nuevas ("n8n API (alertas)", "Freno de mano"). Las viejas pueden borrarse a mano.
- **Voz**: ElevenLabs con estabilidad 0,8; con menos, salían voces distintas.
- **PDF abierto**: si el usuario tiene el PDF abierto, `build_pdf.py` no lo puede regenerar.
- **Vista previa del PDF**: en esta PC no hay con qué convertir el PDF a imagen (ni poppler `pdftoppm` ni PyMuPDF), así que la diagramación la revisa el usuario.
- **Restos de prueba**: el contacto `prueba.m11@example.com` en HubSpot y borradores en Gmail.

## Pendientes
No queda nada obligatorio.

Opcionales:
- **Limpieza (usuario)**: borrar las credenciales viejas de n8n, el contacto de prueba en HubSpot y los borradores de prueba.
- **Apagar el sistema si no se va a usar**: desactivar los workflows con disparadores externos y detener ngrok. Mientras esté activo, cada mensaje que llegue por Telegram o Gmail consume tokens de Anthropic.

## Recursos clave
- **Ids**:
  - workflows: `Avanzado/Modulo11/_ids_m11.json`;
  - Data Tables, credenciales e Ingesta KB: `Avanzado/Modulo11/_aux_m11.json`.
- **Secretos**: `Avanzado/Modulo5/scripts/.env`, fuera de git. Tiene la API key de n8n, NGROK_AUTHTOKEN, NGROK_DOMAIN, FRENO_TOKEN y QDRANT_COLLECTION.
- **Planillas y bases**: Agenda_Turnos `19rWr4cy1pVmiDi5iv3Nkr3gZn4ExF12Ep5OkMrxxaWk`, QA_Veredictos `1IYqouMdEh8s0ecJEdDMWjtObglgDA1Nd8E84nWdSEQk` y la tabla de Airtable Memoria_Pacientes `tblaIZxUOLY1T8g40`.
- **Drive**:
  - "Trabajo Final" `15y6JMd_aVrDFc_hL_yMcVolUFcXkUcV7`: "Del Profe", consigna y teoría;
  - Devoluciones `1PagfRWzjIB3s697JLFEM3PI9-Ui-D74KT0F7Q3XR8hg`;
  - "En varias PCs" `12CcvC0bxGISg2fneCMZkWiriGYg35FHw`: doc de traspaso y `memoria-claude`.
- **Evaluación**: `Avanzado/Modulo11/evaluacion/` tiene `bateria_A` a `G`, `comparacion_modelos.md` y `finanzas.json`. `scripts/finanzas.py` recalcula el ROI.
- **DMSA**: `Avanzado/Modulo11/DMSA/`:
  - `Seccion1` a `4` y `AnexoA` a `C`;
  - `build_pdf.py`;
  - `capturas/` y `evidencias/` (los ejemplos del Juez).
