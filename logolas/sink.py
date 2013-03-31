"""
Sink is responsible for persisting parsed lines to the database.

Additionally it provides deduplication.
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

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

        # This value can be None at start or if the table is empty.
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
