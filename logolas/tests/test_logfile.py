"""Test the LogFile."""

from logolas.logfile import LogFile
from tempfile import NamedTemporaryFile
from unittest import TestCase

#pylint: disable=R0904

class TestLogFile(TestCase):
    """Test the LogFile."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""

        self.tmpfile = NamedTemporaryFile()
        self.tmpfile.write("test\ntest\ntest")
        self.tmpfile.flush()

        self.logfile = LogFile(self.tmpfile.name)

    def tearDown(self): #pylint: disable=C0103
        self.logfile.close()
        self.tmpfile.close()

    def test_read(self):
        """Test reading the file."""
        self.logfile.reload()
        self.assertEquals(3, len(self.logfile.read()))
        self.assertEquals(0, len(self.logfile.read()))

    def test_reload(self):
        """Test reloading the file."""
        self.assertEquals(3, len(self.logfile.read()))
        self.logfile.reload()
        self.assertEquals(3, len(self.logfile.read()))
