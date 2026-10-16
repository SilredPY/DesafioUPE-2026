-- Modo Campus: instituciones educativas y sus avisos. Idempotente.
CREATE TABLE IF NOT EXISTS instituciones (
    slug      text PRIMARY KEY,
    nombre    text NOT NULL,
    ciudad    text NOT NULL,
    ubicacion geography(Point, 4326) NOT NULL,
    radio_m   integer NOT NULL DEFAULT 1500,
    creado    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS avisos (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    institucion   text NOT NULL REFERENCES instituciones (slug) ON DELETE CASCADE,
    tipo          text NOT NULL,
    titulo        text NOT NULL,
    mensaje       text NOT NULL,
    vigente_hasta timestamptz NOT NULL,
    creado        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS avisos_institucion_vigente_idx ON avisos (institucion, vigente_hasta);

-- Institución incluida de ejemplo. Ubicación aproximada: ajustar con las coordenadas exactas del campus.
INSERT INTO instituciones (slug, nombre, ciudad, ubicacion, radio_m)
VALUES ('upe-presidente-franco', 'Universidad Privada del Este (UPE) — Sede Presidente Franco', 'Presidente Franco',
        ST_SetSRID(ST_MakePoint(-54.6110, -25.5560), 4326)::geography, 1500)
ON CONFLICT (slug) DO NOTHING;
