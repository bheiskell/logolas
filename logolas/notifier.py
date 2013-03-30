"""LogNotify is the callback used by pyinotify to handle events."""

from logolas.handler import Handler
import pyinotify

class LogNotifier(pyinotify.ProcessEvent):
    """Dispatch inotify events to the Handler."""

    def __init__(self, configuration):
        pyinotify.ProcessEvent.__init__(self)
        self.configuration = configuration
        self.handler = False

    # HACK: lazy initialization
    def setup_handler(self, handler=False):
        """Setup the inotify handler."""

        if not self.handler:
            if handler:
                self.handler = handler
            else:
                self.handler = Handler(
                    models=self.configuration.get_models(),
                    regexs=self.configuration.get_regexs(),
                    files=self.configuration.get_files(),
                )

    def process_IN_MOVE_SELF(self, event): #pylint: disable=C0103
        """Handle a file move event."""

        self.setup_handler()
        self.handler.reload(event.path)

    def process_IN_CLOSE_WRITE(self, event): #pylint: disable=C0103
        """Handle a file close write event."""

        self.setup_handler()
        self.handler.reload(event.path)

    def process_IN_MODIFY(self, event): #pylint: disable=C0103
        """Handle a file modify event."""

        self.setup_handler()
        self.handler.handle(event.path)

