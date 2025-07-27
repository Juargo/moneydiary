-- Crear tabla para patrones de descripción
CREATE TABLE description_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    pattern VARCHAR NOT NULL,
    pattern_type VARCHAR NOT NULL DEFAULT 'contains' CHECK (pattern_type IN ('contains', 'starts_with', 'ends_with', 'regex', 'exact')),
    subcategory_id INTEGER NOT NULL REFERENCES subcategories(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,
    is_case_sensitive BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    auto_apply BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla para registro de coincidencias de patrones (auditoría)
CREATE TABLE pattern_matches (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    pattern_id INTEGER NOT NULL REFERENCES description_patterns(id) ON DELETE CASCADE,
    matched_text VARCHAR,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    was_manual_override BOOLEAN DEFAULT FALSE
);

-- Crear índices para mejor rendimiento
CREATE INDEX idx_description_patterns_user_id ON description_patterns(user_id);
CREATE INDEX idx_description_patterns_active ON description_patterns(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_description_patterns_priority ON description_patterns(user_id, priority DESC, id);
CREATE INDEX idx_pattern_matches_transaction_id ON pattern_matches(transaction_id);
CREATE INDEX idx_pattern_matches_pattern_id ON pattern_matches(pattern_id);

-- Agregar comentarios para documentación
COMMENT ON TABLE description_patterns IS 'Patrones para transformar descripciones de transacciones en subcategorías automáticamente';
COMMENT ON COLUMN description_patterns.pattern_type IS 'Tipo de patrón: contains, starts_with, ends_with, regex, exact';
COMMENT ON COLUMN description_patterns.priority IS 'Prioridad del patrón (mayor número = mayor prioridad)';
COMMENT ON COLUMN description_patterns.auto_apply IS 'Si el patrón se aplica automáticamente o solo como sugerencia';

COMMENT ON TABLE pattern_matches IS 'Registro de aplicaciones de patrones para auditoría y análisis';
COMMENT ON COLUMN pattern_matches.was_manual_override IS 'Si el usuario cambió la categoría después de aplicar el patrón';
