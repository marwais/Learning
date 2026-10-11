# Módulo 6 — Voice AI y Agentes Conversacionales

**Curso:** AI Automation Avanzado (Coderhouse) · **Clase en vivo:** 29/09/2026, 2h 22m (142 min)
**Deck:** "Clase 6 _ AI Automation Avanzado V2" (Google Slides, ~35 slides; en clase se mostraron pocos)
**Material de la unidad:** documento "Módulo 6" en Drive (6 unidades).

> Barrido hecho por cuadros (cada 2–4 minutos). Claude ve slides y demos, **no el audio**: lo que dijo el docente sobre cada slide no está acá.

---

## Resumen

El M6 le da al agente **oídos y voz**: entra una nota de voz, **Whisper** (STT) la pasa a texto, el agente razona como siempre (con RAG si hace falta) y **ElevenLabs** (TTS) devuelve la respuesta en audio por el mismo canal. La idea que ordena el módulo es de **criterio**, no de técnica: la voz conviene en **respuestas cortas y manos libres** (confirmar un turno, un estado, una consulta frecuente) y es **sobreingeniería** cuando el usuario necesita ver o releer datos (listas, tablas, números).

Tres reglas atraviesan todo: **brevedad** (máximo 200 caracteres por respuesta, porque ElevenLabs cobra por carácter y el audio largo abruma), **contingencia** (un IF después de Whisper para audios vacíos o ruidosos) y **privacidad** (el audio del cliente se procesa en memoria y se destruye).

---

## Recorrido de la clase

| Min | Tema | Tipo |
|----:|------|------|
| 00–15 | Apertura (cámara apagada) | — |
| 16–25 | **Objetivos**: cuándo la voz agrega valor; Whisper (STT) y sus límites; ElevenLabs (TTS) controlando costo; circuito cerrado en n8n; diseño VUI por canal y con contingencias | slide |
| 28–48 | **¿Por qué la voz? Tres fricciones**: accesibilidad (campo, calle, quien no puede tipear), velocidad (hablamos ~150 palabras/min, tipeamos ~40 en el celular), naturalidad (apretar un botón y hablar) | slide |
| 52–68 | **Para pensar**: el error común es ponerle voz a todo. ¿Respuesta corta y manos libres, o el usuario necesita ver y releer? Esa pregunta separa alto retorno de sobreingeniería | slide |
| 70 · 98 · 142 | **¿Cómo continúa el proyecto?** (slide 35, vuelve a aparecer varias veces en el editor de Slides) Puente al M7: ya tenés un agente que escucha, razona y responde con voz; el M7 lo especializa por industria | slide |
| 72–86 | **Principios VUI** — diseñar para el oído: claridad, brevedad, tono según empresa y canal, límites honestos ("no entendí" en vez de inventar) | slide |
| 88–96 | Pausa (cámara apagada) | — |
| 100–116 | **ElevenLabs** en la web: Texto a voz, selección de voz, modelo, generar | demo |
| 118–142 | **Demo n8n "TEST CLASE 6"** (n8n expuesto con un túnel trycloudflare): circuito completo de Telegram | demo |

### La demo de n8n (TEST CLASE 6)
```
Mensaje nuevo (Telegram Trigger, updates: message)
 → Obtener el archivo de audio (Telegram, get: file)
 → Transcribir el audio (OpenAI, Transcribe Recording)
 → Agente de respuesta (AI Agent + OpenAI Chat Model)
 → Convertir texto a voz (ElevenLabs, textToSpeech: speech)
 → Cambiar el nombre y agregar la fecha (Code: renombra el binario)
 → Enviar un archivo de audio (Telegram, sendAudio)
```
Pestañas abiertas del docente: ElevenLabs "De texto a voz", BotFather (creación del bot) y un bot "Voice-AI". El trigger quedó en *Waiting for trigger event* hasta el final del video.

---

## Lo que aporta el material de la unidad (no visto en la grabación)
- **Matriz de viabilidad:** sí a interacciones cortas (turnos, estados, alertas), formatos ejecutivos y FAQ de menos de 30 s de audio; no a balances, contratos, tablas o análisis que requieren releer.
- **ElevenLabs:** modelo *Eleven Multilingual*; *Stability* 0–100% (bajo = expresivo, alto = uniforme); *Clarity/Similarity*. Guía: institucional 75–85%, **soporte 50–60%** (tono cálido), notificaciones alta.
- **Costos:** Whisper ~US$0,006/min; LLM por tokens; **ElevenLabs por carácter** (el más caro) → prompt con tope de 200 caracteres y sin saludos, firmas ni URLs.
- **Whisper:** *Input Binary Property* `data` + idioma `es`. Límites: ruido extremo, acentos muy marcados, varios hablantes a la vez (no separa quién habla).
- **Contingencia:** IF después de Whisper → texto vacío o < 3 caracteres → mensaje "no logré escuchar tu audio con claridad…".
- **Salida por formato:** audio corto → nota de voz; listas o números → texto; alerta crítica → texto + audio.
- **Canales:** WhatsApp 20–30 s por audio, tono empático; Telegram hasta 45 s, ágil. Telegram se arma en 2 minutos con @BotFather.
- **Personalidad hablada en el prompt:** frases simples (sujeto + verbo + predicado), puntos seguidos para forzar pausas, **prohibido** URLs, viñetas y emojis.
- **Testing:** *Listen for test event* → nota de voz real con una pregunta que use el RAG → latencia objetivo 6–8 s. Prueba ciega con 2–3 usuarios.
