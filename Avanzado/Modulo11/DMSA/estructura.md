# Estructura del DMSA (propuesta, para aprobar antes de redactar)

**Archivo:** `Waisburd_JulioMartin_ProyectoFinal_AI_Experto.pdf` · **Extensión objetivo:** 14 a 18 páginas más anexos (límite de la plataforma: 10 MB).
**Título:** *AgendaBot: Central de Turnos agéntica para la Clínica LoDeTincho. Documentación Maestra del Sistema Agéntico (DMSA)*. Autor: Julio Martín Waisburd · Cohorte 2026 · AI Automation Avanzado (Coderhouse).

**Criterios de redacción**, que salen de la consigna y de las devoluciones:
- Tono de comité ejecutivo: impacto, riesgo y control. Lo técnico va a los anexos.
- Cada número va rotulado como **medido en pruebas** o **proyección mensual** (P7 d, P9 a).
- `traceId` siempre en tipografía de código, donde la I mayúscula no se confunde con la l (P9 b).
- Sin "código personalizado" ni "low-code" (P7 a): las decisiones se explican sobre los nodos visuales.
- Capturas recortadas por etapa y numeradas (P8 b), y fórmulas de costo con valores sin redondear (P8 a).
- Ninguna clave ni token real. Se documentan los nombres de las variables y de las credenciales, nunca sus valores.

---

## Sección 1. Portada y resumen ejecutivo (2 págs.)
- **Portada:** título, autor, cohorte 2026, fecha e índice con links a cada página.
- **Resumen ejecutivo (1 pág.):**
  - el problema real, con el baseline (250 gestiones por día, 236 h/mes de trabajo repetitivo, 6 min de espera en los picos, 1 de cada 5 contactos fuera de horario sin respuesta, 5 % de turnos con errores; supuestos declarados);
  - la solución en una frase y qué hace (4 canales, Juez antes de escribir, personas en Slack, CRM como fuente de verdad);
  - **resultados medidos** frente a la **proyección**;
  - el ROI en una línea;
  - los 3 riesgos principales con su control.
- **Cuadro "criterio de aceptación → evidencia → página"** con los 6 criterios de la consigna, para que el corrector encuentre cada uno.

## Sección 2. Arquitectura en n8n (5 a 6 págs.)
1. **Mapa del ecosistema** (diagrama propio):
   - canales (Receptor por webhook, Canal Telegram, Gmail, chat) → Manager → Workers 1 a 4, herramienta RAG, Juez, Escalado humano, Respuesta de voz, Errores, Freno de mano;
   - herramientas: agenda (Sheets), memoria (Airtable), base de conocimiento (Qdrant), CRM (HubSpot), Slack, Gmail, Telegram y Data Tables;
   - **correlación del `traceId`**: por dónde viaja y dónde queda registrado.
2. **El recorrido de un pedido en 10 etapas**: captura general y capturas por etapa (la 5 y la 7 en dos partes), con 2 o 3 líneas de negocio cada una.
3. **Asincronía e idempotencia:** Receptor (202 en ~0,2 s, 200 "duplicado", 400), Data Table `pedidos_procesados_m11`, *append or update* en la agenda y *upsert* en HubSpot. Evidencia: tabla de pruebas con el `traceId` por fila (P8 c).
4. **Memoria persistente y acople contextual:**
   - campos de Airtable `Memoria_M11`, memoria de sesión y resumen cada 5 mensajes;
   - el **recorrido numerado de la memoria** (P3);
   - **tabla de contratos JSON** por sub-workflow: entrada obligatoria, tipos, salida `{traceId, status, data, error}`, errores y destinatario (P7 b).
5. **Robustez y ramas de error:** Errores (M11) con alerta en castellano, reintentos, rama de error del log, aviso de demoras y simulacro. Incluye las **fallas reales que ocurrieron en las pruebas** y cómo respondió el sistema: credencial de Gmail vencida, saldo de la API agotado y caídas del túnel.
6. **Base de conocimiento con disciplina:** cuadro de equivalencia con el *Vector Store Retrieve Tool* nativo (Top-K 5 y Min Score 0,60, que el nodo nativo no trae), citas con metadatos reales y «No sé» (P5).

## Sección 3. Auditoría y rúbricas (3 a 4 págs.)
1. **Cómo funciona el supervisor:**
   - dos tipos de caso (respuesta informativa y acción a escribir) y la rúbrica `exactitud_factual` de 1 a 5;
   - los estados, el **umbral de 4** y las rutas: aceptar; corregir hasta 2 veces; escalar a Slack, o, en una acción, congelarla con aprobación en Slack y 15 minutos de espera;
   - objetividad, versión del prompt (`juez-rubrica-v3.1` con su sha256) y log de auditoría con datos personales enmascarados.
2. **La frontera de la autonomía** (P7 c): qué resuelve solo el sistema y qué pasa siempre por una persona (semáforo y triaje).
3. **Tres ejemplos reales en JSON plano** (los pide la consigna). Cada uno con el pedido, el fragmento recuperado textual (P5), el JSON del veredicto y qué pasó después:
   - a) nota de voz con email sin @ → acción congelada, CORREGIR 2/5;
   - b) "¿tiene estacionamiento?" → «No sé», ACEPTADO 5/5;
   - c) alta con fecha pasada → CORREGIR 2/5, o alta correcta → ACEPTADO.
4. **Métricas de precisión obtenidas en pruebas:** aciertos del Juez frente a la respuesta esperada, casos rojos detectados por el triaje, duplicados bloqueados y falsos positivos. *Requiere la batería de evaluación (ver decisión 2).*

## Sección 4. Justificación financiera (2 a 3 págs.)
1. **Baseline manual por tarea** (volumen, minutos, horas), con los supuestos declarados (del M9).
2. **Costo en tokens con la fórmula exacta** (P8 a): costo por llamada = (tokens de entrada × precio de entrada + tokens de salida × precio de salida) / 1.000.000.
   - Tokens **medidos en el M11** por tipo de pedido, incluido el Juez de acciones, que es nuevo respecto del M9.
   - Valores sin redondear, costo por pedido y cada 1.000, y mensual = volumen × costo.
3. **Optimización con modelos económicos** (lo pide la consigna): configuración actual (Sonnet 4.6) frente a la optimizada (Haiku 4.5 donde no se pierde calidad).
4. **Costo total de operación** (APIs, capas gratuitas y mantenimiento) frente a la labor evitada: ROI, recupero y tres escenarios. Separando siempre lo **medido** de lo **proyectado** (P9 a).
5. **Riesgos de costo y mantenimiento:** saldo prepago de la API (ocurrió y el sistema lo alertó) y la baja de la API de HubSpot después de septiembre de 2027.

## Anexos
- **A. Gobernanza de datos:**
  - variables de entorno (solo nombres) y credenciales de n8n (solo nombres);
  - estructuras de tablas: agenda, memoria, veredictos, Data Tables y propiedades de HubSpot;
  - parámetros de conexión;
  - **tabla por proveedor**: desarrollo hoy / requisito para producción / alternativa empresarial (P9 c);
  - privacidad: audios purgados y verificados (P6), enmascarado y base anonimizada.
- **B. Pruebas de punta a punta:** una tabla con el `traceId` por fila.
- **C. Inventario de workflows y operación:** ids, función, cómo levantar el sistema (ngrok, `activar_aqui.ps1`) y el video opcional.

---

## Decisiones pendientes del usuario
1. **Modelos económicos.** ¿Pasar de verdad el **Router a Haiku 4.5**, o mostrarlo solo como escenario? El Router clasifica y extrae datos, una tarea simple. El RAG y el Juez quedarían en Sonnet por calidad. Recomendación: medir los dos con la batería y decidir con datos, como en el A/B del M8.
2. **Batería de evaluación.** Unos 15 casos con resultado esperado (consultas, altas, cambios, datos faltantes, casos rojos, duplicados, fuera de alcance) para la Sección 3.4 y la tabla del Anexo B. Costo estimado: menos de US$ 1 en tokens.
3. **Video opcional de 3 minutos.** ¿Lo grabás vos (en el anexo C va el guion)?
