"""
Sink is responsible for persisting parsed lines to the database.

Additionally it provides deduplication.
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import mapper

import logging

_LOG = logging.getLogger(__name__)

class Sink: #pylint: disable=R0903
    """Persist parsed lines to the database."""

    def __init__(self, engine=None, model=None):
        self.engine = engine
        self.sessionmaker = sessionmaker(bind=engine)
        self.table = model
        self.latest = None

        class Model(object):
            """Hackidacorus code to allow for dynamic Model generation."""
            def __init__(self, entry):
                for field, value in entry.items():
                    self.__dict__[field] = value

        self.model = Model

        mapper(self.model, self.table)

    def get_latest(self, session):
        """Get the time for the latest entry in this Sink."""
        self.latest = session.query(func.max(self.table.columns.time)).scalar()

        _LOG.info("Latest entry in %s %s", self.table, self.latest)

    def sink(self, entries):
        """Persist the lines to the database."""

        _LOG.error(dir())

        session = self.sessionmaker()

        if self.latest == None:
            self.get_latest(session)

        for entry in entries:

            if self.latest == None or entry['datetime'] >= str(self.latest):

                query = session.query(func.count(self.table.columns.time))

                for field, value in entry.items():
                    query = query.filter(self.table.columns.get(field) == value)

                if 0 == query.scalar():
                    _LOG.info("%s >= %s: %s", \
                        entry['datetime'], \
                        self.latest, \
                        entry.values())

                    session.add(self.model(entry))

        session.commit()

    @staticmethod
    def generate_model():
        """Generate a model for a Sink."""
        pass
