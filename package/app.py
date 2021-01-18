import os
import sys
import time
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class App:
    def __init__(self):
        load_dotenv()
        try:
            self.syncFolderPath = os.getenv('SYNC_FOLDER_PATH')
            self.backupFolderPath = os.getenv('BACKUP_FOLDER_PATH')
        except OSError:
            sys.exit("Failed to read SYNC_FOLDER_PATH and BACKUP_FOLDER_PATH")
        self.observer = Observer()

    def start(self):
        print("Start")
        event_handler = Handler()
        self.observer.schedule(event_handler, self.syncFolderPath, recursive=True)
        self.observer.start()
        try:
            while True:
                # To keep Program running
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return None
        print(f"Event:{event.event_type}, Path:{event.src_path}")

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass
