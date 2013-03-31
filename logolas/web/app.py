"""Web application."""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy #pylint: disable=E0611,F0401
from logolas.model import get_table

db = SQLAlchemy() #pylint: disable=C0103

def application(configuration):
    """Application factory."""
    app = Flask(__name__)

    from logolas.web.routes import logolas
    app.register_blueprint(logolas)

    app.config['SQLALCHEMY_DATABASE_URI'] = configuration.get_database_uri()

    db.init_app(app)

    fields = []

    for patterns in configuration.get_file_to_patterns().values():
        for pattern in patterns.values():
            fields.extend(pattern['fields'])

    app.logger.info("Fields %s:", fields)
    app.config['logolas_fields'] = list(frozenset(fields))

    app.config['logolas_tables'] = []
    metadata = db.metadata
    for patterns in configuration.get_file_to_patterns().values():
        for name, pattern in patterns.items():
            (table, model) = get_table(metadata, name, pattern['fields'], pattern['order']) #pylint: disable=W0612
            app.config['logolas_tables'].append((table, model))

    return app
