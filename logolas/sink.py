"""
Sink is responsible for persisting parsed lines to the database.

Additionally it provides deduplication.
"""
from sqlalchemy import Table, Column, Integer, DateTime, String
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import mapper, sessionmaker

import logging

_LOG = logging.getLogger(__name__)

class Sink: #pylint: disable=R0903
    """Persist parsed lines to the database."""

    def __init__(self, engine, table, model):
        self.engine = engine
        self.sessionmaker = sessionmaker(bind=engine)
        self.table = table
        self.model = model
        self.latest_at_start = None

    def _get_latest(self, session):
        """Get the time for the latest entry in this Sink."""
        latest = session.query(func.max(self.table.columns.time)).scalar()

        _LOG.debug("Latest entry in %s %s", self.table, latest)

        return latest

    def sink(self, entries):
        """Persist the lines to the database."""

        session = self.sessionmaker()

        if self.latest_at_start == None:
            self.latest_at_start = self._get_latest(session)

        for entry in entries:

            if self.latest_at_start == None or entry['time'] >= self.latest_at_start:

                query = session.query(func.count(self.table.columns.time))

                for field, value in entry.items():
                    query = query.filter(self.table.columns.get(field) == value)

                if 0 == query.scalar():
                    _LOG.info("%s : %s", entry['time'], entry.values())

                    session.add(self.model(entry))

        session.commit()

    @staticmethod
    def generate_table(metadata, name, fields):
        """Generate a table for a Sink."""

        table = Table(
            name,
            metadata,
            Column('id', Integer, primary_key=True),
            Column('time', DateTime)
        )

        for field in fields:
            if field not in ['time', 'date']:
                table.append_column(Column(field, String))

        return table

    @staticmethod
    def generate_model(table):
        """Generate a model given a table."""

        class Model(object):
            """Hackidacorus code to allow for dynamic Model generation."""
            def __init__(self, entry):
                for field, value in entry.items():
                    self.__dict__[field] = value

        mapper(Model, table)

        return Model

    @staticmethod
    def generate_sink(engine, metadata, name, fields):
        """Generate a Sink."""

        table = Sink.generate_table(metadata, name, fields)
        model = Sink.generate_model(table)

        return Sink(engine, table, model)
