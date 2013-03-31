"""Test the Configuration."""

from logolas.configuration import Configuration
from unittest import TestCase
from tempfile import NamedTemporaryFile
from yaml import dump

#pylint: disable=R0904

class TestConfiguration(TestCase):
    """Test the dynamic creation of models."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""
        self.config = Configuration()

    def test_load_yaml(self):
        """Test the actual loading of yaml."""

        tmpfile = NamedTemporaryFile()
        dump({ 'version': Configuration.version }, tmpfile)
        self.config.load_yaml(tmpfile.name)

    def test_mismatch(self):
        """Test the loading of old yaml."""

        tmpfile = NamedTemporaryFile()
        dump({ 'version': -1 }, tmpfile)
        self.assertRaises(ValueError, self.config.load_yaml, tmpfile.name)

    def test_db_uri(self):
        """Test database URI retrieval"""
        self.config.configuration = { 'database': 'test' }

        self.assertEquals('test', self.config.get_database_uri())

    def test_file_to_patterns(self):
        """Verify the response of file_to_patterns"""
        self.config.configuration = {
            'files': [
                {
                    'path': '/path',
                    'patterns': [
                        { 'name': 'pattern1', 'key': 'x' },
                        { 'name': 'pattern2', 'key': 'x' },
                    ],
                },
                {
                    'path': '/path/two',
                    'patterns': [
                        { 'name': 'pattern3', 'key': 'x' },
                        { 'name': 'pattern4', 'key': 'x' },
                    ],
                },
            ]
        }

        ftop = self.config.get_file_to_patterns()

        for filename, patterns in ftop.items():
            for name, pattern in patterns.items():

                self.assertEquals(name, pattern['name'])
                self.assertEquals('x', pattern['key'])

                if name in ['pattern3', 'pattern4']:
                    self.assertEquals('/path/two', filename)
                else:
                    self.assertEquals('/path', filename)
