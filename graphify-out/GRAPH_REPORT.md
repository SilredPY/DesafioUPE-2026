# Graph Report - Desafio_UPE  (2026-10-16)

## Corpus Check
- Corpus is ~20,509 words - fits in a single context window. You may not need a graph.

## Summary
- 662 nodes · 1686 edges · 32 communities (19 shown, 13 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 210 edges (avg confidence: 0.94)
- Token cost: 115,441 input · 0 output

## Community Hubs (Navigation)
- Tránsito y Zonas Rojas
- Orquestación Clima-Campus
- API Modo Campus
- Residuos e IA de Clasificación
- Entrada API y Residuos
- Tests de API con Fakes
- Dependencias del Frontend
- Infraestructura, CI y Documentación
- Selector de Ubicación
- UI Clima (Aratiri & Oky)
- UI de Reportes Ciudadanos
- Motor C++ de Agrupación
- Cliente HTTP y Cola Offline
- Shell de la App PWA
- Ajustes y Temas
- UI Campus y Calendario
- Config TypeScript
- Administración de Campus
- Íconos de la App
- Script iniciar.sh
- Paquete naangareko-api
- Paquete naangareko-nativo

## God Nodes (most connected - your core abstractions)
1. `Punto` - 53 edges
2. `Severidad` - 31 edges
3. `Institucion` - 22 edges
4. `Categoria` - 21 edges
5. `ReporteTransito` - 20 edges
6. `CampusRepo` - 19 edges
7. `ReporteResiduoRepo` - 19 edges
8. `Aviso` - 18 edges
9. `estado()` - 18 edges
10. `Temporada` - 18 edges

## Surprising Connections (you probably didn't know these)
- `CI job: nativo (backend + motor C++ in Docker)` --references--> `Motor nativo C++17 + pybind11 (grilla espacial)`  [INFERRED]
  .github/workflows/ci.yml → docs/COMO_FUNCIONA.md
- `.env configuration (ANTHROPIC_API_KEY, ADMIN_TOKEN, TEMPORADA_ENSO, CLIMA_DEMO)` --references--> `Administración con X-Admin-Token (compare_digest)`  [INFERRED]
  README.md → docs/COMO_FUNCIONA.md
- `.env configuration (ANTHROPIC_API_KEY, ADMIN_TOKEN, TEMPORADA_ENSO, CLIMA_DEMO)` --references--> `Reglas estacionales ENSO (El Niño / La Niña)`  [INFERRED]
  README.md → docs/COMO_FUNCIONA.md
- `Agregar institución educativa (mapa OSM / API)` --references--> `Modo Campus (recomendación ¿voy a clase?)`  [EXTRACTED]
  README.md → docs/COMO_FUNCIONA.md
- `Service db (PostGIS 16)` --shares_data_with--> `Esquema PostGIS (reportes_residuos, reportes_transito, instituciones, avisos)`  [INFERRED]
  docker-compose.yml → docs/COMO_FUNCIONA.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Compose startup chain db -> migrar -> api -> web -> tunel** — docker_compose_db, docker_compose_migrar, docker_compose_api, docker_compose_web, docker_compose_tunel [EXTRACTED 1.00]
- **Modo Campus recommendation inputs** — docs_como_funciona_modo_campus, docs_como_funciona_aratiri_oky, docs_como_funciona_zona_roja, docs_como_funciona_yty_sumideros [EXTRACTED 1.00]
- **CI pipeline jobs gating docker build** — _github_workflows_ci_backend, _github_workflows_ci_frontend, _github_workflows_ci_nativo, _github_workflows_ci_docker [EXTRACTED 1.00]
- **PWA icon set generated from icon.svg by @vite-pwa/assets-generator** — frontend_public_icon, frontend_public_apple_touch_icon_180x180, frontend_public_maskable_icon_512x512, frontend_public_pwa_192x192, frontend_public_pwa_512x512, frontend_public_pwa_64x64 [INFERRED 0.95]

## Communities (32 total, 13 thin omitted)

### Community 0 - "Tránsito y Zonas Rojas"
Cohesion: 0.07
Nodes (27): agrupar(), asignar_grupos(), asignar_grupos_py(), get_repo(), reportar(), ReporteIn, ReporteOut, zonas_rojas() (+19 more)

### Community 1 - "Orquestación Clima-Campus"
Cohesion: 0.09
Nodes (35): Settings, estado(), EstadoCampus, InstitucionDuplicada, alertas(), ciudades(), CiudadOut, get_fuente() (+27 more)

### Community 2 - "API Modo Campus"
Cohesion: 0.08
Nodes (36): admin(), _aviso_out(), AvisoIn, AvisoOut, crear_institucion(), estado(), EstadoOut, get_repo() (+28 more)

### Community 3 - "Residuos e IA de Clasificación"
Cohesion: 0.09
Nodes (22): get_repo(), Categoria, Clasificacion, ReporteResiduo, ClasificadorClaude, ReporteResiduoPg, ClasificadorImagen, ReporteResiduoRepo (+14 more)

### Community 4 - "Entrada API y Residuos"
Cohesion: 0.06
Nodes (23): fuera_de_zona(), limite_excedido(), salud(), calendario_barrios(), get_clasificador(), mapa(), _out(), RecorridoOut (+15 more)

### Community 5 - "Tests de API con Fakes"
Cohesion: 0.06
Nodes (18): admin_h(), CampusMem, client(), FuenteFake, h(), RepoMem, test_admin_deshabilitado_sin_token_configurado(), test_agregar_institucion() (+10 more)

### Community 6 - "Dependencias del Frontend"
Cohesion: 0.06
Nodes (37): dependencies, idb-keyval, leaflet, react, react-dom, react-leaflet, react-router-dom, @tanstack/react-query (+29 more)

### Community 7 - "Infraestructura, CI y Documentación"
Cohesion: 0.09
Nodes (26): CI workflow (GitHub Actions), CI job: backend (pytest), CI job: docker (compose build + config), CI job: frontend (npm test + build), CI job: nativo (backend + motor C++ in Docker), Service api (FastAPI backend), Service db (PostGIS 16), Service migrar (applies esquema/*.sql) (+18 more)

### Community 8 - "Selector de Ubicación"
Cohesion: 0.12
Nodes (20): Coord, dentroDeZona(), Lectura, leerCoordenadas(), NUM, PATRONES, ok(), ZONA (+12 more)

### Community 9 - "UI Clima (Aratiri & Oky)"
Cohesion: 0.16
Nodes (21): AlertaCard(), TITULO, AlertasPage(), estado(), TEMPORADA, Alerta, Ciudad, ResumenClima (+13 more)

### Community 10 - "UI de Reportes Ciudadanos"
Cohesion: 0.17
Nodes (17): comprimirImagen(), ReportarFotoPage(), elegirFoto(), enviarReporte(), Resultado, BotonesReporteRapido(), reportar(), TipoIncidente (+9 more)

### Community 11 - "Motor C++ de Agrupación"
Cohesion: 0.11
Nodes (8): Ancla, lat, lon, tipo, asignar_grupos(), clave(), distancia_m(), PYBIND11_MODULE()

### Community 12 - "Cliente HTTP y Cola Offline"
Cohesion: 0.15
Nodes (16): queryClient, sincronizar(), aInit(), ApiError, deviceId(), Envio, nuevoId(), pedir() (+8 more)

### Community 13 - "Shell de la App PWA"
Cohesion: 0.23
Nodes (10): App(), EventoInstalar, useInstalar(), suscribir(), useOnline(), BottomNav(), SECCIONES, Header() (+2 more)

### Community 14 - "Ajustes y Temas"
Cohesion: 0.23
Nodes (15): AjustesPage(), elegir(), Salud, TEMAS, pendientes(), aplicar(), cambiarTema(), COLOR_PREDETERMINADO (+7 more)

### Community 15 - "UI Campus y Calendario"
Cohesion: 0.25
Nodes (12): AVISO, CampusPage(), HERO, hora(), useEstadoCampus(), useInstituciones(), CalendarioBarrio(), clave() (+4 more)

### Community 16 - "Config TypeScript"
Cohesion: 0.13
Nodes (14): compilerOptions, jsx, lib, module, moduleResolution, noUnusedLocals, noUnusedParameters, resolveJsonModule (+6 more)

### Community 17 - "Administración de Campus"
Cohesion: 0.22
Nodes (12): AdminCampus(), agregarInstitucion(), ejecutar(), publicarAviso(), Estado, SelectorUbicacion, TIPOS_AVISO, Aviso (+4 more)

### Community 18 - "Íconos de la App"
Cohesion: 0.33
Nodes (6): Apple touch icon 180x180 (full-bleed teal, no rounded corners), Ñangarekó IA app icon (SVG source): teal rounded square with white map pin containing two wave lines, Maskable PWA icon 512x512 (full-bleed teal safe-zone background), PWA icon 192x192 (rounded teal square, map pin with waves), PWA icon 512x512 (rounded teal square, map pin with waves), PWA icon 64x64 (rounded teal square, map pin with waves)

## Knowledge Gaps
- **17 isolated node(s):** `naangareko-nativo`, `lat`, `lon`, `tipo`, `naangareko-api` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 189 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Punto` connect `Tránsito y Zonas Rojas` to `Orquestación Clima-Campus`, `API Modo Campus`, `Residuos e IA de Clasificación`, `Entrada API y Residuos`, `Tests de API con Fakes`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Punto` (e.g. with `crear_institucion()` and `Institucion`) actually correct?**
  _`Punto` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `naangareko-nativo`, `lat`, `lon` to the rest of the system?**
  _17 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Tránsito y Zonas Rojas` be split into smaller, more focused modules?**
  _Cohesion score 0.07382039573820395 - nodes in this community are weakly interconnected._
- **Why does `react` connect `Cliente HTTP y Cola Offline` to `Dependencias del Frontend`, `Selector de Ubicación`, `UI Clima (Aratiri & Oky)`, `UI de Reportes Ciudadanos`, `Shell de la App PWA`, `Ajustes y Temas`, `UI Campus y Calendario`, `Administración de Campus`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Severidad` (e.g. with `recomendar()` and `Alerta`) actually correct?**
  _`Severidad` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Should `Orquestación Clima-Campus` be split into smaller, more focused modules?**
  _Cohesion score 0.08567774936061381 - nodes in this community are weakly interconnected._