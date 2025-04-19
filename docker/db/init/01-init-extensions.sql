-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For GIN indexes
CREATE EXTENSION IF NOT EXISTS "btree_gist";  -- For exclusion constraints
