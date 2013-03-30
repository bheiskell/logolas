"""
Handler is the controller for reading and dispatching updates to files.
"""

# HACK: container for the configuration to object mapping / buisness logic
class Handler:
    """Listen and dispatch file updates."""

    def __init__(self, log_files, parsers, sinks):
        self.log_files = log_files
        self.parsers   = parsers
        self.sinks     = sinks

    def reload(self, filename):
        """Reload a file."""

        print "Reloading %s" % filename
        self.log_files[filename].reload()

    def handle_all(self):
        """Handle all files."""

        for filename in self.log_files.keys():
            self.handle(filename)

    def handle(self, filename):
        """Handle changes to a file."""

        lines = self.log_files[filename].read()
        for parser in self.parsers[filename]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)
