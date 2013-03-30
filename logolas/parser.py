"""Parses a list of lines given a regular expression."""
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
                results.append(result)

        # TODO: add handling of datetime format

        return results
