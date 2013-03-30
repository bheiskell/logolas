"""
Load and return Logolas's configuration.
"""
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
        'regex': r'([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+)\[\/([0-9.]+)[^\]]+\] logged in.*',
        'order': ('date', 'time', 'user', 'ip'),
    },
    'leave': {
        'regex': r'([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+) lost connection: disconnect.quitting',
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
        'regex': r'([0-9.]+) ([0-9:]+) \[([^\]]+)\] ([^ ]+)[^:]*: (.*)',
        'order': ('date', 'time', 'channel', 'user', 'message'),
    },
    'pm': {
        'regex': r'([0-9.]+) ([0-9:]+) ([^ ]+) -> ([^ ]+): (.*)',
        'order': ('date', 'time', 'user', 'recipient', 'message'),
    },
    'ban': {
        'regex': r"([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+): Banned player ([^ ]+)(.*)",
        'order': ('date', 'time', 'admin', 'user', 'reason'),
    },
    'command': {
        'regex': r'([0-9-]+) ([0-9:]+) \[INFO\] ([^ ]+) issued server command: (.*)',
        'order': ('date', 'time', 'user', 'command'),
    },
    'shop': {
        'regex': r'([0-9-]+) ([0-9:]+) \[INFO\] \[ChestShop\] ([^ ]+) ([^ ]+) ([0-9]+) ([^ ]+) for ([0-9.]+) [fromto]+ (.*) at (.*)',

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
