DROP TABLE IF EXISTS knowledge;

CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT NOT NULL,
    attribute TEXT NOT NULL,
    value TEXT NOT NULL,
    category TEXT,
    description TEXT,
    source TEXT DEFAULT 'knowledge.db',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_entity ON knowledge(entity);
CREATE INDEX idx_attribute ON knowledge(attribute);
