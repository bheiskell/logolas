"""Logolas log watching process."""

from logolas.configuration import Configuration
from logolas.handler import Handler
from logolas.logfile import LogFile
from logolas.parser import Parser
from logolas.sink import Sink

from sqlalchemy import create_engine, MetaData

import logging

_LOG = logging.getLogger(__name__)

def test(files):
    """Perform tests."""

    for patterns in files.values():
        for pattern in patterns.values():
            parser = Parser(pattern['regex'], pattern['fields'], pattern['datetime-format'])
            matches = parser.parse(pattern['tests'])

            _LOG.info("Pattern %s", pattern)
            for match in matches:
                _LOG.info("\t%s", match)

            if len(matches) < len(pattern['tests']):
                raise ValueError("Not all configured tests matched the regex!")

def initialize_handler(configuration, engine):
    """Initialize the handler from configuration."""

    metadata = MetaData()

    files = {}
    parsers = {}
    sinks = {}
    for filename, patterns in configuration.get_file_to_patterns().items():

        files[filename] = LogFile(filename)
        parsers[filename] = []

        for name, pattern in patterns.items():
            parser = Parser(pattern['regex'], pattern['fields'], pattern['datetime-format'])

            parsers[filename].append(parser)

            sinks[parser] = Sink.generate_sink(engine, metadata, name, pattern['fields'])

    # SqlAlchemy will auto create tables, but it will not update existing ones.
    metadata.create_all(engine)

    handler = Handler(files, parsers, sinks)
    notifier = Handler.get_notifier(handler)

    # Kick off a scan before blocking on file updates.
    handler.handle_all()

    return notifier

def main():
    """Begin watching logs."""

    logging.basicConfig(level=logging.INFO)

    configuration = Configuration()
    configuration.load_yaml('sample/config.yml')

    engine = create_engine(configuration.get_database_uri(), pool_recycle=3600)

    test(configuration.get_file_to_patterns())

    notifier = initialize_handler(configuration, engine)

    while True:
        try:
            Handler.handle_events(notifier)

        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
