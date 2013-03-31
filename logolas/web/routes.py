"""Routes."""

from flask import render_template, jsonify, Blueprint, current_app, request
from flask.ext.sqlalchemy import SQLAlchemy #pylint: disable=E0611,F0401
from logolas.web.query import is_search_applicable, get_query_filter
from logolas.web.url import get_filters
from sqlalchemy import desc

logolas = Blueprint('logolas', __name__, template_folder='templates') #pylint: disable=C0103

db = SQLAlchemy() #pylint: disable=C0103

@logolas.route('/')
def index():
    """Render main index page."""
    return render_template('index.html')

@logolas.route('/field')
def field():
    """Retrieve fields list."""
    return jsonify(fields=current_app.config['logolas']['fields'])

@logolas.route('/log')
def log():
    """Retrieve log entries."""

    filters = get_filters(request.args)
    limit   = int(request.args['limit'])

    current_app.logger.debug("Request (limit %s) %s", limit, filters)

    logs = []
    for (table, model) in current_app.config['logolas']['tables']:
        if is_search_applicable(table.columns, filters):
            query = db.session.query(model)

            columns = dict((column.name, column) for column in table.columns)

            logic = get_query_filter(columns, filters)

            query = query.filter(logic).order_by(desc(columns['time'])).limit(limit)

            current_app.logger.debug(query)

            for row in query.all():
                logs.append({
                    'time': str(row.time),
                    'id':   row.id,
                    'type': table.name,
                    'hash': '%s%s' % (table.name, row.id), # hash is used by the UI to avoid collisions
                    'data': row.get_data(),
                })

    # The query sort is only to ensure the query limit gives us the right data set. Here we actually sort the results.
    logs = sorted(logs, key=lambda log: log['time'])

    # The query limit only narrows the number of results we get. Here we actually cut it off at limit.
    logs = logs[-limit:]

    return jsonify(logs=logs)
