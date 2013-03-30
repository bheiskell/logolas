"""Logolas log watching process."""

from logolas.configuration import Configuration
from logolas.handler import Handler
from logolas.logfile import LogFile
from logolas.parser import Parser
from logolas.sink import Sink
import pyinotify

def test(regexs, tests):
    """Perform tests."""

    for pattern, regex in regexs.items():
        parser = Parser(regex['regex'])
        results = parser.parse(tests[pattern])

        print "Pattern", pattern
        for result in results:
            _dict = dict(zip(regex['order'], result))
            print "\t", _dict

        if len(results) < len(tests[pattern]):
            raise ValueError("Not all configured tests matched the regex!")


def main():
    """Begin watching logs."""

    configuration = Configuration()
    configuration.load_yaml('sample/config.yml')

    test(configuration.get_regexs(), configuration.get_tests())

    models = configuration.get_models()
    regexs = configuration.get_regexs()
    parsers = {}
    log_files = {}
    sinks = {}
    for filename, categorys in configuration.get_files().items():

        log_files[filename] = LogFile(filename)

        parsers[filename] = []

        for category in categorys:
            parser = Parser(regexs[category]['regex'])
            parsers[filename].append(parser)

            sinks[parser] = Sink(
                category=category,
                fields=models[category],
                order=regexs[category]['order']
            )

        #handle(filename)

    handler = Handler(log_files, parsers, sinks)
    handler.handle_all()

    # pylint incorrectly reand the pyinotify constant #pylint: disable=E1101
    mask         = pyinotify.IN_MODIFY | pyinotify.IN_MOVE_SELF | pyinotify.IN_CLOSE_WRITE
    watchmanager = pyinotify.WatchManager()
    notifier     = pyinotify.Notifier(watchmanager, handler)

    for _file in configuration.get_files():
        watchmanager.add_watch(_file, mask)

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()

        except KeyboardInterrupt:
            notifier.stop()
            break

if __name__ == '__main__':
    main()
