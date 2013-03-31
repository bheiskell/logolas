"""Handle URL format for defining filters."""

import re

def get_filters(args):
    """Extract the filters from the URL."""
    filters = {}

    for parameter, argument in args.items():
        match = re.search(r'filters\[([0-9]+)\]\[([a-z]+)\]', parameter)
        if match:
            (index, field) = match.groups()
            if not index in filters:
                filters[index] = {}
            filters[index][field] = argument

    return filters.values()
