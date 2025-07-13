-- Create schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
ALTER DATABASE moneydiary SET search_path TO app, public;
ALTER DATABASE moneydiary SET timezone TO 'UTC';

-- Create read-only user for reporting
CREATE USER moneydiary_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE moneydiary TO moneydiary_readonly;
GRANT USAGE ON SCHEMA app TO moneydiary_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO moneydiary_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO moneydiary_readonly;