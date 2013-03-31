"""Test the Parser."""

from logolas.parser import Parser
from unittest import TestCase

#pylint: disable=R0904

class TestParser(TestCase):
    """Test the Parser."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""

        self.parser = Parser(
            r'([0-9]+) ([0-9]+) ([a-z]+)',
            [ 'date', 'time', 'field' ],
            '%Y %H'
        )

    def test_parse(self):
        """Test a simple parsing circumstance."""

        results = self.parser.parse([ '1970 01 test', 'NO MATCH' ])

        self.assertEquals(1, len(results))

        self.assertEquals('test', results[0]['field'])
        self.assertEquals('1970-01-01 01:00:00', str(results[0]['time']))
