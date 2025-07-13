-- Crear el usuario principal si no existe
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'moneydiary_user') THEN
      CREATE USER moneydiary_user WITH PASSWORD 'moneydiary_password' CREATEDB;
   END IF;
END
$$;

-- Asegúrate de que el usuario sea el propietario de la base de datos
ALTER DATABASE moneydiary OWNER TO moneydiary_user;