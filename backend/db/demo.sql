-- Datos de DEMOSTRACIÓN para presentar el mapa. No usar en producción.
-- docker compose exec db psql -U naangareko -f /demo/demo.sql
-- Los reportes de tránsito usan now(): correrlo justo antes de la demo (las Zonas Rojas duran 3 h).

INSERT INTO reportes_residuos (ubicacion, device_id, categoria, confianza, descripcion, severidad, creado)
SELECT ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography, 'demo-' || n, cat, conf, descr, sev, now() - (n || ' hours')::interval
FROM (VALUES
  (1,  -25.5105, -54.6125, 'SUMIDERO_BLOQUEADO',    0.93, 'Boca de tormenta tapada con bolsas y hojas sobre la vereda.', 'CRITICO'),
  (2,  -25.5150, -54.6180, 'SUMIDERO_BLOQUEADO',    0.88, 'Rejilla pluvial cubierta de arena y botellas plásticas.',     'CRITICO'),
  (3,  -25.5210, -54.6300, 'VERTEDERO_CLANDESTINO', 0.91, 'Montículo de basura doméstica en un terreno baldío.',         'MEDIO'),
  (4,  -25.5580, -54.6100, 'VERTEDERO_CLANDESTINO', 0.86, 'Restos de poda y bolsas acumuladas junto a la calle.',        'MEDIO'),
  (5,  -25.5630, -54.6150, 'SUMIDERO_BLOQUEADO',    0.79, 'Desagüe obstruido con barro y residuos.',                     'ALTO'),
  (6,  -25.4080, -54.6400, 'OBSTRUCCION_VIAL',      0.84, 'Escombros de construcción ocupando medio carril.',            'ALTO'),
  (7,  -25.4020, -54.6350, 'VERTEDERO_CLANDESTINO', 0.42, 'Posible acumulación de residuos al costado del camino.',      'BAJO'),
  (8,  -25.4850, -54.7980, 'OBSTRUCCION_VIAL',      0.81, 'Ramas caídas bloqueando la calle de tierra.',                 'MEDIO'),
  (9,  -25.4800, -54.8050, 'VERTEDERO_CLANDESTINO', 0.90, 'Basural a cielo abierto cerca de un arroyo.',                 'MEDIO'),
  (10, -25.5170, -54.6400, 'SUMIDERO_BLOQUEADO',    0.95, 'Sumidero sobre la Ruta PY02 Km 4 tapado por residuos.',       'CRITICO'),
  (11, -25.5300, -54.6250, 'OBSTRUCCION_VIAL',      0.77, 'Neumáticos y chatarra sobre la calzada.',                     'MEDIO'),
  (12, -25.4950, -54.6900, 'VERTEDERO_CLANDESTINO', 0.89, 'Basura acumulada en la banquina de la Ruta PY02 Km 10.',      'MEDIO')
) AS t(n, lat, lon, cat, conf, descr, sev);

INSERT INTO reportes_transito (ubicacion, tipo, device_id, creado)
SELECT ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography, tipo, dev, now() - (min || ' minutes')::interval
FROM (VALUES
  -- Raudal en Ruta PY02 Km 4: 4 vecinos
  (-25.51700, -54.64000, 'RAUDAL', 'demo-a1', 5), (-25.51710, -54.64010, 'RAUDAL', 'demo-a2', 12),
  (-25.51690, -54.63990, 'RAUDAL', 'demo-a3', 20), (-25.51720, -54.64020, 'RAUDAL', 'demo-a4', 31),
  -- Semáforo apagado en Av. Monday: 3 vecinos
  (-25.52480, -54.62100, 'SEMAFORO_CABLE', 'demo-b1', 8), (-25.52490, -54.62110, 'SEMAFORO_CABLE', 'demo-b2', 15),
  (-25.52470, -54.62090, 'SEMAFORO_CABLE', 'demo-b3', 40),
  -- Bache en Pdte. Franco: solo 1 vecino (no llega a Zona Roja: así se ve el anti-spam)
  (-25.56000, -54.61200, 'BACHE', 'demo-c1', 10)
) AS t(lat, lon, tipo, dev, min);
