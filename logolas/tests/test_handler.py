"""Test the Handler."""

from logolas.handler import Handler
from mock import MagicMock
from unittest import TestCase

#pylint: disable=R0904

class TestHandler(TestCase):
    """Test the Handler."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""

        self.test_file   = MagicMock()
        self.test_parser = MagicMock()
        self.test_sink   = MagicMock()

        self.files   = { '/test':          self.test_file }
        self.parsers = { '/test':          [ self.test_parser ] }
        self.sinks   = { self.test_parser: self.test_sink }

        self.handler = Handler(self.files, self.parsers, self.sinks)

    def test_reload(self):
        """Test Handler reloading"""
        self.handler.reload('/test')
        self.test_file.reload.assert_called_with()

    def test_handle(self):
        """Test Handler handle"""
        lines = [ 'test' ]
        results = [ {'test': 'test'} ]
        self.test_file.read.return_value = lines
        self.test_parser.parse.return_value = results

        self.handler.handle('/test')

        self.test_file.read.assert_called_with()
        self.test_parser.parse.assert_called_with(lines)
        self.test_sink.sink.assert_called_with(results)

    def test_handle_all(self):
        """Test Handler handle all"""
        self.handler.handle = MagicMock()

        self.handler.handle_all()

        self.handler.handle.assert_called_with('/test')
