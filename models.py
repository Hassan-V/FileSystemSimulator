import csv
import datetime
import logging
import pickle
import os
import threading
import time

class File:
    def __init__(self, name, content=''):
        self.name = name
        self.content = content
        self.size = len(content)
        self.creation_date = datetime.datetime.now()
        self.modification_date = self.creation_date

    def update_content(self, new_content):
        if self.content != new_content:
            self.content = new_content
            self.size = len(new_content)
            self.modification_date = datetime.datetime.now()

    def get_metadata(self):
        return {
            'name': self.name,
            'size': self.size,
            'creation_date': self.creation_date,
            'modification_date': self.modification_date
        }

class Directory:
    def __init__(self, name):
        self.name = name
        self.files = {}
        self.directories = {}

    def add_file(self, file):
        self.files[file.name] = file

    def remove_file(self, file_name):
        if file_name in self.files:
            del self.files[file_name]

    def add_directory(self, directory):
        self.directories[directory.name] = directory

    def remove_directory(self, dir_name):
        if dir_name in self.directories:
            del self.directories[dir_name]

    def list_contents(self):
        return {
            'files': list(self.files.keys()),
            'directories': list(self.directories.keys())
        }

class FileSystem:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.FileHandler("performance_log.txt"),
                            logging.StreamHandler()
                        ])

    def __init__(self, root_path="/"):
        self.root = Directory(root_path)
        self.root_path = root_path

    def _create_directory(self, path):
        parts = path.strip("/").split("/")
        current_dir = self.root
        for part in parts:
            if part not in current_dir.directories:
                new_dir = Directory(part)
                current_dir.add_directory(new_dir)
            current_dir = current_dir.directories[part]

    def _get_directory(self, path):
        parts = path.strip("/").split("/")
        current_dir = self.root
        for part in parts:
            if part == "":  # Skip if it's the root directory
                continue
            if part in current_dir.directories:
                current_dir = current_dir.directories[part]
            else:
                return None  # Directory does not exist
        return current_dir

    def create_file(self, path, name, content=''):
        start_time = time.time_ns()
        directory = self._get_directory(path)
        if not directory:
            self._create_directory(path)
            directory = self._get_directory(path)
        if directory:
            new_file = File(name, content)
            directory.add_file(new_file)
        self._log_performance("create", start_time)

    def read_file(self, path):
        start_time = time.time_ns()
        dir_path, file_name = os.path.split(path)
        directory = self._get_directory(dir_path)
        content = None
        if directory and file_name in directory.files:
            content = directory.files[file_name].content
        self._log_performance("read", start_time)
        return content

    def write_file(self, path, content):
        start_time = time.time_ns()
        dir_path, file_name = os.path.split(path)
        directory = self._get_directory(dir_path)
        if directory and file_name in directory.files:
            directory.files[file_name].update_content(content)
        self._log_performance("update", start_time)

    def delete(self, path):
        start_time = time.time_ns()
        dir_path, name = os.path.split(path)
        directory = self._get_directory(dir_path)
        if directory:
            if name in directory.files:
                directory.remove_file(name)
            elif name in directory.directories:
                directory.remove_directory(name)
        self._log_performance("delete", start_time)

    def list_dir(self, path):
        directory = self._get_directory(path)
        if directory:
            return directory.list_contents()
        return {'files': [], 'directories': []}

    def statistics(self):
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "total_size": 0
        }
        # Start counting from root, so root itself is included
        self._gather_stats(self.root, stats)
        stats["total_directories"] -= 1  # Adjust for the root directory itself
        return stats

    def _gather_stats(self, directory, stats):
        stats["total_directories"] += 1
        for file in directory.files.values():
            stats["total_files"] += 1
            stats["total_size"] += file.size
        for subdir in directory.directories.values():
            self._gather_stats(subdir, stats)

    def save_state(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_state(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def create_virtual_drive(self, drive_name):
        virtual_drive_path = os.path.join(self.root_path, drive_name.strip("/"))
        if not os.path.exists(virtual_drive_path):
            os.makedirs(virtual_drive_path)
        self.root = Directory(drive_name)  # Adjusted to remove leading slash

    def copy(self, source_path, destination_path):
        start_time = time.time_ns()
        source_dir, source_name = os.path.split(source_path)
        destination_dir, destination_name = os.path.split(destination_path)
        source_directory = self._get_directory(source_dir)
        destination_directory = self._get_directory(destination_dir)

        if not destination_directory:
            self._create_directory(destination_dir)
            destination_directory = self._get_directory(destination_dir)

        if source_directory and source_name in source_directory.files:
            file_to_copy = source_directory.files[source_name]
            new_file = File(destination_name, file_to_copy.content)
            destination_directory.add_file(new_file)
        elif source_directory and source_name in source_directory.directories:
            dir_to_copy = source_directory.directories[source_name]
            new_dir = Directory(destination_name)
            destination_directory.add_directory(new_dir)
            self._copy_directory_contents(dir_to_copy, new_dir)

        self._log_performance("copy", start_time)

    def _copy_directory_contents(self, source_directory, destination_directory):
        for file in source_directory.files.values():
            new_file = File(file.name, file.content)
            destination_directory.add_file(new_file)
        for dir in source_directory.directories.values():
            new_sub_dir = Directory(dir.name)
            destination_directory.add_directory(new_sub_dir)
            self._copy_directory_contents(dir, new_sub_dir)

    def move(self, source_path, destination_path):
        start_time = time.time_ns()
        self.copy(source_path, destination_path)
        self.delete(source_path)
        self._log_performance("move", start_time)

    def rename(self, path, new_name):
        start_time = time.time_ns()
        dir_path, old_name = os.path.split(path)
        directory = self._get_directory(dir_path)
        if directory and old_name in directory.files:
            file_to_rename = directory.files[old_name]
            file_to_rename.name = new_name
            directory.files[new_name] = file_to_rename
            del directory.files[old_name]
        elif directory and old_name in directory.directories:
            dir_to_rename = directory.directories[old_name]
            dir_to_rename.name = new_name
            directory.directories[new_name] = dir_to_rename
            del directory.directories[old_name]
        self._log_performance("rename", start_time)

    def search(self, directory_path, search_term):
        start_time = time.time_ns()
        directory = self._get_directory(directory_path)
        results = []
        if directory:
            self._search_directory(directory, search_term, results)
        self._log_performance("search", start_time)
        return results

    def _search_directory(self, directory, search_term, results):
        for file_name, file in directory.files.items():
            if search_term in file_name:
                results.append(file)
        for dir_name, dir in directory.directories.items():
            if search_term in dir_name:
                results.append(dir)
            self._search_directory(dir, search_term, results)

    def _log_performance(self, operation, start_time):
        end_time = time.time_ns()
        elapsed_time_ms = (end_time - start_time) / 1_000_000  # Convert to milliseconds
        logging.info(f"Operation: {operation}, Time taken: {elapsed_time_ms:.2f} ms")
        
        # Open the CSV file or create it if it doesn't exist, then append the new data
        with open('performance_data.csv', 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write the operation and elapsed time in milliseconds to the CSV file
            csvwriter.writerow([operation, elapsed_time_ms])
