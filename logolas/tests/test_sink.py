"""Test the Sink."""

from datetime import datetime, timedelta
from logolas.model import get_table
from logolas.sink import Sink
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from unittest import TestCase

#pylint: disable=R0904

class TestSink(TestCase):
    """Test the Sink."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""

        engine = create_engine('sqlite:///:memory:')
        metadata = MetaData()

        (self.table, self.model) = get_table(
            metadata,
            'table',
            [ 'time', 'test1', 'test2' ],
            [ 'test2', 'test1' ],
        )

        metadata.create_all(engine)

        self.sessionmaker = sessionmaker(bind=engine)

        self.sink = Sink(self.sessionmaker, self.table, self.model)

    def test_empty_sink(self):
        """Testing a empty sink"""

        self.sink.sink([])

    def test_sink(self):
        """Testing a basic sink"""

        self.sink.sink([ { 'time': datetime.now() + timedelta(minutes=-1), 'test1': 'x', 'test2': 'y' } ])
        self.sink.sink([ { 'time': datetime.now(), 'test1': 'x', 'test2': 'y' } ])

        count = self.sessionmaker().query(func.count(self.table)).scalar()
        self.assertEquals(2, count)

    def test_duplicate_sink(self):
        """Testing a duplicate sink"""

        time = datetime.now()
        self.sink.sink([ { 'time': time, 'test1': 'x', 'test2': 'y' } ])
        self.sink.sink([ { 'time': time, 'test1': 'x', 'test2': 'y' } ])

        count = self.sessionmaker().query(func.count(self.table)).scalar()
        self.assertEquals(1, count)

    def test_old_sink(self):
        """Testing a old sink"""

        time = datetime.now()
        self.sink.sink([ { 'time': time, 'test1': 'x', 'test2': 'y' } ])
        self.sink.sink([ { 'time': time + timedelta(minutes=-1), 'test1': 'x', 'test2': 'y' } ])

        count = self.sessionmaker().query(func.count(self.table)).scalar()
        self.assertEquals(1, count)
