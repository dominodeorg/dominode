import sqlalchemy as sla


# TODO: call setStaginPermissions() on all done tests
# DONE: ppd_user1 can create table on ppd_staging
# DONE: ppd_user1 can insert new features on table on ppd_staging
# DONE: ppd_user1 can update features on table on ppd_staging
# DONE: ppd_user1 can delete table on ppd_staging

# TODO: ppd_user2 can insert new features on table on ppd_staging created by ppd_user1
# TODO: ppd_user2 can update features on table on ppd_staging created by ppd_user1
# TODO: ppd_user2 can delete table on ppd_staging created by ppd_user1

# TODO: ppd_user can create table on dominode_staging
# TODO: ppd_user can update table on dominode_staging
# TODO: ppd_user can delete table on dominode_staging

# TODO: ppd_user can call setStagingPermissions() in order to set permissions
# TODO: ppd_user can call moveTableToDominodeStagingSchema() in order to set permissions
# TODO: ppd_user cannot call moveTableToPublicSchema()

# TODO: ppd_user cannot create table on lsd_staging
# TODO: ppd_user cannot update table on lsd_staging
# TODO: ppd_user cannot delete table on lsd_staging

# TODO: ppd_editor can call moveTableToPublicSchema()


def test_ppd_user1_user_can_create_tables_on_ppd_staging(
        db_users,
        db_admin_credentials,
        db_users_credentials,
):
    engine = _connect_to_db('ppd_user1', db_admin_credentials, db_users_credentials)
    table_name = 'ppd_staging."ppd_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            transaction.rollback()


def test_ppd_user_user_can_insert_features_on_ppd_staging(
        db_users,
        db_admin_credentials,
        db_users_credentials
):
    engine = _connect_to_db('ppd_user1', db_admin_credentials, db_users_credentials)
    table_name = 'ppd_staging."ppd_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
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


def test_ppd_user_user_can_update_features_on_ppd_staging(
        db_users,
        db_admin_credentials,
        db_users_credentials
):
    engine = _connect_to_db('ppd_user1', db_admin_credentials, db_users_credentials)
    table_name = 'ppd_staging."ppd_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
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


def test_ppd_user_user_can_delete_table_on_ppd_staging(
        db_users,
        db_admin_credentials,
        db_users_credentials
):
    engine = _connect_to_db('ppd_user1', db_admin_credentials, db_users_credentials)
    table_name = 'ppd_staging."ppd_roads_v0.0.1"'
    with engine.connect() as connection:
        with connection.begin() as transaction:
            create_result = connection.execute(
                f'CREATE TABLE {table_name} '
                f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
            )
            connection.execute(f'DROP TABLE {table_name}')
            transaction.rollback()


def _connect_to_db(name, db_credentials, users_credentials):
    engine = sla.create_engine(
        f'postgresql://{name}:{users_credentials[name][0]}@'
        f'{db_credentials["host"]}:'
        f'{db_credentials["port"]}/'
        f'{db_credentials["db"]}'
    )
    return engine
