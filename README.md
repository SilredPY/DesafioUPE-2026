# Ñangarekó IA

[![CI](https://github.com/SilredPY/DesafioUPE-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/SilredPY/DesafioUPE-2026/actions/workflows/ci.yml)

> *Ñangarekó* (guaraní): cuidar, proteger, velar por algo.
> **Tu compañero diario para anticiparte al clima, ordenar tu ciudad y moverte seguro.**

App instalable (PWA) para el área metropolitana de Alto Paraná: Ciudad del Este, Presidente Franco, Hernandarias y Minga Guazú.

| | Sección | Qué hace |
|---|---|---|
| ⛈️ | **Aratiri & Oky** | Alertas del pronóstico según El Niño / La Niña, explicadas en lenguaje del barrio por IA (Claude). |
| 🚦 | **Tape Ysyry** | Reportes de 1 toque (raudal, semáforo, bache). Tres vecinos a menos de 50 m forman una **Zona Roja**. |
| 📷 | **Yty & Sumideros** | Foto + GPS: la IA clasifica la basura; un sumidero tapado con lluvia en camino sale **CRÍTICO**. |
| 🗺️ | **Mapa de Riesgo** | Todos los reportes por severidad, más el calendario del camión recolector por barrio. |
| 🎓 | **Modo Campus** | Para estudiantes: clima, tránsito y avisos de su institución, más un "¿voy a clase?". Incluye la **UPE Presidente Franco**; se pueden sumar otras instituciones. |
| ⚙️ | **Ajustes** | Modo claro, oscuro o del sistema, y paleta de colores con color personalizado. |

📖 **Informe técnico completo:** [docs/COMO_FUNCIONA.md](docs/COMO_FUNCIONA.md). Tiene la arquitectura, los flujos, la API, los datos, el motor C++, la seguridad y el rendimiento.

---

## 🚀 Inicio rápido (para todo el equipo)

**Único requisito:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) abierto. No hace falta instalar Python ni Node.

```bash
git clone https://github.com/SilredPY/DesafioUPE-2026.git
cd DesafioUPE-2026
```

| Sistema | Levantar | Con demo + link público | Apagar |
|---|---|---|---|
| **Windows (PowerShell)** | `.\scripts\iniciar.ps1` | `.\scripts\iniciar.ps1 -Demo -Publico` | `.\scripts\iniciar.ps1 -Detener` |
| **Windows (CMD)** | `scripts\iniciar.cmd` | `scripts\iniciar.cmd -Demo -Publico` | `scripts\iniciar.cmd -Detener` |
| **macOS / Linux / WSL** | `./scripts/iniciar.sh` | `./scripts/iniciar.sh --demo --publico` | `./scripts/iniciar.sh --detener` |

El script revisa que Docker esté corriendo y crea `.env` si falta. Después levanta la base, aplica las migraciones, arranca la API y la web, y al final muestra las direcciones:

| | Dirección |
|---|---|
| App en tu compu | http://localhost |
| API + documentación (Swagger) | http://localhost:8000/docs |
| Otros equipos de tu red (Wi-Fi) | `http://<tu-IP>`: la muestra el script |
| Celulares desde cualquier lugar | `https://….trycloudflare.com`: con `-Publico` / `--publico` |

> Si PowerShell bloquea el script ("la ejecución de scripts está deshabilitada"), usá la versión CMD o corré una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 📱 Usarla en el celular

- **Cámara, GPS y modo sin señal requieren HTTPS.** Usá el link público (`-Publico`), que es gratis y no pide cuenta ni dominio. Por la IP de la red local la app abre, pero sin esas funciones.
- **Instalar:**
  - En Android (Chrome): botón **⬇ Instalar** del encabezado.
  - En iPhone (Safari): Compartir → *Agregar a pantalla de inicio*.
- **El link público** depende de que la compu que lo generó siga encendida, y **cambia** si se reinicia el túnel.

### 🔑 Activar la IA y la administración (opcional)

Editá `.env` (no se sube a git):

```ini
ANTHROPIC_API_KEY=sk-ant-...     # mensajes en jopara y clasificación de fotos
ADMIN_TOKEN=un-token-largo        # publicar avisos y agregar instituciones en 🎓 Campus
```

Después de editarlo, reiniciá con el script. Sin clave, todo funciona igual: las alertas muestran el texto técnico y las fotos quedan como "Pendiente de revisión".

---

## 🎤 Modo demo (para el jurado)

```powershell
.\scripts\iniciar.ps1 -Demo -Publico
```

Simula una tormenta y carga datos de ejemplo:
- **Clima:** tormenta CRÍTICA en las 4 ciudades.
- **Tránsito:** 3 Zonas Rojas (PY02 Km 4, Av. Monday, cerca de la UPE). Un bache con un solo reporte no aparece: así se ve el anti-spam.
- **Mapa:** 13 reportes de basura, 4 críticos.
- **Campus UPE:** "🏠 Evitá trasladarte", con un aviso de la universidad, una Zona Roja y un sumidero crítico cerca.

Las Zonas Rojas duran unas 2 horas: correr el script de nuevo justo antes de presentar.

**Guion sugerido (2 min):**
1. El problema: inundaciones y basurales en Alto Paraná.
2. La alerta en lenguaje del barrio.
3. Un estudiante abre 🎓 Campus y ve que no conviene salir.
4. Una foto de un sumidero tapado con lluvia en camino sale CRÍTICO.
5. Tres vecinos confirman un raudal y aparece la Zona Roja.
6. Funciona sin señal.
7. Ajustes: modo oscuro y la paleta de colores.

---

## 🧩 Agregar otra institución educativa

Hace falta `ADMIN_TOKEN` configurado.

- **Desde la app:** 🎓 Campus → *Administración de la institución* → completar el token y los datos, o tocar *Usar mi ubicación actual* estando en el campus.
- **Desde la API** (las coordenadas son de ejemplo):
  ```bash
  curl -X POST http://localhost:8000/api/campus/instituciones \
    -H "X-Admin-Token: $ADMIN_TOKEN" -H "Content-Type: application/json" \
    -d '{"nombre":"Facultad Politécnica — UNE","ciudad":"Ciudad del Este","lat":-25.4995,"lon":-54.6744}'
  ```

---

## 🛠️ Desarrollo

| Tarea | Comando |
|---|---|
| Frontend con recarga en caliente | `docker compose up -d db migrar api` y después `cd frontend && npm install && npm run dev` → http://localhost:5173 |
| Tests backend (local) | `cd backend && python -m venv .venv && .venv/Scripts/pip install -e ".[dev]" && .venv/Scripts/python -m pytest` |
| Tests backend con motor C++ | `docker build --target pruebas -t prueba backend && docker run --rm prueba` |
| Benchmark C++ vs Python | `docker run --rm prueba python nativo/bench.py 100000` |
| Regenerar íconos | `cd frontend && npm run iconos` |
| Ver logs | `docker compose logs -f api` |
| Borrar todos los datos | `docker compose down -v` ⚠️ irreversible |

En macOS/Linux, reemplazá `.venv/Scripts/` por `.venv/bin/`.

## ⚙️ Configuración (`.env`)

| Variable | Default | |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Activa la IA |
| `ANTHROPIC_MODEL` | `claude-opus-5-5` | `claude-haiku-5-5` abarata mucho la clasificación |
| `ADMIN_TOKEN` | vacío | Habilita la administración de Campus |
| `TEMPORADA_ENSO` | `NEUTRAL` | `EL_NINO` / `LA_NINA`: actualizar según el boletín ENSO |
| `CLIMA_DEMO` | vacío | `tormenta` / `sequia`: escenario fijo para presentar |

## Estructura

```
backend/
  app/modules/        clima · residuos · transito · campus (Clean Architecture por módulo)
  nativo/             motor C++17 + pybind11 (agrupación masiva, 47–53× más rápido)
  db/esquema/         migraciones SQL idempotentes   db/demo.sql: datos de ejemplo
  tests/              52 tests
frontend/src/
  shared/             cliente HTTP + cola offline, tema, componentes UI
  features/           clima · transito · residuos · campus · ajustes
scripts/              iniciar.ps1 · iniciar.cmd · iniciar.sh
docs/                 COMO_FUNCIONA.md (informe técnico)
```
