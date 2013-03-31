"""Test the dynamic creation of models."""

from collections import deque
from datetime import datetime
from logolas.model import get_table
from sqlalchemy import MetaData, DateTime, Integer
from sqlalchemy.exc import InvalidRequestError
from unittest import TestCase

#pylint: disable=R0904

class TestModels(TestCase):
    """Test the dynamic creation of models."""

    def setUp(self): #pylint: disable=C0103
        """Initialize"""
        self.metadata = MetaData()
        self.fields = [ 'time', 'test1', 'test2' ]
        self.order = [ 'test2', 'test1' ]
        (self.table, self.model_class) = get_table(self.metadata, 'table', self.fields, self.order)

    def test_construction(self):
        """Initialize"""

        self.assertEquals('table', self.table.name)

        column_names = [ column.name for column in self.table.columns ]
        for field in self.fields:
            self.assertIn(field, column_names)

    def test_model(self):
        """Initialize"""

        model = self.model_class({'id': 1, 'time': datetime.now(), 'test1': 'test1', 'test2': 'test2'})

        #pylint: disable=E1101
        self.assertEquals('test1', model.test1)
        self.assertEquals('test2', model.test2)
        self.assertEquals(1, model.id)

    def test_order(self):
        """Initialize"""

        model = self.model_class({'id': 1, 'time': datetime.now(), 'test1': 'test1', 'test2': 'test2'})

        order = deque(self.order)
        for key in model.get_data().keys():
            self.assertEquals(order.popleft(), key)

        self.assertEquals(0, len(order))

    def test_difference(self):
        """Test that two tables don't return the same instances."""

        (table, model_class) = get_table(self.metadata, 'table_2', self.fields, self.order)

        self.assertNotEqual(self.table, table)
        self.assertNotEqual(self.model_class, model_class)

    def test_duplicate(self):
        """Test that the same table cannot be created twice even with different columns."""

        self.assertRaises(InvalidRequestError, get_table, self.metadata, 'table', {}, self.order)

    def test_field_ignoring(self):
        """Assert special fields are ignored."""

        self.fields.append('id')
        self.fields.append('date')
        self.fields.append('time')

        (table, model_class) = get_table(self.metadata, 'table_2', self.fields, self.order) #pylint: disable=W0612

        for column in table.columns:
            if column.name == 'id':
                self.assertEqual(type(column.type), Integer)
            elif column.name == 'time':
                self.assertEqual(type(column.type), DateTime)
            self.assertNotEqual('date', column.name)

    def test_order_ignoring(self):
        """Assert special orders are ignored."""

        self.order.append('id')
        self.order.append('date')
        self.order.append('time')

        (table, model_class) = get_table(self.metadata, 'table_2', self.fields, self.order) #pylint: disable=W0612

        model = model_class({'id': 1, 'time': datetime.now(), 'test1': 'test1', 'test2': 'test2'})

        for key in model.get_data().keys():
            self.assertNotIn(key, ['id', 'date', 'time'])
