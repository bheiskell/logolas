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

    return jsonify(fields=current_app.config['logolas_fields'])

def _get_filters():
    """Extract the filters from the URL."""
    filters = {}

    for parameter, argument in request.args.items():
        match = re.search(r'filters\[([0-9]+)\]\[([a-z]+)\]', parameter)
        current_app.logger.debug("Filters %s", parameter)
        if match:
            (_index, _field) = match.groups()
            if not _index in filters:
                filters[_index] = {}
            filters[_index][_field] = argument

    current_app.logger.debug(filters)

    return filters.values()

def _applicable(columns, filters):
    """Determines if this filter is applicable to these columns."""
    result = True

    for _filter in filters:
        if _filter['column'] not in [ x.name for x in columns ]:
            result = False

            current_app.logger.debug("Column %s not found in %s", _filter['column'], columns)

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
            pass

        if logic is None:
            logic = conditional
        elif _filter['conditional'] == 'AND':
            logic = and_(conditional, logic)
        elif _filter['conditional'] == 'OR':
            logic = or_(conditional, logic)
        else:
            pass
        current_app.logger.debug(logic)

    # If no logic is set, it's easier to just return true for use in the filter.
    if logic is None:
        logic = True

    return logic

@logolas.route('/log')
def log():
    """Retrieve log entries."""

    limit = request.args['limit']
    filters = _get_filters()
    tables = current_app.config['logolas_tables']

    current_app.logger.debug("Request (limit %s) %s", limit, filters)
    current_app.logger.debug(tables)

    results = {}
    for (table, model) in tables:
        if _applicable(table.columns, filters):
            query = db.session.query(model)

            columns = dict((column.name, column) for column in table.columns)

            logic = _get_logic(columns, filters)

            query = query.filter(logic).order_by(desc(columns['time'])).limit(limit)

            current_app.logger.debug(query)

            results[table.name] = query.all()

    logs = []
    for table_name, result in results.items():
        for row in result:
            logs.append({
                'time': str(row.time),
                'id':   row.id,
                'type': table_name,
                'hash': '%s%s' % (table_name, row.id),
                'data': row.get_data(),
            })

    logs = sorted(logs, key=lambda x: x['time'])
    logs = logs[-int(limit):]

    current_app.logger.debug(logs)
    return jsonify(logs=logs)
