import sqlalchemy as sla


# DONE: ppd_user can create table on ppd_staging
# TODO: ppd_user can update table on ppd_staging
# TODO: ppd_user can delete table on ppd_staging

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


# def test_ppd_user_user_can_insert_features_on_ppd_staging(
#         db_users,
#         db_admin_credentials,
#         db_users_credentials
# ):
#     engine = _connect_to_db('ppd_user1', db_admin_credentials, db_users_credentials)
#     table_name = 'ppd_staging."ppd_roads_v0.0.1"'
#     with engine.connect() as connection:
#         with connection.begin() as transaction:
#             create_result = connection.execute(
#                 f'CREATE TABLE {table_name} '
#                 f'(id serial, road_name text, geom geometry(LINESTRING, 4326))'
#             )
#             update_result = connection.execute(
#                 f'INSERT INTO {table_name} (road_name, geom) VALUES '
#                 f'(\'dummy\', \'ST_GeomFromText(\'LINESTRING(191232 243118,191108 243242))\', 4326\')'
#             )
#             transaction.rollback()


def _connect_to_db(name, db_credentials, users_credentials):
    engine = sla.create_engine(
        f'postgresql://{name}:{users_credentials[name][0]}@'
        f'{db_credentials["host"]}:'
        f'{db_credentials["port"]}/'
        f'{db_credentials["db"]}'
    )
    return engine
