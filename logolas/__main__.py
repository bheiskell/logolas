"""Logolas log watching process."""

from logolas.configuration import Configuration
from logolas.handler import Handler
from logolas.logfile import LogFile
from logolas.parser import Parser
from logolas.sink import Sink
import logging

_LOG = logging.getLogger(__name__)

def test(regexs, tests):
    """Perform tests."""

    for pattern, regex in regexs.items():
        parser = Parser(regex['regex'])
        results = parser.parse(tests[pattern])

        _LOG.info("Pattern %s", pattern)
        for result in results:
            _dict = dict(zip(regex['order'], result))
            _LOG.info("\t%s", _dict)

        if len(results) < len(tests[pattern]):
            raise ValueError("Not all configured tests matched the regex!")


def main():
    """Begin watching logs."""

    logging.basicConfig(level=logging.DEBUG)

    configuration = Configuration()
    configuration.load_yaml('sample/config.yml')

    test(configuration.get_regexs(), configuration.get_tests())

    models = configuration.get_models()
    regexs = configuration.get_regexs()
    parsers = {}
    files = {}
    sinks = {}
    for filename, categories in configuration.get_files().items():

        files[filename] = LogFile(filename)

        parsers[filename] = []

        for category in categories:
            parser = Parser(regexs[category]['regex'])
            parsers[filename].append(parser)

            sinks[parser] = Sink(
                category=category,
                fields=models[category],
                order=regexs[category]['order']
            )

    handler = Handler(files, parsers, sinks)
    notifier = Handler.get_notifier(handler)
    handler.handle_all()
    while True:
        try:
            Handler.handle_events(notifier)

        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
