"""LogNotify is the callback used by pyinotify to handle events."""

import pyinotify

class LogNotifier(pyinotify.ProcessEvent):
    """Dispatch inotify events to the Handler."""

    def __init__(self, handler):
        pyinotify.ProcessEvent.__init__(self)
        self.handler = handler

    def process_IN_MOVE_SELF(self, event): #pylint: disable=C0103
        """Handle a file move event."""

        self.handler.reload(event.path)

    def process_IN_CLOSE_WRITE(self, event): #pylint: disable=C0103
        """Handle a file close write event."""

        self.handler.reload(event.path)

    def process_IN_MODIFY(self, event): #pylint: disable=C0103
        """Handle a file modify event."""

        self.handler.handle(event.path)

