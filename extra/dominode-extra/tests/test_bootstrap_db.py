import sqlalchemy as sla
from sqlalchemy import exc

import pytest

# TODO: regular user is not able to update existing features on public table
# TODO: regular user is not able to insert new features on public table
# TODO: regular user is not able to delete features from public table
# TODO: regular user is not able to drop public table


@pytest.mark.parametrize('username, schemaname', [
    pytest.param('ppd_user1', 'ppd_staging'),
    pytest.param('ppd_user1', 'dominode_staging'),
])
def test_user_can_create_tables_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname', [
    pytest.param('ppd_editor1', 'public'),
])
def test_editor_user_can_create_tables_on_public(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname', [
    pytest.param('ppd_user1', 'public', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_regular_user_cannot_create_tables_on_public(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname, expected_owner', [
    pytest.param('ppd_user1', 'ppd_staging', 'ppd_user'),
    pytest.param('ppd_user1', 'dominode_staging', 'ppd_user'),
])
def test_user_can_call_setStagingPermissions_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname,
        expected_owner
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    unqualified_table_name = f'{user_department}_roads_v0.01'
    table_name = f'{schemaname}."{unqualified_table_name}"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            owner_result = connection.execute(
                sla.text(
                    f'SELECT tableowner from pg_tables WHERE schemaname = :schema AND tablename = :table'
                ),
                schema=schemaname,
                table=unqualified_table_name
            )
            owner = owner_result.scalar()
            assert owner == expected_owner
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_user1', 'ppd_staging'),
    pytest.param('ppd_user1', 'dominode_staging'),
])
def test_user_can_insert_features_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            insert_result = connection.execute(
                insert_query,
                name='dummy',
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_user1', 'ppd_staging'),
    pytest.param('ppd_user1', 'dominode_staging'),
])
def test_user_can_update_features_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            original_name = 'dummy'
            insert_result = connection.execute(
                insert_query,
                name=original_name,
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
            update_query = sla.text(
                f'UPDATE {table_name} SET road_name = :new_name WHERE road_name = :original_name'
            )
            update_result = connection.execute(
                update_query,
                new_name='new_dummy',
                original_name=original_name
            )
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_user1', 'ppd_staging'),
    pytest.param('ppd_user1', 'dominode_staging'),
])
def test_user_can_delete_table_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            connection.execute(f'DROP TABLE {table_name}')
            transaction.rollback()


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'ppd_user2', 'ppd_staging'),
    pytest.param('ppd_user1', 'ppd_user2', 'dominode_staging'),
])
def test_same_department_user_can_insert_features_on_table_created_by_another_user_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname,

):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        with connection.begin() as transaction:
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            insert_result = connection.execute(
                insert_query,
                name='dummy',
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
    # clean up the DB
    with creator_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'ppd_user2', 'ppd_staging'),
    pytest.param('ppd_user1', 'ppd_user2', 'dominode_staging'),
])
def test_same_department_user_can_update_features_on_table_created_by_another_user_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname,
):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            original_name = 'dummy'
            insert_result = connection.execute(
                insert_query,
                name=original_name,
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        with connection.begin() as transaction:
            update_query = sla.text(
                f'UPDATE {table_name} SET road_name = :new_name WHERE road_name = :original_name'
            )
            update_result = connection.execute(
                update_query,
                new_name='new_dummy',
                original_name=original_name
            )
    # clean up the DB
    with creator_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'ppd_user2', 'ppd_staging'),
    pytest.param('ppd_user1', 'ppd_user2', 'dominode_staging'),
])
def test_same_department_user_can_delete_table_created_by_another_user_on_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname
):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('username, schemaname', [
    pytest.param('ppd_user1', 'lsd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_editor1', 'lsd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_user_cannot_create_tables_on_another_department_staging_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            transaction.rollback()


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'lsd_user1', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_user1', 'lsd_user1', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_user_cannot_insert_features_on_table_owned_by_another_department(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname,

):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        with connection.begin() as transaction:
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            insert_result = connection.execute(
                insert_query,
                name='dummy',
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
    # clean up the DB
    with creator_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'lsd_user1', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_user1', 'lsd_user1', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_user_cannot_update_features_on_table_owned_by_another_department(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname,
):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            original_name = 'dummy'
            insert_result = connection.execute(
                insert_query,
                name=original_name,
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        with connection.begin() as transaction:
            update_query = sla.text(
                f'UPDATE {table_name} SET road_name = :new_name WHERE road_name = :original_name'
            )
            update_result = connection.execute(
                update_query,
                new_name='new_dummy',
                original_name=original_name
            )
    # clean up the DB
    with creator_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('creator_username, modifier_username, schemaname', [
    pytest.param('ppd_user1', 'ppd_user2', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_user1', 'ppd_user2', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_user_cannot_delete_table_owned_by_another_department(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        creator_username,
        modifier_username,
        schemaname
):
    creator_engine = _connect_to_db(creator_username, db_admin_credentials, db_users_credentials)
    creator_department = creator_username.partition('_')[0]
    table_name = f'{schemaname}."{creator_department}_roads_v0.0.1"'
    with creator_engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
    modifier_engine = _connect_to_db(modifier_username, db_admin_credentials, db_users_credentials)
    with modifier_engine.connect() as connection:
        connection.execute(f'DROP table {table_name}')


@pytest.mark.parametrize('username, schemaname, expected_owner', [
    pytest.param('ppd_user1', 'ppd_staging', 'ppd_user'),
    pytest.param('ppd_user1', 'dominode_staging', 'ppd_user'),
    pytest.param('lsd_user1', 'lsd_staging', 'lsd_user'),
])
def test_user_can_call_moveTableToDominodeStagingSchema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname,
        expected_owner
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    unqualified_table_name = f'{user_department}_roads_v0.01'
    table_name = f'{schemaname}."{unqualified_table_name}"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            connection.execute(
                sla.text(f'SELECT moveTableToDominodeStagingSchema(\'{table_name}\')')
            )
            owner_result = connection.execute(
                sla.text(
                    f'SELECT tableowner from pg_tables WHERE schemaname = :schema AND tablename = :table'
                ),
                schema='dominode_staging',
                table=unqualified_table_name
            )
            owner = owner_result.scalar()
            assert owner == expected_owner
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname, expected_owner', [
    pytest.param('ppd_user1', 'ppd_staging', 'ppd_user'),
    pytest.param('ppd_user1', 'dominode_staging', 'ppd_user'),
    pytest.param('lsd_user1', 'lsd_staging', 'lsd_user'),
])
def test_user_can_call_moveTableToDominodeStagingSchema_without_calling_setStagingPermissions_first(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname,
        expected_owner
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    unqualified_table_name = f'{user_department}_roads_v0.01'
    table_name = f'{schemaname}."{unqualified_table_name}"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT moveTableToDominodeStagingSchema(\'{table_name}\')')
            )
            owner_result = connection.execute(
                sla.text(
                    f'SELECT tableowner from pg_tables WHERE schemaname = :schema AND tablename = :table'
                ),
                schema='dominode_staging',
                table=unqualified_table_name
            )
            owner = owner_result.scalar()
            assert owner == expected_owner
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname, expected_owner', [
    pytest.param('ppd_editor1', 'ppd_staging', 'ppd_user'),
    pytest.param('ppd_editor1', 'dominode_staging', 'ppd_user'),
    pytest.param('lsd_editor1', 'lsd_staging', 'lsd_user'),
    pytest.param('lsd_editor1', 'dominode_staging', 'lsd_user'),
])
def test_editor_user_can_call_moveTableToPublicSchema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname,
        expected_owner
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    unqualified_table_name = f'{user_department}_roads_v0.01'
    table_name = f'{schemaname}."{unqualified_table_name}"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT moveTableToDominodeStagingSchema(\'{table_name}\')')
            )
            owner_result = connection.execute(
                sla.text(
                    f'SELECT tableowner from pg_tables WHERE schemaname = :schema AND tablename = :table'
                ),
                schema='dominode_staging',
                table=unqualified_table_name
            )
            owner = owner_result.scalar()
            assert owner == expected_owner
            transaction.rollback()


@pytest.mark.parametrize('username, schemaname, expected_owner', [
    pytest.param('ppd_user1', 'ppd_staging', 'ppd_user', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_user1', 'dominode_staging', 'ppd_user', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('lsd_user1', 'lsd_staging', 'lsd_user', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('lsd_user1', 'dominode_staging', 'lsd_user', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_regular_user_cannot_call_moveTableToPublicSchema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname,
        expected_owner
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    unqualified_table_name = f'{user_department}_roads_v0.01'
    table_name = f'{schemaname}."{unqualified_table_name}"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT moveTableToPublicSchema(\'{table_name}\')')
            )
            owner_result = connection.execute(
                sla.text(
                    f'SELECT tableowner from pg_tables WHERE schemaname = :schema AND tablename = :table'
                ),
                schema='public',
                table=unqualified_table_name
            )
            owner = owner_result.scalar()
            assert owner == expected_owner
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_editor1', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_editor1', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_editor_user_cannot_insert_features_on_public_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            connection.execute(
                sla.text(f'SELECT moveTableToPublicSchema(\'{table_name}\')')
            )
            public_table_name = table_name.replace(schemaname, 'public')
            insert_query = sla.text(
                f'INSERT INTO {public_table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            insert_result = connection.execute(
                insert_query,
                name='dummy',
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_editor1', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_editor1', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_editor_user_cannot_update_features_on_public_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            original_name = 'dummy'
            insert_result = connection.execute(
                insert_query,
                name=original_name,
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
            connection.execute(
                sla.text(f'SELECT moveTableToPublicSchema(\'{table_name}\')')
            )
            public_table_name = table_name.replace(schemaname, 'public')
            update_query = sla.text(
                f'UPDATE {public_table_name} SET road_name = :new_name WHERE road_name = :original_name'
            )
            update_result = connection.execute(
                update_query,
                new_name='new_dummy',
                original_name=original_name
            )
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_editor1', 'ppd_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
    pytest.param('ppd_editor1', 'dominode_staging', marks=pytest.mark.raises(exception=exc.ProgrammingError)),
])
def test_editor_user_cannot_delete_features_on_public_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            insert_query = sla.text(
                f'INSERT INTO {table_name} (road_name, geom) VALUES (:name, ST_GeomFromText(:geom, 4326))'
            )
            original_name = 'dummy'
            insert_result = connection.execute(
                insert_query,
                name=original_name,
                geom='LINESTRING(-71.160 42.258, -71.160 42.259, -71.161 42.25)'
            )
            connection.execute(
                sla.text(f'SELECT moveTableToPublicSchema(\'{table_name}\')')
            )
            public_table_name = table_name.replace(schemaname, 'public')
            update_query = sla.text(
                f'DELETE FROM {public_table_name} WHERE road_name = :original_name'
            )
            update_result = connection.execute(
                update_query,
                original_name=original_name
            )
            transaction.rollback()


@pytest.mark.parametrize('username,schemaname', [
    pytest.param('ppd_editor1', 'ppd_staging'),
    pytest.param('ppd_editor1', 'dominode_staging'),
])
def test_editor_user_can_delete_table_from_public_schema(
        db_users,
        db_admin_credentials,
        db_users_credentials,
        username,
        schemaname
):
    engine = _connect_to_db(username, db_admin_credentials, db_users_credentials)
    user_department = username.partition('_')[0]
    table_name = f'{schemaname}."{user_department}_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            existing_tables_result = connection.execute(
                sla.text('SELECT tablename FROM pg_tables WHERE schemaname = :schema'), schema=schemaname)
            print('previously existing tables:')
            for row in existing_tables_result:
                print(row)
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(
                sla.text(f'SELECT setStagingPermissions(\'{table_name}\')')
            )
            connection.execute(
                sla.text(f'SELECT moveTableToPublicSchema(\'{table_name}\')')
            )
            public_table_name = table_name.replace(schemaname, 'public')
            connection.execute(f'DROP TABLE {public_table_name}')
            transaction.rollback()




def _connect_to_db(name, db_credentials, users_credentials):
    engine = sla.create_engine(
        f'postgresql://{name}:{users_credentials[name][0]}@'
        f'{db_credentials["host"]}:'
        f'{db_credentials["port"]}/'
        f'{db_credentials["db"]}'
    )
    return engine
