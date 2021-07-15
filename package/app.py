import os
import sys
import shutil
import json
from time import sleep
from threading import Thread
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.utils import dirsnapshot


class App:
    def __init__(self):
        self.threads = []
        try:
            with open("settings.json", "r") as file:
                contents = json.load(file)
            self.Paths = contents["Paths"]
        except OSError:
            sys.exit("Failed to read SYNC_FOLDER_PATH and BACKUP_FOLDER_PATH")

    def __exit__(self, exc_type, exc_val, exc_tb):
        for thread in self.threads:
            thread.join()

    def start(self):
        for Path in self.Paths:
            if os.path.exists(Path["SYNC_FOLDER_PATH"]) and os.path.exists(Path["BACKUP_FOLDER_PATH"]):
                print(f"creating handler for {Path['SYNC_FOLDER_PATH']}")
                self.init_handler(Path["SYNC_FOLDER_PATH"], Path["BACKUP_FOLDER_PATH"])
        while True:
            sleep(5)

    def init_handler(self, sync_folder_path, backup_folder_path):
        print(f"syncing: {sync_folder_path} to: {backup_folder_path}")
        sync_folder_snapshot = dirsnapshot.DirectorySnapshot(sync_folder_path, True)
        backup_folder_snapshot = dirsnapshot.DirectorySnapshot(backup_folder_path, True)
        sync_folder_snapshot_paths = sync_folder_snapshot.paths
        backup_folder_snapshot_paths = backup_folder_snapshot.paths
        sync_folder_snapshot_paths.remove(sync_folder_path)
        backup_folder_snapshot_paths.remove(backup_folder_path)
        # TODO check if enough space is available before copying
        space_needed = sum(f.stat().st_size for f in Path(sync_folder_path).glob('**/*') if f.is_file()) // (2**30)
        total, used, space_available = shutil.disk_usage(backup_folder_path)
        space_available = space_available // (2**30)
        print(f"space needed: {space_needed if space_needed != 0 else '<1'}GiB, "
              f"space available: {space_available if space_available != 0 else '<1'}GiB")
        if space_needed < space_available:
            for element in sorted(sync_folder_snapshot_paths):
                converted_path = element.replace(sync_folder_path, backup_folder_path)
                if converted_path not in backup_folder_snapshot_paths:
                    if os.path.isdir(element):
                        print("made dir")
                        os.mkdir(converted_path)
                    else:
                        print("copied file")
                        shutil.copy2(element, converted_path)
        else:
            print(f"not enough space, missing {(space_needed - space_available) // (2**30)}GiB")
        del sync_folder_snapshot
        del backup_folder_snapshot
        del sync_folder_snapshot_paths
        del backup_folder_snapshot_paths
        total, used, space_available = shutil.disk_usage(backup_folder_path)
        space_available = space_available // (2 ** 30)
        observer = Observer()
        event_handler = Handler(sync_folder_path, backup_folder_path, space_available)
        observer.schedule(event_handler, sync_folder_path, recursive=True)
        thread = Thread(target=observer.start)
        self.threads.append(thread)
        thread.start()
        print("\n")


class Handler(FileSystemEventHandler):
    # TODO impl logging to show thread id on log
    def __init__(self, sync_folder_path, backup_folder_path, backup_driver_available_space):
        self.syncFolderPath = sync_folder_path
        self.backupFolderPath = backup_folder_path
        self.backup_driver_available_space = backup_driver_available_space

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
        # TODO add backup option
        print(f"removed: {event.src_path}")
        if os.path.isdir(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1]):
            shutil.rmtree(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])
        else:
            os.remove(self.backupFolderPath + event.src_path.split(self.syncFolderPath)[-1])

    def on_modified(self, event):
        pass
        # TODO impl
