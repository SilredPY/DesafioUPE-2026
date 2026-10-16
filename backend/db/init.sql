-- Esquema inicial. Lo ejecuta la imagen de PostGIS solo la primera vez que crea el volumen.
-- shortcut: sin herramienta de migraciones; sumar Alembic con el primer cambio de esquema en producción.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE reportes_residuos (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ubicacion   geography(Point, 4326) NOT NULL,
    device_id   text NOT NULL,
    categoria   text NOT NULL,
    confianza   real NOT NULL,
    descripcion text NOT NULL DEFAULT '',
    severidad   text NOT NULL,
    creado      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON reportes_residuos USING gist (ubicacion);
CREATE INDEX ON reportes_residuos (creado);
CREATE INDEX ON reportes_residuos (device_id, creado);

CREATE TABLE reportes_transito (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ubicacion geography(Point, 4326) NOT NULL,
    tipo      text NOT NULL,
    device_id text NOT NULL,
    creado    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON reportes_transito USING gist (ubicacion);
CREATE INDEX ON reportes_transito (creado);
CREATE INDEX ON reportes_transito (device_id, creado);
