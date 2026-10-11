# 9. Anexo: configuración exportada en formato texto

Extracto del workflow exportado de n8n (`AI Automation Avanzado - M6.json`): los nodos de la capa de voz con su tipo y parámetros, más los *settings* del workflow. El JSON completo (82 nodos) y los de los sub-workflows están versionados en el repositorio del proyecto (`Avanzado/Modulo6/`). Las credenciales solo aparecen por nombre: los secretos quedan cifrados en n8n.

## Settings del workflow
```json
{
  "executionOrder": "v1",
  "binaryMode": "separate",
  "saveExecutionProgress": false,
  "saveManualExecutions": false,
  "saveDataErrorExecution": "none",
  "saveDataSuccessExecution": "none"
}
```

## Mensaje de Telegram
```json
{
  "type": "n8n-nodes-base.telegramTrigger",
  "typeVersion": 1.2,
  "parameters": {
    "updates": [
      "message"
    ],
    "additionalFields": {}
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```

## Filtrar repetidos
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "jsCode": "// Telegram reintenta la entrega si el webhook tarda en responder: el mismo update llega varias veces.\n// Se procesa cada update_id una sola vez (memoria del workflow; persiste con el workflow publicado).\nconst s = $getWorkflowStaticData('global');\ns.vistos = s.vistos || [];\nconst id = $json.update_id;\nif (s.vistos.includes(id)) return [];\ns.vistos.push(id);\ns.vistos = s.vistos.slice(-200);\nreturn [$input.first()];"
  }
}
```

## ¿Nota de voz?
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "loose",
        "version": 1
      },
      "conditions": [
        {
          "id": "7fab2622-31e3-4a28-9cc8-3a38ac1f1e85",
          "leftValue": "={{ $json.message.voice || $json.message.audio ? 'si' : 'no' }}",
          "operator": {
            "type": "string",
            "operation": "equals"
          },
          "rightValue": "si"
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Descargar nota de voz
```json
{
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "resource": "file",
    "fileId": "={{ $json.message.voice ? $json.message.voice.file_id : $json.message.audio.file_id }}",
    "additionalFields": {}
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```

## Transcribir (Whisper)
```json
{
  "type": "@n8n/n8n-nodes-langchain.openAi",
  "typeVersion": 2.3,
  "parameters": {
    "resource": "audio",
    "operation": "transcribe",
    "binaryPropertyName": "data",
    "options": {
      "language": "es",
      "temperature": 0
    }
  },
  "credentials": {
    "openAiApi": "OpenAI account"
  }
}
```

## Evaluar transcripción
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "jsCode": "// Contingencia de audio: Whisper no devuelve vacío ante silencio o ruido, ALUCINA frases de subtítulos\n// (p. ej. \"Subtítulos realizados por la comunidad de Amara.org\"). Se marca como ilegible:\n// texto vacío o < 3 letras, solo signos, o una frase alucinada conocida.\nconst texto = String($json.text || '').trim();\nconst letras = texto.replace(/[^\\p{L}\\p{N}]/gu, '');\nconst ALUCINACIONES = [\n  /amara\\.org/i, /subt[ií]tulos (realizados|hechos|por)/i, /gracias por ver/i, /suscr[ií]bete/i,\n  /^\\W*(m[uú]sica|aplausos|risas|silencio)\\W*$/i, /^\\W*gracias\\.?\\W*$/i, /www\\.\\S+/i\n];\nconst alucinada = ALUCINACIONES.some(r => r.test(texto));\nconst ilegible = letras.length < 3 || alucinada;\n// Un email dictado por voz se transcribe mal (\"mwhisbord arroba gmail punto com\"): se pide por escrito.\nconst dicta_email = !ilegible && (/\\barroba\\b/i.test(texto) || /@/.test(texto) || /punto\\s*com\\b/i.test(texto));\nreturn [{ json: { ...$json, text: texto, ilegible, motivo_ilegible: ilegible ? (alucinada ? 'alucinación de Whisper' : 'audio vacío') : '', dicta_email } }];"
  }
}
```

## ¿Audio vacío o ilegible?
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "loose",
        "version": 1
      },
      "conditions": [
        {
          "id": "af5c353f-69e8-4678-8a37-72a6160e1abc",
          "leftValue": "={{ $json.ilegible }}",
          "operator": {
            "type": "boolean",
            "operation": "true",
            "singleValue": true
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Avisar: no se escuchó
```json
{
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "chatId": "={{ $('Mensaje de Telegram').first().json.message.chat.id }}",
    "text": "Perdón, no logré escuchar tu audio con claridad. ¿Podés grabarlo de nuevo en un lugar con menos ruido, o escribirme tu consulta?",
    "additionalFields": {
      "appendAttribution": false
    }
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```

## ¿Dictó un email?
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "loose",
        "version": 1
      },
      "conditions": [
        {
          "id": "f9cbc31f-3c9b-4794-bbac-8caba8c46e00",
          "leftValue": "={{ $json.dicta_email }}",
          "operator": {
            "type": "boolean",
            "operation": "true",
            "singleValue": true
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Pedir email por escrito
```json
{
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "chatId": "={{ $('Mensaje de Telegram').first().json.message.chat.id }}",
    "text": "Para no anotar mal tu email, ¿me lo escribís por texto? Por audio se confunden letras.",
    "additionalFields": {
      "appendAttribution": false
    }
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```

## Entrada Telegram
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "jsCode": "// Une las dos ramas de Telegram (voz transcrita o texto) en el formato del Manager.\nconst t = $('Mensaje de Telegram').first().json.message || {};\nconst esVoz = !!(t.voice || t.audio);\nconst texto = esVoz ? String($json.text || '').trim() : String(t.text || '').trim();\nreturn [{ json: {\n  canal: esVoz ? 'telegram_voz' : 'telegram_texto',\n  sessionId: 'tg-' + t.chat.id,\n  tg_chat_id: t.chat.id,\n  mensaje: texto,\n  nombre_remitente: [t.from?.first_name, t.from?.last_name].filter(Boolean).join(' ')\n} }];"
  }
}
```

## ¿Vino por Telegram?
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "loose",
        "version": 1
      },
      "conditions": [
        {
          "id": "e671822e-eb15-4f8e-9d9d-08f07280baeb",
          "leftValue": "={{ $('Normalizar entrada').first().json.canal }}",
          "operator": {
            "type": "string",
            "operation": "startsWith"
          },
          "rightValue": "telegram"
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Preparar respuesta hablada
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "jsCode": "// Respuesta para el canal de voz: sin citas, links, emojis ni markdown, y como máximo 200 caracteres\n// (ElevenLabs cobra por carácter; la regla también está en el System Prompt del Agente RAG).\nconst MAX = 200;\nconst original = String($json.output || '');\nlet t = original\n  .replace(/\\[Fuente:[^\\]]*\\]/gi, '')          // citas de fuente (quedan en el texto, no en el audio)\n  .replace(/https?:\\/\\/\\S+/g, '')              // URLs\n  .replace(/[*_`#>]/g, '')                     // markdown\n  .replace(/^\\s*[-•]\\s+/gm, '')                // viñetas\n  .replace(/[\\u{1F300}-\\u{1FAFF}\\u{2600}-\\u{27BF}\\u{FE0F}]/gu, '') // emojis\n  .split(/\\s*\\n+\\s*/).map(s => s.trim()).filter(Boolean)\n  // cada línea se une como frase: si no termina en signo, se le agrega un punto (\"atienden:\" -> \"atienden:\")\n  .map(s => /[.?!:;,]$/.test(s) ? s : s + '.').join(' ')\n  .replace(/\\s{2,}/g, ' ').trim();\nif (t.length > MAX) {\n  // cortar en el último fin de oración (. ? !) que entre en 200; si no hay, en la última palabra\n  const corte = t.slice(0, MAX + 1);\n  // fines de oración reales: no cuentan las abreviaturas (Dr., Dra., Sr., Sra., Lic., etc.)\n  let fin = -1;\n  for (const m of corte.matchAll(/[.?!](?=\\s|$)/g)) {\n    const previa = corte.slice(0, m.index).split(/\\s/).pop();\n    if (m[0] === '.' && /^(Dr|Dra|Sr|Sra|Lic|Dres|Av|Nro|Ing)$/i.test(previa)) continue;\n    fin = m.index;\n  }\n  t = (fin > 60 ? corte.slice(0, fin + 1) : corte.slice(0, corte.lastIndexOf(' ')) + '…').trim();\n}\nconst n = $('Normalizar entrada').first().json;\nreturn [{ json: { texto_voz: t, caracteres: t.length, texto_completo: original, canal: n.canal, tg_chat_id: n.tg_chat_id } }];"
  }
}
```

## ¿Responder con voz?
```json
{
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "loose",
        "version": 1
      },
      "conditions": [
        {
          "id": "31b9608a-f820-4d90-90d0-92cec23f7f2b",
          "leftValue": "={{ $json.canal }}",
          "operator": {
            "type": "string",
            "operation": "equals"
          },
          "rightValue": "telegram_voz"
        }
      ],
      "combinator": "and"
    },
    "options": {}
  }
}
```

## Sintetizar voz (ElevenLabs)
```json
{
  "type": "@elevenlabs/n8n-nodes-elevenlabs.elevenLabs",
  "typeVersion": 1,
  "parameters": {
    "resource": "speech",
    "operation": "textToSpeech",
    "voice": {
      "__rl": true,
      "mode": "id",
      "value": "pFZP5JQG7iQjIQuC4Bku"
    },
    "text": "={{ $json.texto_voz }}",
    "additionalOptions": {
      "model": {
        "__rl": true,
        "mode": "list",
        "value": "eleven_multilingual_v2"
      },
      "outputFormat": "mp3_44100_128",
      "languageCode": "es",
      "voiceSettings": "{\n  \"stability\": 0.55,\n  \"similarity_boost\": 0.75,\n  \"style\": 0,\n  \"use_speaker_boost\": true,\n  \"speed\": 1\n}"
    }
  },
  "credentials": {
    "elevenLabsApi": "ElevenLabs account"
  }
}
```

## Enviar nota de voz (Telegram)
```json
{
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "operation": "sendAudio",
    "chatId": "={{ $('Preparar respuesta hablada').first().json.tg_chat_id }}",
    "binaryData": true,
    "binaryPropertyName": "data",
    "additionalFields": {
      "title": "AgendaBot",
      "fileName": "respuesta.mp3"
    }
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```

## Descartar audio (compliance)
```json
{
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "jsCode": "// Compliance: el audio del paciente y el sintetizado no se conservan.\n// Se devuelve solo metadata (sin binario); además el workflow no guarda ejecuciones,\n// así que n8n borra los archivos temporales de la ejecución al terminar.\nreturn $input.all().map(i => ({ json: { enviado: true, chat_id: i.json.result?.chat?.id ?? null, audio_destruido: true } }));"
  }
}
```

## Enviar texto (Telegram)
```json
{
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "chatId": "={{ $json.tg_chat_id }}",
    "text": "={{ $json.texto_completo }}",
    "additionalFields": {
      "appendAttribution": false
    }
  },
  "credentials": {
    "telegramApi": "Telegram account"
  }
}
```
