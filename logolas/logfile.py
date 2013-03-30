"""LogFile is a simple model for maintaining and reloading file handles."""

class LogFile:
    """Maintains the filehandle for a given filename."""


    def __init__(self, filename):
        self.filename = filename
        self.filehandle = None
        self.load()

    def read(self):
        """Read all available lines."""

        return self.filehandle.readlines()

    def load(self):
        """Load the file."""

        self.filehandle = open(self.filename, 'r')

    def reload(self):
        """Reload the file."""

        self.close()
        self.load()

    def close(self):
        """Close the file."""

        self.filehandle.close()

