# Continuar el proyecto en otra PC

Guía de continuidad del proyecto integrador (curso *AI Automation Avanzado*).
El workflow es portable (está en este repo + Drive). Lo único que se rehace en cada PC
son las cosas propias de la instalación: **credenciales** y **API key de n8n**.

---

## Requisitos en la otra PC
- **Claude Code** instalado y logueado con la misma cuenta de Anthropic (va con la cuenta, no con la máquina).
- **n8n local** funcionando (su propia instalación).
- **Git** + acceso al repo `marwais/Learning`.
- **Chrome** logueado en ese n8n (para que Claude maneje la UI vía Claude-in-Chrome).

## A tener a mano (secretos — NO están en el repo)
- **Anthropic API key** (`sk-ant-...`) — la misma sirve en cualquier PC.
- **Google OAuth2 Client ID + Client Secret** (del proyecto de Google Cloud).

---

## Pasos

### 1. Traer el proyecto
```bash
git clone https://github.com/marwais/Learning.git
# o si ya lo tenés:  git pull
```
El flujo está en `Avanzado/Modulo1/checkpoint1_julio_waisburd.json`.

### 2. Importar el workflow en el n8n de esa PC
n8n → menú (⋯) → **Import from File** → elegí el `.json`.
Van a aparecer los 5 nodos con **triángulos rojos** (falta credencial) — es normal.

### 3. Re-crear las 3 credenciales
- **Anthropic account** → pegar la Anthropic API key.
- **Google Sheets OAuth2** y **Gmail OAuth2** → pegar el **mismo** Client ID/Secret y hacer *Sign in with Google* autorizando con **mwquiero@gmail.com**.

> **Redirect URI:** si este n8n también corre en `http://localhost:5678`, el cliente OAuth de Google ya sirve tal cual
> (`http://localhost:5678/rest/oauth2-credential/callback`). Si el host/puerto es distinto, agregá ese redirect URI
> nuevo al cliente en Google Cloud Console antes de autorizar.

### 4. Re-linkear credenciales en cada nodo
Abrí **Anthropic Chat Model**, **Agenda_Turnos** y **Reporte de observabilidad** y seleccioná la credencial nueva en cada uno.
Verificá que **Agenda_Turnos** siga apuntando a la planilla (Document = Agenda_Turnos, Sheet = Hoja 1).

### 5. Generar una API key de n8n en esa PC (para que Claude trabaje por API)
n8n → **Settings → n8n API → Create an API key**. Guardala en un archivo local
(ej. `...\SessionLocal\n8n-api-key-OTRA-PC.txt`) — fuera de todo repo git.

### 6. Probar
*Execute Workflow* con un prompt de prueba. Recorrido en verde = todo ok.

---

## Datos de referencia (no secretos)
- **Rol del agente:** Coordinador de Agenda ("AgendaBot"). Proyecto integrador que crece M1→M11 (no se rehace).
- **Modelo:** `claude-sonnet-5` (OJO: `claude-3-5-sonnet-20241022` está **retirado**, da 404).
- **Guardrail:** AI Agent, maxIterations = 8.
- **Planilla Agenda_Turnos** (en Drive, nube, compartida con mwquiero):
  id `1IjnCbHrSslWrcryhGU-vB5iT0lRt62b6l5C0FBVAMmg` — columnas: Fecha, Hora, Nombre, Motivo, Estado.
- **Cuenta Google para OAuth:** mwquiero@gmail.com (test user de la consent screen en modo Testing).
- **Observabilidad:** Gmail envía a mwaisburd@gmail.com.

## Nota sobre la memoria de Claude Code
La memoria automática es local de cada PC (`~/.claude/projects/<proyecto>/memory/`). No viaja con el repo.
Este documento cumple esa función de handoff. Si querés, podés copiar manualmente esa carpeta de `memory`
a la otra PC para conservar el contexto acumulado.
