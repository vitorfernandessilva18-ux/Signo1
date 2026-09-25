-- Tabela que guarda cada consulta de signo feita no site
CREATE TABLE IF NOT EXISTS submissions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    birthdate   TEXT NOT NULL,        -- formato YYYY-MM-DD
    sign_name   TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
