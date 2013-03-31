"""Define tables dynamically from configuration."""

from collections import OrderedDict
from sqlalchemy import Table, Column, Integer, DateTime, String

from sqlalchemy.orm import mapper
import logging

_LOG = logging.getLogger(__name__)

def get_table(metadata, name, fields, order):
    """
    Dynamically generate the Table and model class for a give Table and Fields.
    The schema will be added to the sqlalchemy.MetaData instance provided.
    """

    table = Table(
        name,
        metadata,
        Column('id', Integer, primary_key=True),
        Column('time', DateTime)
    )

    for field in fields:
        if field not in ['date', 'time']:
            table.append_column(Column(field, String))

    class Model(object): #pylint: disable=R0903
        """
        There's probably a better way to do this, but I need a model class for
        this table. This allows me to instantiate an ORM instance and add it to
        a SqlAlchemy session.
        """
        def __init__(self, entry):
            self.entry = entry
            for field, value in entry.items():
                self.__dict__[field] = value

        def get_data(self):
            """Return 'data' components in an ordered dictionary"""
            result = OrderedDict()

            for field in order:
                if field not in ['id', 'time', 'date']:
                    result[field] = getattr(self, field)

            return result

    mapper(Model, table)

    return (table, Model)
