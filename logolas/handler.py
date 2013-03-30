"""Handler is the callback used by pyinotify to handle events."""

import logging
import pyinotify

_LOG = logging.getLogger(__name__)

class Handler(pyinotify.ProcessEvent):
    """Dispatch inotify events to the Handler."""

    def __init__(self, log_files, parsers, sinks):
        self.log_files = log_files
        self.parsers   = parsers
        self.sinks     = sinks

        pyinotify.ProcessEvent.__init__(self)

    def process_IN_MOVE_SELF(self, event): #pylint: disable=C0103
        """Handle a file move event."""

        _LOG.debug("Entering process_IN_MOVE_SELF %s", event.path)
        self.reload(event.path)

    def process_IN_CLOSE_WRITE(self, event): #pylint: disable=C0103
        """Handle a file close write event."""

        _LOG.debug("Entering process_IN_CLOSE_WRITE %s", event.path)
        self.reload(event.path)

    def process_IN_MODIFY(self, event): #pylint: disable=C0103
        """Handle a file modify event."""

        _LOG.debug("Entering process_IN_MODIFY %s", event.path)
        self.handle(event.path)

    def reload(self, filename):
        """Reload a file."""

        _LOG.info("Reloading %s", filename)
        self.log_files[filename].reload()

    def handle_all(self):
        """Handle all files."""

        for filename in self.log_files.keys():
            self.handle(filename)

    def handle(self, filename):
        """Handle changes to a file."""

        _LOG.debug("Handling %s", filename)

        lines = self.log_files[filename].read()
        for parser in self.parsers[filename]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)
