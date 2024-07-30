import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Enable foreign key constraints
        g.db.execute("PRAGMA foreign_keys = ON;")

    return g.db


# when close_db is automatically called bacause of app.teardown_appcontext(close_db) after every request
# if an unhandled exception occurs, the error will be passed to close_db, hence the e=None to escape a type error
def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo("Initialized the database.")


# This function needs to be called in the foundry, otherwise the application instance would not be available
def init_app(app):
    # close_db will be called after every http request
    app.teardown_appcontext(close_db)
    # add this cli command to the flask application
    app.cli.add_command(init_db_command)
