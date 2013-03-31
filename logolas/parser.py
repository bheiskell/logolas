"""Parses a list of lines given a regular expression."""
from datetime import datetime
import re

class Parser: #pylint: disable=R0903
    """Regular expression parser given a set of lines."""

    def __init__(self, regex, order, datetime_format):
        self.regex = regex
        self.order = order
        self.datetime_format = datetime_format

    def parse(self, lines):
        """Parse the list with our regular expression. Return an dictionary of matches."""

        results = []

        for line in lines:
            match = re.search(self.regex, line.decode("utf-8"))

            if match:
                result = dict(zip(self.order, match.groups()))

                # Standardize date & time to datetime
                if 'date' in result and 'time' in result:
                    result['time'] = "%s %s" % (result.pop('date'), result.pop('time'))

                # Parse input datetime to an actual datetime object. Reusing
                # time here because some databases treat datetime as a key word.
                result['time'] = datetime.strptime(result['time'], self.datetime_format)

                results.append(result)

        return results
