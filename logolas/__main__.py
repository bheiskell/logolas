#!/usr/bin/python

import re
import os
import pyinotify
import MySQLdb

################################################################################
## Configurate #################################################################
################################################################################
## Each log entry needs a database (model) entry, a regular expression entry  ##
## for parsing the logs, and a file entry mapping a log type to a file.       ##
##                                                                            ##
## There is a minimum requirement of being able to extract a timestamp from   ##
## the log entry as the web interface makes assumptions about that.           ##
################################################################################

models = {
    'join':    ('time', 'user', 'ip'),
    'leave':   ('time', 'user'),
    'chat':    ('time', 'user', 'channel', 'message'),
    'pm':      ('time', 'user', 'recipient', 'message'),
    'ban':     ('time', 'user', 'admin', 'reason'),
    'command': ('time', 'user', 'command'),
    'shop':    ('time', 'user', 'action', 'amount', 'item', 'price', 'shop', 'location'),
}

regexs = {
    'join': {
        'regex': '([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+)\[\/([0-9.]+)[^\]]+\] logged in.*',
        'order': ('date', 'time', 'user', 'ip'),
    },
    'leave': {
        'regex': '([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+) lost connection: disconnect.quitting',
        'order': ('date', 'time', 'user'),
    },
    #'chat': {
    #    'regex': '([0-9-]+) ([0-9:]+) \[INFO\] \[([^\]]+)\] ([^ ]+)[^:]*: (.*)',
    #    'order': ('date', 'time', 'channel', 'user', 'message'),
    #},
    #'pm': {
    #    'regex': '([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+) -> ([^ ]+): (.*)',
    #    'order': ('date', 'time', 'user', 'recipient', 'message'),
    #},
    'chat': {
        'regex': '([0-9.]+) ([0-9:]+) \[([^\]]+)\] ([^ ]+)[^:]*: (.*)',
        'order': ('date', 'time', 'channel', 'user', 'message'),
    },
    'pm': {
        'regex': '([0-9.]+) ([0-9:]+) ([^ ]+) -> ([^ ]+): (.*)',
        'order': ('date', 'time', 'user', 'recipient', 'message'),
    },
    'ban': {
        'regex': "([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+): Banned player ([^ ]+)(.*)",
        'order': ('date', 'time', 'admin', 'user', 'reason'),
    },
    'command': {
        'regex': '([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+) issued server command: (.*)',
        'order': ('date', 'time', 'user', 'command'),
    },
    'shop': {
        'regex': '([0-9-]+) ([0-9:]+) \[INFO\] \[ChestShop\] ([^ ]+) ([^ ]+) ([0-9]+) ([^ ]+) for ([0-9.]+) [fromto]+ (.*) at (.*)',

        'order': ('date', 'time', 'user', 'action', 'amount', 'item', 'price', 'shop', 'location'),
    },
}

files = {
    '/home/minecraft/usr/server.log': [
        'join',
        'leave',
        'shop',
        'command',
        #'chat',
        #'pm',
        'ban',
    ],
    '/home/minecraft/usr/plugins/Herochat/logs/chat.0.0.log': [
        'chat',
        'pm',
    ],
    #'/home/minecraft/usr/plugins/CommandBook/bans.0.0.log': [
    #],
}

################################################################################
## LogFile #####################################################################
################################################################################

class LogFile:
    filename = ''
    filehandle = False

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def read(self):
        return self.filehandle.readlines()

    def load(self):
        self.filehandle = open(self.filename, 'r')

    def reload(self):
        self.close();
        self.load();

    def close(self):
        self.filehandle.close()

################################################################################
## Parsers #####################################################################
################################################################################

class Parser:
    regex = ''

    def __init__(self, regex):
        self.regex = regex

    def parse(self, array):
        result = []

        for line in array:
            match = re.search(self.regex, line)
            if match:
                result.append(match.groups())
        return result


################################################################################
## Sinks #######################################################################
################################################################################

class Sink:
    table = False
    fields = False
    order = False
    connection = False
    latest = False

    def __init__(self, type=False, fields=False, order=False):
        self.table  = "%s_log" % type 
        self.fields = fields
        self.order  = order

        try:
            self.connection = MySQLdb.connect(
                'localhost',
                'logger-shell',
                '',
                'logger');

            latest = "SELECT MAX(time) FROM %s" % ( self.table )

            cursor = self.connection.cursor()
            cursor.execute(latest)
            self.latest = cursor.fetchone()[0]
            print self.latest

        except MySQLdb.Error, e:
            print "Mysql error %d: %s" % (e.args[0], e.args[1])

    def sink(self, array):
        #for input in array:
            #print input
        #return True
        try:
            for input in array:
                dictionary = dict(zip(self.order, input))

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

        except MySQLdb.Error, e:
            print "Mysql error %d: %s" % (e.args[0], e.args[1])
            if (2006 == e.args[0]):
                self.connection = MySQLdb.connect(
                    'localhost',
                    'logger-shell',
                    '',
                    'logger');
                self.sink(array)

################################################################################
## Notifier ####################################################################
################################################################################

class LogNotifier(pyinotify.ProcessEvent):

    handler = False

    # HACK: lazy initialization
    def setup_handler(self, handler=False):
        if not self.handler:
            if handler:
                self.handler = handler
            else:
                # accessing global configuration, gross I know
                global models, regexs, files
                self.handler = Handler(
                    models=models,
                    regexs=regexs,
                    files=files,
                )

    def process_IN_MOVE_SELF(self, event):
        self.setup_handler()
        self.handler.reload(event.path)

    def process_IN_CLOSE_WRITE(self, event):
        self.setup_handler()
        self.handler.reload(event.path)

    def process_IN_MODIFY(self, event):
        self.setup_handler()
        self.handler.handle(event.path)

################################################################################
## Handler #####################################################################
################################################################################

# HACK: container for the configuration to object mapping / buisness logic
class Handler:
    log_files = { } # filename: LogFile
    parsers   = { } # filename: [ Parser, ... ]
    sinks     = { } # Parser: Sink

    def __init__(self, models=False, regexs=False, files=False):

        for file, types in files.items():

            self.log_files[file] = LogFile(file)

            self.parsers[file] = []

            for type in types:
                parser = Parser(regexs[type]['regex'])
                self.parsers[file].append(parser)

                self.sinks[parser] = Sink(
                    type=type,
                    fields=models[type],
                    order=regexs[type]['order']
                )

            self.handle(file)


    def reload(self, file):
        print "Reloading %s" % file
        self.log_files[file].reload()

    def handle(self, file, supress=False):
        lines = self.log_files[file].read()
        for parser in self.parsers[file]:
            results = parser.parse(lines)
            self.sinks[parser].sink(results)

################################################################################
## Testing #####################################################################
################################################################################

if True:
    print "Testing:"
    for key in regexs.keys():
        p = Parser(regexs[key]['regex'])
        print "\t%s: %s" % (key, p.parse([
                "2012-09-02 07:54:39 [INFO] UserA lost connection: disconnect.quitting",
                "2012-09-02 07:54:57 [INFO] UserA[/122.49.155.77:60073] logged in with entity id 3886922 at ([alendria] -403.5180933748426, 99.0, 221.38148706833465)",
                "2012.08.26 10:49:39 [ooc] UserB: hello",
                "2012.08.26 10:33:13 UserA -> UserB: hello hello",
                "2012-08-26 10:32:42 [INFO] [ooc] UserA (Nickname): hello",
                "2012-08-26 10:33:08 [INFO] UserA -> UserB: herro hello",
                "2012-08-26 10:31:49 [INFO] UserA tried to use command /home",
                "2011-12-03 04:06:45 [INFO] [ChestShop] UserB sold 1 GOLD_INGOT for 20.0 to Admin Shop",
                "[2011-08-28 09:45:38] BAN: UserA (121.45.44.33) banned name 'UserC': griefing, hacking, trolling",
                "2013-03-09 02:01:34 [INFO] [ChestShop] UserB bought 20 Bread for 45.00 from Admin Shop at [world] -349, 88, 226",
                "2013-03-09 09:26:00 [INFO] UserB: Banned player UserC",
            ]))

################################################################################
## Main ########################################################################
################################################################################

mask         = pyinotify.IN_MODIFY | pyinotify.IN_MOVE_SELF | pyinotify.IN_CLOSE_WRITE
watchmanager = pyinotify.WatchManager()
notifier     = pyinotify.Notifier(watchmanager, LogNotifier())

for file in files:
    wdd = watchmanager.add_watch(file, mask)

while True:
    try:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()

    except KeyboardInterrupt:
        notifier.stop()
        break
