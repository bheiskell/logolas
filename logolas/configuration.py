"""Load and return Logolas's configuration."""

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Configuration(object):
    """Logolas configuration"""

    version = 1

    def __init__(self):
        self.configuration = None

    def load_yaml(self, filename):
        """Load configuration from a yaml file."""

        with file(filename) as file_in:
            self.configuration = load(file_in, Loader=Loader)

        if not self.configuration['version'] == Configuration.version:
            raise ValueError('Version %s found - expected version %d' % (
                self.configuration['version'],
                Configuration.version
            ))

    def __str__(self):
        return dump(self.configuration, Dumper=Dumper, default_flow_style=False)

    def get_database_uri(self):
        """Get the database URI."""
        return self.configuration['database']

    def get_file_to_patterns(self):
        """Get a multi-dimensional dict representing filenames -> name -> pattern."""

        files = {}
        for _file in self.configuration['files']:
            filename = _file['path']
            files[filename] = {}

            for pattern in _file['patterns']:
                files[filename][pattern['name']] = pattern

        return files
