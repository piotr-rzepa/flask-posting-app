import os

import flask
import pymongo

CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
APP_NAME = os.getenv("APP_NAME")


def get_database() -> pymongo.database.Database:
    """Returns a database instance."""
    if "database" not in flask.g:
        client: pymongo.MongoClient = pymongo.MongoClient(
            CONNECTION_STRING,
            appname=APP_NAME,
        )
        try:
            flask.g.database = client[DATABASE_NAME]
        except pymongo.errors.ConnectionFailure:
            flask.current_app.logger.error(
                "Unable to connect to the server: {host}:{port}".format(
                    host=client.HOST,
                    port=client.PORT,
                ),
            )
        except pymongo.errors.InvalidName:
            flask.current_app.logger.error(
                "Invalid name used for database creation: {db_name}".format(
                    db_name=DATABASE_NAME,
                ),
            )
    return flask.g.database


def close_database(signal=None) -> None:
    """Closes a connection with database."""
    database: pymongo.database.Database = flask.g.pop("database", None)

    if database is not None:
        flask.current_app.logger.debug(
            "Closing the connection with the database: {db_name}".format(
                db_name=database.name,
            ),
        )
        database.client.close()
    return


def get_collection(name: str) -> pymongo.collection.Collection:
    """Return a collection of given name."""
    database = get_database()
    try:
        return database[name]
    except pymongo.errors.InvalidName:
        flask.current_app.logger.error(
            "Invalid name used for collection creation: {collection_name}".format(
                collection_name=name,
            ),
        )
