-- Seed data for initial setup

-- Insert financial methods
INSERT INTO app.financial_methods (name, description, key)
VALUES
  ('Presupuesto 50/30/20', 'Divide tus ingresos en necesidades (50%), deseos (30%) y ahorros (20%)', 'fifty_thirty_twenty'),
  ('Método de Sobres', 'Asigna efectivo en sobres físicos o digitales para cada categoría de gasto', 'envelope'),
  ('Sistema Cero', 'Cada peso que ganas tiene un destino asignado, dejando tu balance mensual en cero', 'zero_based'),
  ('Método Kakebo', 'Diario financiero donde anotas ingresos, gastos, metas y reflexiones', 'kakebo'),
  ('Pay Yourself First', 'Antes de gastar en cualquier cosa, apartas una cantidad fija para ahorro o inversión', 'pay_yourself_first')
ON CONFLICT (key) DO NOTHING;

-- Insert basic transaction statuses
INSERT INTO app.transaction_statuses (name, description)
VALUES
  ('Pendiente', 'Transacción registrada pero no conciliada'),
  ('Completada', 'Transacción verificada y conciliada'),
  ('Anulada', 'Transacción cancelada o revertida')
ON CONFLICT (name) DO NOTHING;

-- Insert basic account types
INSERT INTO app.account_types (name, description)
VALUES
  ('Cuenta Corriente', 'Cuenta bancaria de uso diario'),
  ('Cuenta de Ahorros', 'Cuenta bancaria para ahorros'),
  ('Tarjeta de Crédito', 'Tarjeta de crédito bancaria'),
  ('Efectivo', 'Dinero en efectivo'),
  ('Inversiones', 'Cuentas de inversión')
ON CONFLICT (name) DO NOTHING;

-- Insert basic category groups
INSERT INTO app.category_groups (name, is_expense)
VALUES
  ('Ingresos', FALSE),
  ('Vivienda', TRUE),
  ('Alimentación', TRUE),
  ('Transporte', TRUE),
  ('Salud', TRUE),
  ('Educación', TRUE),
  ('Entretenimiento', TRUE),
  ('Ahorro', FALSE)
ON CONFLICT (name) DO NOTHING;
