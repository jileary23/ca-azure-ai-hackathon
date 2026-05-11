-- Create SQL users for the system-assigned managed identities of the DAB and webapp
-- Container Apps. Run as the Entra SQL admin after the bicep deployment assigns
-- `identity: SystemAssigned` to both apps. Idempotent.

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'sqlrag-aca-dab')
    CREATE USER [sqlrag-aca-dab] FROM EXTERNAL PROVIDER;
GO
ALTER ROLE db_datareader ADD MEMBER [sqlrag-aca-dab];
ALTER ROLE db_datawriter ADD MEMBER [sqlrag-aca-dab];
GRANT EXECUTE TO [sqlrag-aca-dab];
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = 'sqlrag-aca-webapp')
    CREATE USER [sqlrag-aca-webapp] FROM EXTERNAL PROVIDER;
GO
ALTER ROLE db_datareader ADD MEMBER [sqlrag-aca-webapp];
GRANT EXECUTE TO [sqlrag-aca-webapp];
GO
