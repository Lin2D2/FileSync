import os
import sys
import shutil
import asyncio
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class App:
    def __init__(self):
        try:
            with open("settings.json", "r") as file:
                contents = json.load(file)
            self.Paths = contents["Paths"]
        except OSError:
            sys.exit("Failed to read SYNC_FOLDER_PATH and BACKUP_FOLDER_PATH")

    async def start(self):
        print("Start")
        event_loop = asyncio.get_event_loop()
        # TODO for loop to watch more Paths
        for Path in self.Paths:
            event_loop.create_task(self.init_handler(Path["SYNC_FOLDER_PATH"], Path["BACKUP_FOLDER_PATH"]))

    @staticmethod
    async def init_handler(sync_folder_path, backup_folder_path):
        print(f"syncing: {sync_folder_path} to: {backup_folder_path}")
        # TODO first sync up
        observer = Observer()
        event_handler = Handler(sync_folder_path, backup_folder_path)
        observer.schedule(event_handler, sync_folder_path, recursive=True)
        observer.start()
        try:
            while True:
                # To keep Program running
                await asyncio.sleep(5)
        except Exception as error:
            observer.stop()
            print(f"Error: {error}")
        finally:
            observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, sync_folder_path, backup_folder_path):
        self.syncFolderPath = sync_folder_path
        self.backupFolderPath = backup_folder_path

    def on_any_event(self, event):
        if event.is_directory:
            return None
        print(f"Event:{event.event_type}, Path:{event.src_path}")

    def on_moved(self, event):
        shutil.move(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1],
                    self.backupFolderPath + event.dest_path.split(self.syncFolderPath)[-1])

    def on_created(self, event):
        print(f"created: {event.src_path}")
        if event.is_directory:
            os.mkdir(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])
        else:
            shutil.copy2(event.src_path, self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])

    def on_deleted(self, event):
        print(f"removed: {event.src_path}")
        if os.path.isdir(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1]):
            shutil.rmtree(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])
        else:
            os.remove(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])

    def on_modified(self, event):
        pass
