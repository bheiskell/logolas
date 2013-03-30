from logolas.notifier import LogNotifier
import pyinotify

def test():
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

def main():
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
