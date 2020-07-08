-- DDL commands to bootstrap the DomiNode DB

--  TODO: Add a function to copy a table back to the staging area so that it may be modified safely

-- Create group roles
-- Create staging schemas and assign access permissions
-- Tweak public schema's permissions
-- Create styles table
-- Install helper functions

-- -----
-- ROLES
-- -----

CREATE ROLE admin WITH CREATEDB CREATEROLE;
CREATE ROLE replicator WITH REPLICATION;

CREATE ROLE dominode_user;
CREATE ROLE editor IN ROLE dominode_user;

CREATE ROLE ppd_user IN ROLE dominode_user;
CREATE ROLE ppd_editor IN ROLE ppd_user, editor;

CREATE ROLE lsd_user IN ROLE dominode_user;
CREATE ROLE lsd_editor IN ROLE lsd_user, editor;

-- ---------------
-- STAGING SCHEMAS
-- ---------------

CREATE SCHEMA IF NOT EXISTS dominode_staging AUTHORIZATION editor;
CREATE SCHEMA IF NOT EXISTS ppd_staging AUTHORIZATION ppd_editor;
CREATE SCHEMA IF NOT EXISTS lsd_staging AUTHORIZATION lsd_editor;

-- Grant schema access to the relevant roles
GRANT USAGE, CREATE ON SCHEMA dominode_staging TO dominode_user;
GRANT USAGE, CREATE ON SCHEMA ppd_staging TO ppd_user;
GRANT USAGE, CREATE ON SCHEMA lsd_staging TO lsd_user;

-- -------------
-- PUBLIC SCHEMA
-- -------------

-- Create the `layer_styles` table which is used by QGIS to save styles
CREATE TABLE IF NOT EXISTS public.layer_styles
(
    id                serial not null
        constraint layer_styles_pkey
            primary key,
    f_table_catalog   varchar,
    f_table_schema    varchar,
    f_table_name      varchar,
    f_geometry_column varchar,
    stylename         text,
    styleqml          xml,
    stylesld          xml,
    useasdefault      boolean,
    description       text,
    owner             varchar(63) default CURRENT_USER,
    ui                xml,
    update_time       timestamp   default CURRENT_TIMESTAMP
);

ALTER TABLE public.layer_styles OWNER TO editor;
GRANT SELECT ON public.layer_styles TO dominode_user;


-- Create helper functions in order to facilitate loading datasets

CREATE OR REPLACE FUNCTION setStagingPermissions(qualifiedTableName varchar) RETURNS VOID AS $functionBody$
--   1. assign ownership to the group role
--
--      ALTER TABLE ppd_staging."ppd_rrmap_v0.0.1-staging" OWNER TO ppd_editor;
--
--   2. Grant relevant permissions to users
--
--      GRANT SELECT ON ppd_staging."ppd_rrmap_v0.0.1-staging" TO ppd_user;
    DECLARE
        unqualifiedName varchar;
        schemaName varchar;
        schemaDepartment varchar;
        userRoleName varchar;
    BEGIN
        schemaName := split_part(qualifiedTableName, '.', 1);
        unqualifiedName := replace(qualifiedTableName, concat(schemaName, '.'), '');
        unqualifiedName := replace(unqualifiedName, '"', '');
        schemaDepartment := split_part(unqualifiedName, '_', 1);
        userRoleName := concat(schemaDepartment, '_user');
        EXECUTE format('ALTER TABLE %s OWNER TO %I', qualifiedTableName, userRoleName);
    END

    $functionBody$
    LANGUAGE  plpgsql;


CREATE OR REPLACE FUNCTION moveTableToDominodeStagingSchema(qualifiedTableName varchar) RETURNS VOID AS $functionBody$
    -- Move a table from a department's internal schema to the project-wide internal staging schema
    --
    -- Tables in the department's staging schema are only readable by deparment members, while those
    -- on the project-wide staging schema are readable by all users (but they are only editable by
    -- department members).
    --

DECLARE
    schemaName varchar;
    unqualifiedName varchar;
    newQualifiedName varchar;
BEGIN
    schemaName := split_part(qualifiedTableName, '.', 1);
    unqualifiedName := replace(qualifiedTableName, concat(schemaName, '.'), '');
    newQualifiedName := concat('dominode_staging.', format('%s', unqualifiedName));
    PERFORM setStagingPermissions(qualifiedTableName);
    -- EXECUTE format('SELECT setStagingPermissions(%s)', qualifiedTableName);
    EXECUTE format('ALTER TABLE %s SET SCHEMA dominode_staging', qualifiedTableName);
    EXECUTE format('GRANT SELECT ON %s TO dominode_user', newQualifiedName);

END
$functionBody$
    LANGUAGE  plpgsql;


CREATE OR REPLACE FUNCTION moveTableToPublicSchema(qualifiedTableName varchar) RETURNS VOID AS $functionBody$
    -- Move a table from a department's internal schema to the public schema
    --
    -- Moved table is renamed and assigned proper permissions.
    --
    -- Example usage:
    --
    -- SELECT moveToPublicSchema('ppd_staging."ppd_schools_v0.0.1"')
    --
    --

    DECLARE
        schemaName varchar;
        unqualifiedName varchar;
        publicQualifiedName varchar;
        ownerRole varchar;
    BEGIN
        schemaName := split_part(qualifiedTableName, '.', 1);
        unqualifiedName := replace(qualifiedTableName, concat(schemaName, '.'), '');
        unqualifiedName := replace(unqualifiedName, '"', '');
        publicQualifiedName := concat('public.', format('%I', unqualifiedName));
        EXECUTE format('SELECT tableowner FROM pg_tables where schemaname=%L AND tablename=%L', schemaName, unqualifiedName) INTO ownerRole;
        RAISE NOTICE 'schemaName: %', schemaName;
        RAISE NOTICE 'unqualifiedName: %', unqualifiedName;
        -- RAISE NOTICE 'newQualifiedName: %', newQualifiedName;
        -- RAISE NOTICE 'publicQualifiedName: %', publicQualifiedName;
        RAISE NOTICE 'ownerRole: %', ownerRole;
        EXECUTE format('ALTER TABLE %s SET SCHEMA public', qualifiedTableName);
        EXECUTE format('GRANT SELECT ON %s TO public', publicQualifiedName);
        EXECUTE format('REVOKE INSERT, UPDATE, DELETE ON %s FROM %I', publicQualifiedName, ownerRole);

    END
    $functionBody$
    LANGUAGE  plpgsql;




-- Disable creation of objects on the public schema by default
REVOKE CREATE ON SCHEMA public FROM public;

-- Grant permission to editors for creating new objects on the public schema
GRANT CREATE ON SCHEMA public TO editor;


-- After the initial setup is done, perform the following:

-- 1. Create initial users
-- PPD users
-- CREATE USER ppd_editor1 PASSWORD 'ppd_editor1' IN ROLE ppd_editor, admin;
-- CREATE USER ppd_editor2 PASSWORD 'ppd_editor2' IN ROLE ppd_editor;
-- CREATE USER ppd_user1 PASSWORD 'ppd_user1' IN ROLE ppd_user;
-- LSD users
-- CREATE USER lsd_editor1 PASSWORD 'lsd_editor1' IN ROLE lsd_editor;
-- CREATE USER lsd_editor2 PASSWORD 'lsd_editor2' IN ROLE lsd_editor;
-- CREATE USER lsd_user1 PASSWORD 'lsd_user1' IN ROLE lsd_user;

-- -----------------
-- Add a new dataset
-- -----------------

-- 2. Whenever a new dataset is added by an editor,
--   1. assign ownership to the group role
--
--   ALTER TABLE ppd_staging."ppd_rrmap_v0.0.1-staging" OWNER TO ppd_editor;
--
--   2. Grant relevant permissions to users
--
--   GRANT SELECT ON ppd_staging."ppd_rrmap_v0.0.1-staging" TO ppd_user;


-- ---------------------------------------------
-- Move layer to public (i.e. production) schema
-- ---------------------------------------------

-- 3. In order to move the dataset to the public (i.e. production) schema,
--   1. Tables in the public schema must be properly versioned, so first
--      rename the table in order to either:
--      -  remove any pre-release information from its name
--      -  ensure a proper version is included in the table name
--
--      ALTER TABLE ppd_staging."ppd_rrmap_v0.0.1-staging" RENAME TO "ppd_rrmap_v0.0.1";
--
--   2. Move the renamed table to the public schema
--
--      ALTER TABLE ppd_staging."ppd_rrmap_v0.0.1" SET SCHEMA public;
--
--   3. Grant relevant permissions to users
--
--      GRANT SELECT ON public."ppd_rrmap_v0.0.1" TO public;

--  moveToPublic(table, new_name)

-- useful psql commands:
--
-- dt ppd_staging.*
