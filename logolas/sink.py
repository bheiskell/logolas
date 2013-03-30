"""
Sink is responsible for persisting parsed lines to the database.

Additionally it provides deduplication.
"""
import MySQLdb

class Sink: #pylint: disable=R0903
    """Persist parsed lines to the database."""

    def __init__(self, category=False, fields=False, order=False):
        self.table  = "%s_log" % category 
        self.fields = fields
        self.order  = order

        try:
            self.connection = MySQLdb.connect(
                'localhost',
                'logger-shell',
                '',
                'logger')

            latest = "SELECT MAX(time) FROM %s" % ( self.table )

            cursor = self.connection.cursor()
            cursor.execute(latest)
            self.latest = cursor.fetchone()[0]
            print self.latest

        except MySQLdb.Error, exception:
            print "Mysql error %d: %s" % (exception.args[0], exception.args[1])

    def sink(self, lines):
        """Persist the lines to the database."""
        try:
            for line in lines:
                dictionary = dict(zip(self.order, line))

                if 'time_short' in dictionary:
                    dictionary['time'] = "%s:00" % dictionary['time_short']

                #if ("%s %s" % ( dictionary['date'], dictionary['time'] )) >= "2011-11-01 00:00:00":
                dictionary['date'] = dictionary['date'].replace('.', '-')
                if (None == self.latest) or ("%s %s" % ( dictionary['date'], dictionary['time'] )) >= str(self.latest):
                    dictionary['time'] = "%s %s" % ( dictionary['date'], dictionary['time'] )

                    cursor = self.connection.cursor()

                    # Leveraging ugly syntax to generate the prepared statements
                    exists = """
                        SELECT COUNT(*) FROM %s WHERE
                            %s
                        """ % (self.table,  ' AND '.join(["%s = %%s" % field for field in self.fields]))

                    insert = """
                        INSERT INTO %s (
                            %s
                        ) VALUES (
                            %s
                        )
                        """% (self.table,  ', '.join(self.fields), ', '.join(['%s'] * len(self.fields)))

                    data = [dictionary[field] for field in self.fields]

                    print "Time %s %s >= %s: %s" % ( dictionary['date'], dictionary['time'] , str(self.latest), data )
                    #print exists
                    #print dictionary

                    cursor.execute(exists, data)

                    if 0 == cursor.fetchone()[0]:
                        cursor.execute(insert, (data))

                    cursor.close()

        except MySQLdb.Error, exception:
            print "Mysql error %d: %s" % (exception.args[0], exception.args[1])
            if (2006 == exception.args[0]):
                self.connection = MySQLdb.connect(
                    'localhost',
                    'logger-shell',
                    '',
                    'logger')
                self.sink(lines)
