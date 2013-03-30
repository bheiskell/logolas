"""Handler is the callback used by pyinotify to handle events."""

import logging
import pyinotify

_LOG = logging.getLogger(__name__)

class Handler(pyinotify.ProcessEvent):
    """Dispatch inotify events to the Handler."""

    def __init__(self, files, parsers, sinks):
        pyinotify.ProcessEvent.__init__(self)

        self.files   = files
        self.parsers = parsers
        self.sinks   = sinks

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
        self.files[filename].reload()

    def handle_all(self):
        """Handle all files."""

        for filename in self.files.keys():
            self.handle(filename)

    def handle(self, filename):
        """Parse all new lines and sink the results."""

        _LOG.debug("Handling %s", filename)

        lines = self.files[filename].read()
        for parser in self.parsers[filename]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)

    @staticmethod
    def get_notifier(handler):
        """Factory for generating a pyinotify.Notifier compatible with Handler."""

        # pylint incorrectly reand the pyinotify constant #pylint: disable=E1101
        watchmanager = pyinotify.WatchManager()
        mask = pyinotify.IN_MODIFY | pyinotify.IN_MOVE_SELF | pyinotify.IN_CLOSE_WRITE

        filenames = handler.files.keys()

        for filename in filenames:
            watchmanager.add_watch(filename, mask)

        return pyinotify.Notifier(watchmanager, handler)

    @staticmethod
    def handle_events(notifier):
        """Wrapper for processing pyinotify.Notifier events."""

        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()

        except KeyboardInterrupt, exception:
            notifier.stop()
            raise exception

