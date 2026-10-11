# 1. Viabilidad de la voz en AgendaBot (ROI y fatiga cognitiva)

**Diagnóstico:** la voz conviene en AgendaBot para pedidos **cortos y de manos libres** (sacar, confirmar o consultar un turno; una pregunta frecuente) y **no** conviene cuando el paciente necesita ver o releer datos (listas largas, emails, números). Por eso la capa de voz responde con audio solo lo breve y deja lo largo o lo exacto por escrito.

| Proceso de AgendaBot | ¿Voz? | Por qué |
|---|---|---|
| Sacar o reprogramar un turno ("agendame una tomografía el 11 a las 21:30") | **Sí** | Una frase de 5–8 s reemplaza varios mensajes tipeados; la confirmación entra en un audio de ~6 s. |
| Consultar el propio turno o una pregunta frecuente | **Sí** | Respuesta de una o dos oraciones: el caso de uso de alto retorno de la unidad. |
| Listado completo de profesionales (8 nombres en Cardiología + Infantil) | **No** | Escuchar ocho nombres genera fatiga cognitiva; el audio da los primeros y el resto va por texto. |
| Dictar un email | **No** | Whisper lo transcribe mal (ver pieza 6): se pide por escrito. |
| Pregunta fuera de alcance (dólar, trámites) | Audio corto | Una frase fija de límite honesto (106 caracteres). |

**Costo por interacción** (`Costo = Whisper (min) + LLM (tokens) + ElevenLabs (caracteres)`), medido en las pruebas:

| Componente | Unidad | Medido en las pruebas | Contención aplicada |
|---|---|---|---|
| OpenAI Whisper | minuto de audio | notas de 3–8 s (≈ US$ 0,0003–0,0008 a US$ 0,006/min) | idioma fijo `es` (no detecta idioma) |
| Claude (Router + Agente RAG + validador) | tokens | ~6.700 tokens en una consulta INFO | prompts acotados; mismo pipeline que el M5 |
| ElevenLabs | carácter sintetizado | 87–134 caracteres por respuesta | **tope de 200 caracteres** (prompt + código), sin citas, URLs ni emojis |

El componente que más crece con el uso es ElevenLabs: sin el tope, una respuesta de texto del M5 (lista de profesionales con citas) supera los 600 caracteres; con el tope queda en ~130, es decir, **un ahorro de más del 75 % por respuesta hablada**.
