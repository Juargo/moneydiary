-- Script SQL para agregar soporte a patrones de exclusión y transferencias internas
-- Ejecutar este script después de las migraciones existentes

-- 1. Crear categorías especiales para transferencias y exclusiones
INSERT INTO categories (name, is_income, icon, display_order, created_at, updated_at) VALUES 
    ('Sistema', false, '⚙️', 1000, NOW(), NOW()),
    ('Transferencias', false, '🔄', 999, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- 2. Crear subcategorías especiales
INSERT INTO subcategories (name, category_id, display_order, created_at, updated_at)
SELECT 
    'Transferencia Interna',
    c.id,
    1,
    NOW(),
    NOW()
FROM categories c 
WHERE c.name = 'Transferencias'
ON CONFLICT (name, category_id) DO NOTHING;

INSERT INTO subcategories (name, category_id, display_order, created_at, updated_at)
SELECT 
    'Ignorar',
    c.id,
    1,
    NOW(),
    NOW()
FROM categories c 
WHERE c.name = 'Sistema'
ON CONFLICT (name, category_id) DO NOTHING;

INSERT INTO subcategories (name, category_id, display_order, created_at, updated_at)
SELECT 
    'Ajuste de Saldo',
    c.id,
    2,
    NOW(),
    NOW()
FROM categories c 
WHERE c.name = 'Sistema'
ON CONFLICT (name, category_id) DO NOTHING;

INSERT INTO subcategories (name, category_id, display_order, created_at, updated_at)
SELECT 
    'Comisión Bancaria',
    c.id,
    3,
    NOW(),
    NOW()
FROM categories c 
WHERE c.name = 'Sistema'
ON CONFLICT (name, category_id) DO NOTHING;

-- 3. Crear vista para obtener patrones con información completa
CREATE OR REPLACE VIEW pattern_details AS
SELECT 
    dp.id,
    dp.user_id,
    dp.name,
    dp.pattern,
    dp.pattern_type,
    dp.subcategory_id,
    dp.priority,
    dp.is_case_sensitive,
    dp.is_active,
    dp.auto_apply,
    dp.notes,
    dp.created_at,
    dp.updated_at,
    s.name as subcategory_name,
    c.name as category_name,
    CASE 
        WHEN c.name IN ('Sistema', 'Transferencias') THEN true 
        ELSE false 
    END as is_system_category
FROM description_patterns dp
JOIN subcategories s ON dp.subcategory_id = s.id
JOIN categories c ON s.category_id = c.id
ORDER BY dp.priority DESC, dp.created_at ASC;

-- 4. Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_patterns_priority_active ON description_patterns(priority DESC, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_patterns_user_priority ON description_patterns(user_id, priority DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_pattern_matches_transaction ON pattern_matches(transaction_id);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_pattern ON pattern_matches(pattern_id);

-- 5. Mostrar las categorías y subcategorías creadas
SELECT 'Categorías creadas:' as info;
SELECT id, name, is_income, icon, display_order FROM categories WHERE name IN ('Sistema', 'Transferencias');

SELECT 'Subcategorías creadas:' as info;
SELECT s.id, s.name, c.name as category_name, s.display_order 
FROM subcategories s 
JOIN categories c ON s.category_id = c.id 
WHERE c.name IN ('Sistema', 'Transferencias')
ORDER BY c.name, s.display_order;

COMMIT;
