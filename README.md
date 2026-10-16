# Ñangarekó IA

[![CI](https://github.com/SilredPY/DesafioUPE-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/SilredPY/DesafioUPE-2026/actions/workflows/ci.yml)

> *Ñangarekó* (guaraní): cuidar, proteger, velar por algo.
> **Tu compañero diario para anticiparte al clima, ordenar tu ciudad y moverte seguro.**

PWA mobile-first para el área metropolitana de Alto Paraná (Ciudad del Este, Presidente Franco, Hernandarias, Minga Guazú).

| Módulo | Qué hace |
|---|---|
| **Aratiri & Oky** | Pronóstico de 6 h (Open-Meteo) → reglas por temporada (El Niño / La Niña) → mensaje preventivo en español paraguayo generado por Claude. |
| **Yty & Sumideros** | Foto + GPS → Claude clasifica (`VERTEDERO_CLANDESTINO`, `SUMIDERO_BLOQUEADO`, `OBSTRUCCION_VIAL`) → severidad (sumidero tapado + lluvia = `CRITICO`) → Mapa de Riesgo Urbano. Calendario del camión por barrio. |
| **Tape Ysyry** | Reporte de 1 toque (🌊 raudal, ⚡ semáforo/cable, 🕳️ bache) → Zona Roja cuando ≥3 dispositivos distintos reportan lo mismo a ≤50 m en las últimas 3 h. |

## Arquitectura

```
backend/app/
  shared/            geo (Punto, bbox, haversine), severidad, db, http (device-id), ia/claude_client
  modules/<módulo>/
    domain.py        modelos y enums puros
    <reglas>.py      lógica de negocio pura (reglas_estacionales, scoring, agrupacion, calendario)
    ports.py         Protocols de los adaptadores externos
    use_cases.py     orquesta dominio + puertos
    infra/           adaptadores: Open-Meteo, Claude, PostGIS
    api.py           router FastAPI + DTOs
frontend/src/
  shared/            api (cliente + cola offline), hooks, ui (átomos y Mapa)
  features/          clima/, residuos/, transito/
```

Resiliencia:
- Si falla la IA, la alerta muestra el texto técnico y el reporte de foto se guarda como `PENDIENTE`. Ningún reporte se pierde.
- Los POST sin señal se guardan en IndexedDB y se reenvían cuando vuelve la conexión.
- El service worker cachea la app, los mapas (CacheFirst) y las últimas respuestas de la API (NetworkFirst con 5 s).
- Las fotos se comprimen a 1280 px / JPEG 70% en el celular antes de subirlas, y se les borran los datos EXIF.

## Cómo correrlo

Todo el sistema con un solo comando:

```bash
cp .env.example .env            # cargar ANTHROPIC_API_KEY
docker compose up -d --build
```

| Servicio | URL |
|---|---|
| App (nginx: PWA + proxy `/api`) | http://localhost |
| API + Swagger | http://localhost:8000/docs |
| PostGIS | localhost:5432 |

Para desarrollar con recarga en caliente: `docker compose up -d db api` y después `cd frontend && npm install && npm run dev`. Queda en http://localhost:5173.

## 📱 Instalar como app

Ñangarekó IA es una **PWA**: se instala desde el navegador, sin tienda de apps, y ocupa menos de 1 MB.

- **Android (Chrome):** tocar el botón **⬇ Instalar** del encabezado, o ⋮ → *Instalar aplicación*. Al mantener presionado el ícono aparecen accesos directos a *Tránsito* y *Reportar*.
- **iPhone (Safari):** Compartir → *Agregar a pantalla de inicio*.
- **PC (Chrome/Edge):** ícono de instalar en la barra de direcciones.

> ⚠️ En un celular, la cámara, el GPS y el modo offline **requieren HTTPS**: los navegadores solo los habilitan en `localhost` o en sitios seguros.

### Link público HTTPS gratis (sin dominio ni cuenta)

```bash
docker compose --profile publico up -d --build
docker compose logs tunel | grep trycloudflare     # → https://xxxx.trycloudflare.com
```

Abrí ese link en cualquier celular, o pasalo como código QR al jurado. Ten en cuenta:
- La app corre en **tu** compu: si la apagás o la desconectás, el link deja de funcionar.
- El link **cambia cada vez** que se reinicia el túnel.
- Para cerrarlo: `docker compose stop tunel`.

Para regenerar los íconos después de cambiar `frontend/public/icon.svg`, correr `cd frontend && npm run iconos`.

## 🎤 Modo demo (para el jurado)

Un día soleado no muestra nada. Para presentar:

```bash
CLIMA_DEMO=tormenta docker compose up -d --build     # o CLIMA_DEMO=sequia con TEMPORADA_ENSO=LA_NINA
docker compose exec db psql -U naangareko -f /demo/demo.sql   # justo antes de presentar
# abrir http://localhost
```

- **Clima:** muestra tormenta crítica en rojo, con consejos y el mensaje en jopara si hay `ANTHROPIC_API_KEY`.
- **Tránsito:** aparecen 2 Zonas Rojas, un raudal en la PY02 Km 4 y un semáforo en la Av. Monday. Un bache con un solo reporte no aparece: así se ve el anti-spam.
- **Mapa:** muestra 12 reportes de residuos en las 4 ciudades, 3 de ellos críticos.
- **Reportar:** subí una foto de un desagüe tapado. Como el modo demo simula lluvia, la IA la marca como **CRÍTICO**.

Guion sugerido (2 min): problema (inundaciones y basurales en Alto Paraná) → alerta en lenguaje del barrio → foto de sumidero + lluvia = crítico → tres vecinos confirman un raudal → Zona Roja → funciona sin señal (activá "Offline" en DevTools y reportá).

## Calidad y producción

- **CI (GitHub Actions):** en cada push corre los tests del backend, el build tipado del frontend y el build de las imágenes Docker.
- **nginx:**
  - Assets con hash cacheados un año (`immutable`).
  - Service worker y HTML sin caché, para que las actualizaciones lleguen al toque.
  - Compresión gzip.
  - Cabeceras de seguridad (`X-Frame-Options`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`: solo GPS y cámara).
- **API:**
  - Corre con un usuario sin privilegios y tiene healthcheck.
  - Comprime las respuestas con gzip.
  - Valida el tipo de imagen por su firma.
  - Limita los reportes por dispositivo.
  - No expone el `device_id`.

## Tests

```bash
cd backend && .venv/Scripts/python -m pytest
```

Prueban la lógica pura (reglas, scoring, agrupación de 50 m, calendario) y recorren la API completa con adaptadores falsos: sin red, sin Claude y sin base de datos.

## Configuración

| Variable | Default | |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | requerida para la IA |
| `ANTHROPIC_MODEL` | `claude-opus-5-5` | `claude-haiku-5-5` abarata mucho la clasificación |
| `TEMPORADA_ENSO` | `NEUTRAL` | `EL_NINO` / `LA_NINA`: actualizar a mano según el boletín ENSO |
| `CLIMA_DEMO` | vacío | `tormenta` / `sequia`: escenario fijo para presentar |
| `DATABASE_URL` | local | |

## Pendiente / fuera de alcance

- Notificaciones push reales: hoy el aviso del camión se muestra dentro de la app.
- Integración con la DMH oficial: hay que sumar un adaptador nuevo que implemente `FuenteClima`.
- Panel municipal y moderación de reportes `PENDIENTE`.
- Login.
- Guardar las fotos: hoy solo se guarda la clasificación.
- **El calendario de recolección usa datos de ejemplo** (`backend/app/modules/residuos/data/calendario_barrios.json`). Hay que reemplazarlo por el cronograma oficial de cada municipalidad.
