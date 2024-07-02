# test_models.py

import unittest
import os
import datetime
import time
from models import File, Directory, FileSystem

class TestFile(unittest.TestCase):
    def test_file_creation(self):
        file = File(name="test.txt", content="Hello, World!")
        self.assertEqual(file.name, "test.txt")
        self.assertEqual(file.content, "Hello, World!")
        self.assertEqual(file.size, len("Hello, World!"))
        self.assertIsInstance(file.creation_date, datetime.datetime)
        self.assertEqual(file.creation_date, file.modification_date)

    def test_file_update_content(self):
        file = File(name="test.txt", content="Hello, World!")
        time.sleep(0.01)  # Introduce a slight delay
        file.update_content("New content")
        self.assertEqual(file.content, "New content")
        self.assertEqual(file.size, len("New content"))
        self.assertNotEqual(file.creation_date, file.modification_date)

    def test_get_metadata(self):
        file = File(name="test.txt", content="Hello, World!")
        metadata = file.get_metadata()
        self.assertEqual(metadata['name'], "test.txt")
        self.assertEqual(metadata['size'], len("Hello, World!"))
        self.assertIsInstance(metadata['creation_date'], datetime.datetime)
        self.assertIsInstance(metadata['modification_date'], datetime.datetime)

class TestDirectory(unittest.TestCase):
    def test_directory_creation(self):
        directory = Directory(name="root")
        self.assertEqual(directory.name, "root")
        self.assertEqual(directory.files, {})
        self.assertEqual(directory.directories, {})

    def test_add_remove_file(self):
        directory = Directory(name="root")
        file = File(name="test.txt", content="Hello, World!")
        directory.add_file(file)
        self.assertIn("test.txt", directory.files)
        directory.remove_file("test.txt")
        self.assertNotIn("test.txt", directory.files)

    def test_add_remove_directory(self):
        root = Directory(name="root")
        subdir = Directory(name="subdir")
        root.add_directory(subdir)
        self.assertIn("subdir", root.directories)
        root.remove_directory("subdir")
        self.assertNotIn("subdir", root.directories)

    def test_list_contents(self):
        root = Directory(name="root")
        file = File(name="test.txt", content="Hello, World!")
        subdir = Directory(name="subdir")
        root.add_file(file)
        root.add_directory(subdir)
        contents = root.list_contents()
        self.assertIn("test.txt", contents['files'])
        self.assertIn("subdir", contents['directories'])

class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem()

    def test_create_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        content = self.fs.read_file("/home/user/test.txt")
        self.assertEqual(content, "Hello World")

    def test_create_and_delete_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        self.fs.delete("/home/user/test.txt")
        content = self.fs.read_file("/home/user/test.txt")
        self.assertIsNone(content)

    def test_create_directory(self):
        self.fs._create_directory("/home/user/docs")
        contents = self.fs.list_dir("/home/user")
        self.assertIn("docs", contents["directories"])

    def test_copy_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        self.fs.copy("/home/user/test.txt", "/home/user/copy_test.txt")
        content = self.fs.read_file("/home/user/copy_test.txt")
        self.assertEqual(content, "Hello World")

    def test_copy_directory(self):
        self.fs._create_directory("/home/user/docs")
        self.fs.create_file("/home/user/docs", "test.txt", "Hello World")
        self.fs.copy("/home/user/docs", "/home/user/docs_copy")
        contents = self.fs.list_dir("/home/user")
        self.assertIn("docs_copy", contents["directories"])
        copied_content = self.fs.read_file("/home/user/docs_copy/test.txt")
        self.assertEqual(copied_content, "Hello World")

    def test_move_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        self.fs.move("/home/user/test.txt", "/home/user/moved_test.txt")
        content = self.fs.read_file("/home/user/moved_test.txt")
        self.assertEqual(content, "Hello World")
        old_content = self.fs.read_file("/home/user/test.txt")
        self.assertIsNone(old_content)

    def test_rename_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        self.fs.rename("/home/user/test.txt", "renamed_test.txt")
        content = self.fs.read_file("/home/user/renamed_test.txt")
        self.assertEqual(content, "Hello World")
        old_content = self.fs.read_file("/home/user/test.txt")
        self.assertIsNone(old_content)

    def test_search_file(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        results = self.fs.search("/home/user", "test.txt")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "test.txt")

    def test_statistics(self):
        self.fs.create_file("/home/user", "test.txt", "Hello World")
        stats = self.fs.statistics()
        self.assertEqual(stats["total_files"], 1)
        self.assertEqual(stats["total_directories"], 2)
        self.assertEqual(stats["total_size"], len("Hello World"))

if __name__ == "__main__":
    unittest.main()