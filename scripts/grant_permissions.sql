-- Grant permissions to usr_codorch for codorch_dev database

\c codorch_dev

-- Grant schema permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO usr_codorch;

-- Grant table permissions (existing tables)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO usr_codorch;

-- Grant sequence permissions (for auto-increment)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO usr_codorch;

-- Grant future table permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO usr_codorch;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO usr_codorch;

-- Verify permissions
SELECT grantee, privilege_type 
FROM information_schema.role_table_grants 
WHERE grantee = 'usr_codorch'
LIMIT 5;

\echo 'Permissions granted successfully!'
