ALTER TABLE comentarios
    ADD COLUMN IF NOT EXISTS parent_id bigint
    REFERENCES comentarios (id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_comentarios_parent
    ON comentarios (parent_id);
