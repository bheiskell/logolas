"""Handler is the callback used by pyinotify to handle events."""

import logging
import pyinotify
from os.path import dirname

_LOG = logging.getLogger(__name__)

MASK = pyinotify.IN_MODIFY | pyinotify.IN_MOVE_SELF

class Handler(pyinotify.ProcessEvent):
    """Dispatch inotify events to the Handler."""

    def __init__(self, files, parsers, sinks):
        pyinotify.ProcessEvent.__init__(self)

        self.files   = files
        self.parsers = parsers
        self.sinks   = sinks
        self.watchmanager = None

    def set_watchmanager(self, watchmanager):
        """Set the watch manager used to lookup original filename in IN_MOVE_SELF."""
        self.watchmanager = watchmanager

    def process_IN_CREATE(self, event): #pylint: disable=C0103
        """Handle the creation of a previously watched file."""

        _LOG.debug("Entering process_IN_CREATE %s", event.path)

        for filename in self.files.keys():
            if filename.startswith(event.path):
                _LOG.info("Watched file has been recreated: %s", event.path)

                self.watchmanager.add_watch(filename, MASK)
                self.files[filename].load()

    def process_IN_MOVE_SELF(self, event): #pylint: disable=C0103
        """Handle the removal of a file and the unregistering from watch manager."""

        _LOG.info("Removing previous watch on moved file: %s", event.path)
        self.watchmanager.del_watch(event.wd)

    def process_IN_MODIFY(self, event): #pylint: disable=C0103
        """Handle a file modify event."""

        _LOG.debug("Entering process_IN_MODIFY %s", event.path)
        self.handle(event.path)

    def reload(self, filename):
        """Reload a file."""

        _LOG.info("Reloading %s", filename)
        self.files[filename].reload()

    def handle(self, filename):
        """Parse all new lines and sink the results."""

        _LOG.debug("Handling %s", filename)

        lines = self.files[filename].read()
        for parser in self.parsers[filename]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)

    def handle_all(self):
        """Handle all files."""

        for filename in self.files.keys():
            self.handle(filename)

    @staticmethod
    def get_notifier(handler):
        """Factory for generating a pyinotify.Notifier compatible with Handler."""

        # pylint incorrectly reand the pyinotify constant #pylint: disable=E1101
        watchmanager = pyinotify.WatchManager()

        filenames = handler.files.keys()

        for filename in filenames:
            watchmanager.add_watch(filename, MASK)
            watchmanager.add_watch(dirname(filename), pyinotify.IN_CREATE)

        handler.set_watchmanager(watchmanager)

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
