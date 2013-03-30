"""
Handler is the controller for reading and dispatching updates to files.
"""

from logolas.logfile import LogFile
from logolas.parser import Parser
from logolas.sink import Sink

# HACK: container for the configuration to object mapping / buisness logic
class Handler:
    """Listen and dispatch file updates."""

    def __init__(self, models=None, regexs=None, files=None):
        self.log_files = { } # filename: LogFile
        self.parsers   = { } # filename: [ Parser, ... ]
        self.sinks     = { } # Parser: Sink

        for filename, categorys in files.items():

            self.log_files[filename] = LogFile(filename)

            self.parsers[filename] = []

            for category in categorys:
                parser = Parser(regexs[category]['regex'])
                self.parsers[filename].append(parser)

                self.sinks[parser] = Sink(
                    category=category,
                    fields=models[category],
                    order=regexs[category]['order']
                )

            self.handle(filename)


    def reload(self, filename):
        """Reload a file."""

        print "Reloading %s" % filename
        self.log_files[filename].reload()

    def handle(self, filename):
        """Handle changes to a file."""

        lines = self.log_files[filename].read()
        for parser in self.parsers[filename]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)
