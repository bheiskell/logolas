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

    def get_files(self):
        """Get a filename to pattern names mapping."""

        files = {}
        for _file in self.configuration['files']:
            files[_file['path']] = []
            for pattern in _file['patterns']:
                files[_file['path']].append(pattern['name'])

        return files

    def get_regexs(self):
        """Get a dictionary of pattern names to regex / extracted fields."""

        regexs = {}
        for _file in self.configuration['files']:
            for pattern in _file['patterns']:
                regexs[pattern['name']] = {
                    'regex': pattern['regex'],
                    'order': pattern['fields'],
                }

        return regexs

    def get_models(self):
        """Get a dictionary of pattern names to fields."""

        models = {}
        for _file in self.configuration['files']:
            for pattern in _file['patterns']:
                models[pattern['name']] = pattern['fields']

        return models

    def __str__(self):
        print "getste"
        return dump(self.configuration, Dumper=Dumper, default_flow_style=False)
