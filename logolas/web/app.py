"""Web application."""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy #pylint: disable=E0611,F0401
from logolas.model import get_table

db = SQLAlchemy() #pylint: disable=C0103

def _config(configuration):
    """Get Logolas web configuration."""

    fields = []
    for patterns in configuration.get_file_to_patterns().values():
        for pattern in patterns.values():
            fields.extend(pattern['fields'])

    fields = list(frozenset(fields))

    tables = []
    for patterns in configuration.get_file_to_patterns().values():
        for name, pattern in patterns.items():
            pair = get_table(db.metadata, name, pattern['fields'], pattern['order'])
            tables.append(pair)

    return { 'fields': fields, 'tables': tables }

def application(configuration):
    """Application factory."""

    app = Flask(__name__)

    from logolas.web.routes import logolas
    app.register_blueprint(logolas)

    app.config['SQLALCHEMY_DATABASE_URI'] = configuration.get_database_uri()

    db.init_app(app)

    app.config['logolas'] = _config(configuration)

    app.logger.debug(app.config['logolas'])

    return app
