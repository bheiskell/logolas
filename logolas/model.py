"""Define tables dynamically from configuration."""

from collections import OrderedDict
from sqlalchemy import Table, Column, Integer, DateTime, String
from sqlalchemy.orm import mapper
import logging

_LOG = logging.getLogger(__name__)

IGNORED_COLUMNS=['id', 'time', 'date']

def get_table(metadata, name, fields, order):
    """
    Dynamically create the table and model class.

    * The table will by default have an auto-incrementing id and time datetime.
    * The id, date, and time in both fields and order are ignored.
    * The generated table is automatically added to the metadata and mapped to the model class.
    """

    table = Table(
        name,
        metadata,
        Column('id', Integer, primary_key=True),
        Column('time', DateTime)
    )

    for field in fields:
        if field not in IGNORED_COLUMNS:
            table.append_column(Column(field, String))

    class Model(object): #pylint: disable=R0903
        """This table's model class."""

        def __init__(self, entry):
            # enable the dynamic access to fields via accessors
            for field, value in entry.items():
                self.__dict__[field] = value

        def get_data(self):
            """Return 'data' components in an ordered dictionary"""

            result = OrderedDict()

            for field in order:
                if field not in IGNORED_COLUMNS:
                    result[field] = getattr(self, field)

            return result

    mapper(Model, table)

    return (table, Model)
