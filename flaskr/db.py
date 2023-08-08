import sqlite3
import click 
from flask import current_app, g

# g = special object that is unique for each request, used to store data that might be accessed by multiple functions during the request
# current_app = useful to access the app without needing to import it (cannot be imported when using application factory)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],    # establishes connection to file pointed at by DATABASE config key
            detect_types = sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row    # tells the connection to return rows that behave like dicts

    return g.db

def close_db(e=None):    # checks if the connection was created by checking if g.db was set
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()    # returns a database connection

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# defines a command line command that calls the init_db function and shows a success message to the user
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    app.teardown_appcontext(close_db)    # registers a function to be called when the application context is popped
    app.cli.add_command(init_db_command)   # adds a new command that can be called with the flask command