import os
import sys
import time
import shutil
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
        print(f"disk usage sync: {shutil.disk_usage(self.syncFolderPath)}")
        print(f"disk usage backup: {shutil.disk_usage(self.backupFolderPath)}")
        event_handler = Handler(self)
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
    def __init__(self, parent):
        self.parent = parent

    def on_any_event(self, event):
        if event.is_directory:
            return None
        print(f"Event:{event.event_type}, Path:{event.src_path}")

    def on_moved(self, event):
        shutil.move(self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1],
                    self.parent.backupFolderPath + event.dest_path.split(self.parent.syncFolderPath)[-1])

    def on_created(self, event):
        print(f"created: {event.src_path}")
        if event.is_directory:
            os.mkdir(self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1])
        else:
            shutil.copy2(event.src_path, self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1])

    def on_deleted(self, event):
        print(f"removed: {event.src_path}")
        if os.path.isdir(self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1]):
            shutil.rmtree(self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1])
        else:
            os.remove(self.parent.backupFolderPath + event.src_path.split(self.parent.syncFolderPath)[-1])

    def on_modified(self, event):
        pass