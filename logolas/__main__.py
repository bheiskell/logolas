"""Logolas log watching process."""

from logolas.configuration import Configuration
from logolas.handler import Handler
from logolas.logfile import LogFile
from logolas.parser import Parser
from logolas.sink import Sink

from sqlalchemy import create_engine, Table, Column, Integer, DateTime, String, MetaData

import logging

_LOG = logging.getLogger(__name__)

def test(regexs, tests):
    """Perform tests."""

    for pattern, regex in regexs.items():
        parser = Parser(regex['regex'], regex['order'], regex['datetime-format'])
        matches = parser.parse(tests[pattern])

        _LOG.info("Pattern %s", pattern)
        for match in matches:
            _LOG.info("\t%s", match)

        if len(matches) < len(tests[pattern]):
            raise ValueError("Not all configured tests matched the regex!")


def main():
    """Begin watching logs."""

    logging.basicConfig(level=logging.DEBUG)

    configuration = Configuration()
    configuration.load_yaml('sample/config.yml')

    engine = create_engine('sqlite:///:memory:', pool_recycle=3600)
    metadata = MetaData()

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
            parser = Parser(
                regexs[category]['regex'],
                regexs[category]['order'],
                regexs[category]['datetime-format'],
            )

            parsers[filename].append(parser)

            model = Table(
                category,
                metadata,
                Column('id', Integer, primary_key=True),
                Column('time', DateTime)
            )

            for field in models[category]:
                model.append_column(Column(field, String))

            sinks[parser] = Sink(
                engine=engine,
                model=model
            )

    metadata.create_all(engine)

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
