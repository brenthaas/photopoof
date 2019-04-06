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
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            if self.debug:
                print("New Photo Upload - %s." % event.src_path)
            self.callback(event.src_path)

class Testing:
    def puts(self, str):
        print("YAY!! %s" % str)

if __name__ == '__main__':
    test_obj = Testing()
    w = Watcher("/Users/brent/tmp", test_obj.puts, True)
    w.run()
    try:
        while True:
            time.sleep(50000)
    except:
        w.finish()

