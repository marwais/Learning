# Módulo 6 — Voice AI y Agentes Conversacionales

Sexta etapa del proyecto integrador **AgendaBot** (curso AI Automation Avanzado, Coderhouse). Este módulo **parte de cómo quedó el Módulo 5** (multi-agente + memoria + integraciones + RAG con validador) y le suma la **capa de voz**: el paciente manda una nota de voz por Telegram, Whisper la transcribe, el Manager la resuelve como siempre y ElevenLabs le devuelve la respuesta en audio.

> Resumen de la clase 6 (29/09, 2h22m) → [`resumen-clase.md`](resumen-clase.md).

## Estado
- [x] Consigna y material de la unidad relevados.
- [x] Túnel HTTPS para el webhook de Telegram: contenedor `cloudflared` (quick tunnel, la URL cambia en cada reinicio).
  Script: [`scripts/levantar_tunel.ps1`](scripts/levantar_tunel.ps1) (reinicia el túnel y recrea n8n con `WEBHOOK_URL` = URL nueva).
- [x] Nodo de ElevenLabs: paquete oficial `@elevenlabs/n8n-nodes-elevenlabs@0.2.4` instalado en `~/.n8n/nodes` con `--ignore-scripts` (la dependencia `isolated-vm` no compila en la imagen y no hace falta). Text to Speech: modelo `eleven_multilingual_v2`; Stability y Clarity van en el JSON `voiceSettings` (`stability`, `similarity_boost`), no como sliders.
- [x] Recursos 06: carpeta Drive `Entregas/06` (`1ss0I2z38rS36oC3c-yljB7F7YkXuBswH`), planilla `Agenda_Turnos (06)` (`1ite0UG7EYZBk4XCSDZN3GTXeRv6UkzZQhyPei2vc_D0`, copia de la 05 con sus turnos), tabla Airtable `Memoria_M6` (`tblk6hJg3wq5UG0Ur`).
- [x] Credenciales: Telegram, OpenAI y ElevenLabs (cargadas por el usuario en n8n).
- [x] M5 duplicado a M6 por API (`_ids_m6.json`): Manager `7ml1Rhe3miNhD1bK`, Worker1..4 y Tool_ConsultarConocimiento (M6), publicados; apuntan a `Agenda_Turnos (06)` y `Memoria_M6`. La colección Qdrant sigue siendo `kb_lodetincho_m5` (mismo conocimiento). Regresión por chat OK (ejecución #294).
- [x] Rama de voz en el Manager M6: [`scripts/agregar_voz.py`](scripts/agregar_voz.py) (idempotente). Mientras falte una credencial, sus nodos quedan desactivados para no frenar el chat. `--keep-executions` para depurar; sin ese flag aplica los settings de compliance.
- [x] Pruebas de punta a punta con notas de voz reales (turno, RAG, fuera de alcance, silencio). Ajustes que salieron de las pruebas: alucinación de Whisper ante silencio, email dictado → por escrito, filtro de `update_id` repetidos, "Listo." → mensaje de fuera de alcance, System Message del Router como expresión.
- [x] Compliance aplicado (settings sin guardar ejecuciones) y verificado con una ejecución de chat.
- [x] Pre-entrega: [`PreEntrega/PreEntrega_Modulo6_JulioMartinWaisburd.pdf`](PreEntrega/PreEntrega_Modulo6_JulioMartinWaisburd.pdf) (20 págs.), generado con `PreEntrega/build_pdf.py` desde `Pieza1..9_*.md` y `capturas/`. **Subido a la plataforma el 11/10/2026.**
- [ ] Pendientes: probar en vivo el pedido de email por escrito; bajar la latencia (18–21 s) mandando el audio antes de logs y memoria.

## Diseño de la rama de voz (Manager M6)
```
Telegram Trigger (message) ─► ¿trae voz? ─no─► (texto: entra igual al Manager)
                                   │ sí
                                   ▼
                    Telegram: Get File (binario "data")
                                   ▼
                    OpenAI Whisper: Transcribe (binary "data", language "es")
                                   ▼
                    IF transcripción vacía o < 3 caracteres ─sí─► Telegram: texto "no te escuché bien"
                                   │ no
                                   ▼
                    Normalizar entrada → Router (AI Agent, Tools Agent) → workers / Agente RAG → validador
                                   ▼
                    Respuesta final (System Prompt: máx. 200 caracteres, sin URLs ni emojis)
                                   ▼
                    ElevenLabs: Text to Speech (Eleven Multilingual v2, Stability ~55%, Clarity ~75%)
                                   ▼
                    Telegram: Send Audio/Voice (binario de ElevenLabs)
```
- **Compliance:** el audio vive solo en la memoria de la ejecución (binary mode `default`, sin guardar en disco ni en Drive); el workflow no guarda los datos de ejecuciones exitosas y un nodo final descarta el binario. Se documenta en el lienzo con una nota.
- **Voz de soporte** (guía de la unidad 2): estabilidad media, tono cálido para una clínica.

## Consigna oficial (Pre-entrega 6: Ensamblado de Circuito Cerrado Conversacional de Voz)
Entregable: **PDF con screenshots** de la configuración visual del circuito en n8n. Componentes obligatorios en el lienzo:
1. **Trigger** de mensajería (Telegram o WhatsApp) que reciba notas de voz (payload binario).
2. **OpenAI Whisper** inmediatamente después: *Input Binary Property* = `data` e idioma `es`.
3. **AI Agent** en modo *Tools Agent* que recibe el texto transcrito.
4. **System Prompt** con la regla explícita de **máximo 200 caracteres** por respuesta.
5. **ElevenLabs**: modelo *Eleven Multilingual* + sliders *Stability* y *Clarity* según la identidad de marca.
6. **Salida** del canal con *Send Voice* / *Send Audio* usando el binario de ElevenLabs.
7. **Contingencia** con *IF* o *Switch* ante audios corruptos o transcripciones vacías.
8. **Compliance**: procesar los audios en memoria volátil y destruirlos al cerrar el flujo.

Plazo: **13/10/2026 21:00** (junto con las Pre-entregas 7 y 8).
