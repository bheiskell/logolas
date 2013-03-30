"""Parses a list of lines given a regular expression."""
import re

class Parser: #pylint: disable=R0903
    """Regular expression parser given a set of lines."""

    def __init__(self, regex):
        self.regex = regex

    def parse(self, lines):
        """Parse the list with our regular expression. Return an ordered list of matches."""

        results = []

        for line in lines:
            match = re.search(self.regex, line)
            if match:
                results.append(match.groups())
        return results
