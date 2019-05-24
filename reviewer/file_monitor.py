import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    def __init__(self, dir, callback, debug=False):
        """ Watches the given directory and calls callback on new file creation """
        self.observer = Observer()
        self.callback = callback
        self.debug = debug
        self.dir_to_watch = dir

    def run(self):
        """ Begin watching """
        event_handler = SlideshowHandler(self.callback, self.debug)
        self.observer.schedule(event_handler, self.dir_to_watch, recursive=True)
        self.observer.start()

    def finish(self):
        self.observer.stop()
        if self.debug:
            print("Stopping watching - %s" % self.dir_to_watch)
        self.observer.join()

class SlideshowHandler(FileSystemEventHandler):
    def __init__(self, callback, debug=False):
        self.debug = debug
        self.callback = callback

    def on_any_event(self, event):
        if self.debug:
            print("Encountered event: {0} - {1}".format(event.event_type, event.src_path))
        if event.is_directory:
            return None

        elif event.event_type is 'created' or 'modified' :
            # Take any action here when a file is first created.
            if self.debug:
                print("New File - %s." % event.src_path)
            if event.src_path.endswith('.jpg'):
                if self.debug:
                    print("Calling callback")
                self.callback(event.src_path)

class Testing:
    def puts(self, str):
        print("YAY!! %s" % str)

if __name__ == '__main__':
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "/home/pi/Desktop/photopoof"
    print("Using Path %s" % path)
    test_obj = Testing()
    w = Watcher(path, test_obj.puts, True)
    w.run()
    try:
        while True:
            time.sleep(50000)
    except:
        w.finish()

