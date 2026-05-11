/*
Set this before running:
  :setvar OPENAI_ENDPOINT "https://<account>.openai.azure.com"

Subscription policy requires Entra-only auth, so the database scoped credential
uses the SQL server's system-assigned managed identity. The credential NAME must
match the URL prefix that sp_invoke_external_rest_endpoint will call so the
engine can locate it automatically.

The SQL server MI must hold the "Cognitive Services User" role on the AI account.
*/

-- A database master key is required before creating database scoped credentials.
IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
BEGIN
    DECLARE @pwd NVARCHAR(128) = CONVERT(NVARCHAR(36), NEWID()) + '!Aa1';
    DECLARE @createKey NVARCHAR(MAX) = N'CREATE MASTER KEY ENCRYPTION BY PASSWORD = ''' + REPLACE(@pwd, '''', '''''') + N'''';
    EXEC sp_executesql @createKey;
END
GO

DECLARE @drop NVARCHAR(MAX) = N'IF EXISTS (SELECT 1 FROM sys.database_scoped_credentials WHERE name = ''$(OPENAI_ENDPOINT)'') ' +
    N'DROP DATABASE SCOPED CREDENTIAL ' + QUOTENAME('$(OPENAI_ENDPOINT)');
EXEC sp_executesql @drop;
GO

DECLARE @create NVARCHAR(MAX) = N'CREATE DATABASE SCOPED CREDENTIAL ' + QUOTENAME('$(OPENAI_ENDPOINT)') +
    N' WITH IDENTITY = ''Managed Identity'', SECRET = ''{"resourceid":"https://cognitiveservices.azure.com"}''';
EXEC sp_executesql @create;
GO
