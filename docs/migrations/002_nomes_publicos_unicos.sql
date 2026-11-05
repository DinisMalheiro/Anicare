INSERT INTO perfis (utilizador_id, nome_exibicao)
SELECT u.id, u.username::text
FROM utilizadores u
WHERE NOT EXISTS (
    SELECT 1 FROM perfis p WHERE p.utilizador_id = u.id
);

UPDATE perfis p
SET nome_exibicao = u.username::text
FROM utilizadores u
WHERE u.id = p.utilizador_id
  AND NULLIF(btrim(p.nome_exibicao), '') IS NULL;

WITH duplicados AS (
    SELECT p.utilizador_id, u.username::text AS username,
           row_number() OVER (
               PARTITION BY lower(btrim(p.nome_exibicao))
               ORDER BY p.utilizador_id
           ) AS numero
    FROM perfis p
    JOIN utilizadores u ON u.id = p.utilizador_id
)
UPDATE perfis p
SET nome_exibicao = d.username || '-' || d.utilizador_id
FROM duplicados d
WHERE p.utilizador_id = d.utilizador_id
  AND d.numero > 1;

CREATE UNIQUE INDEX IF NOT EXISTS uq_perfis_nome_exibicao_ci
    ON perfis (lower(btrim(nome_exibicao)));
