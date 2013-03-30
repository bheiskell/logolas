"""
Sink is responsible for persisting parsed lines to the database.

Additionally it provides deduplication.
"""
#import MySQLdb
import logging

_LOG = logging.getLogger(__name__)

class Sink: #pylint: disable=R0903
    """Persist parsed lines to the database."""

    def __init__(self, engine=None, model=None):
        self.engine = engine
        self.model = model
        self.latest = None

    def get_latest(self):
        """Get the time for the latest entry in this Sink."""

        #latest = "SELECT MAX(time) FROM %s" % ( self.table )
        #cursor = self.connection.cursor()
        #cursor.execute(latest)
        #self.latest = cursor.fetchone()[0]
        _LOG.info("Latest entry in Sink %s", self.latest)

    def sink(self, entries):
        """Persist the lines to the database."""

        if self.latest == None:
            self.get_latest()

        for entry in entries:

            # Need datetime-format and need to convert this into a SQL date
            entry['datetime'] = ""

            if entry['datetime'] >= str(self.latest):

                pass
                #cursor = self.connection.cursor()

                # Utilizing ugly syntax to generate the prepared statements
                #exists = """
                #    SELECT COUNT(*) FROM %s WHERE
                #        %s
                #    """ % (self.table,  ' AND '.join(["%s = %%s" % field for field in self.fields]))

                #insert = """
                #    INSERT INTO %s (
                #        %s
                #    ) VALUES (
                #        %s
                #    )
                #    """% (self.table,  ', '.join(self.fields), ', '.join(['%s'] * len(self.fields)))

                #data = [entry[field] for field in self.fields]

                #_LOG.info("Time %s >= %s: %s", entry['datetime'], str(self.latest), data )

                #cursor.execute(exists, data)

                #if 0 == cursor.fetchone()[0]:
                #    cursor.execute(insert, (data))
                #cursor.close()

    @staticmethod
    def generate_model():
        """Generate a model for a Sink."""
        pass
