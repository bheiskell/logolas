"""Routes."""

from flask import render_template, jsonify, Blueprint, current_app, request
from flask.ext.sqlalchemy import SQLAlchemy #pylint: disable=E0611,F0401
from sqlalchemy import or_, and_, desc

import re

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

    filters = _get_filters(request.args)
    limit   = int(request.args['limit'])

    current_app.logger.debug("Request (limit %s) %s", limit, filters)

    logs = []
    for (table, model) in current_app.config['logolas']['tables']:
        if _applicable(table.columns, filters):
            query = db.session.query(model)

            columns = dict((column.name, column) for column in table.columns)

            logic = _get_logic(columns, filters)

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

def _get_filters(args):
    """Extract the filters from the URL."""
    filters = {}

    for parameter, argument in args.items():
        match = re.search(r'filters\[([0-9]+)\]\[([a-z]+)\]', parameter)
        if match:
            (_index, _field) = match.groups()
            if not _index in filters:
                filters[_index] = {}
            filters[_index][_field] = argument

    return filters.values()

def _applicable(columns, filters):
    """Determines if this filter is applicable to these columns."""
    result = True

    for _filter in filters:
        if _filter['column'] not in [ column.name for column in columns ]:
            result = False

    return result

def _get_logic(columns, filters):
    """Get boolean logic for the query filter."""
    logic = None
    for _filter in filters:
        conditional = None
        if _filter['operator'] == '==':
            conditional = columns[_filter['column']] == _filter['filter']
        elif _filter['operator'] == '>=':
            conditional = columns[_filter['column']] >= _filter['filter']
        elif _filter['operator'] == '<=':
            conditional = columns[_filter['column']] <= _filter['filter']
        elif _filter['operator'] == 'LIKE':
            conditional = columns[_filter['column']].like(_filter['filter'])
        else:
            raise ValueError('%s is not a valid operator', _filter['operator'])

        if logic is None:
            logic = conditional
        elif _filter['conditional'] == 'AND':
            logic = and_(conditional, logic)
        elif _filter['conditional'] == 'OR':
            logic = or_(conditional, logic)
        else:
            raise ValueError('%s is not a valid conditional', _filter['conditional'])

    # If no logic is set, it's easier to just return true for use in the filter.
    if logic is None:
        logic = True

    return logic

