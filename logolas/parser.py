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
            match = re.search(self.regex, line)
            if match:
                result = dict(zip(self.order, match.groups()))

                # standardize date & time to datetime
                if 'date' in result and 'time' in result:
                    result['datetime'] = "%s %s" % (result.pop('date'), result.pop('time'))

                # parse input datetime to an actual datetime object
                result['datetime'] = datetime.strptime(result['datetime'], self.datetime_format)

                results.append(result)

        return results
