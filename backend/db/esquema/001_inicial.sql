-- Esquema inicial. Idempotente: se puede volver a correr sin romper nada.
-- shortcut: migraciones SQL numeradas aplicadas en orden; pasar a Alembic si el esquema se vuelve complejo.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS reportes_residuos (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ubicacion   geography(Point, 4326) NOT NULL,
    device_id   text NOT NULL,
    categoria   text NOT NULL,
    confianza   real NOT NULL,
    descripcion text NOT NULL DEFAULT '',
    severidad   text NOT NULL,
    creado      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS reportes_residuos_ubicacion_idx ON reportes_residuos USING gist (ubicacion);
CREATE INDEX IF NOT EXISTS reportes_residuos_creado_idx ON reportes_residuos (creado);
CREATE INDEX IF NOT EXISTS reportes_residuos_device_id_creado_idx ON reportes_residuos (device_id, creado);

CREATE TABLE IF NOT EXISTS reportes_transito (
    id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ubicacion geography(Point, 4326) NOT NULL,
    tipo      text NOT NULL,
    device_id text NOT NULL,
    creado    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS reportes_transito_ubicacion_idx ON reportes_transito USING gist (ubicacion);
CREATE INDEX IF NOT EXISTS reportes_transito_creado_idx ON reportes_transito (creado);
CREATE INDEX IF NOT EXISTS reportes_transito_device_id_creado_idx ON reportes_transito (device_id, creado);
