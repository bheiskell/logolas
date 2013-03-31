"""Helpers for querying tables using filters."""

from sqlalchemy import or_, and_

def is_search_applicable(columns, filters):
    """Determines if this filter is applicable to these columns."""
    result = True

    for _filter in filters:
        if _filter['column'] not in [ column.name for column in columns ]:
            result = False

    return result

def get_query_filter(columns, filters):
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
