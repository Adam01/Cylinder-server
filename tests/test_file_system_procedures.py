__author__ = 'Adam'

import unittest
import sys
import os
import tempfile
import shutil


class TestFileSystemProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        print "Test directory created at: " + cls.test_dir

        # Create a static dir (this won't change throughout the tests)
        cls.static_dir = os.path.join(cls.test_dir, "Static")

        os.mkdir(cls.static_dir)
        os.mkdir(cls.static_dir + "/D1")
        os.mkdir(cls.static_dir + "/D2")

        with open(cls.static_dir + "/A", "w") as f:
            f.write("Abcdefg123")

        with open(cls.static_dir + "/B", "w") as f:
            f.write("123Abc")

        cls.expected_static_list = ["D1/", "D2/", "A", "B"]

        # Move file vars
        cls.file_move_source_path = os.path.join(cls.test_dir, "FileMove")
        cls.file_move_target_dir = os.path.join(cls.test_dir, "FileMoveDir")
        cls.file_move_target_name = os.path.join(cls.test_dir, "FileMoved")
        cls.file_move_target_path = os.path.join(cls.file_move_target_dir, cls.file_move_target_name)

        os.mkdir(cls.file_move_target_dir)

        # Copy file vars
        cls.file_copy_source_path = os.path.join(cls.test_dir, "FileCopy")
        cls.file_copy_target_dir = os.path.join(cls.test_dir, "FileCopyDir")
        cls.file_copy_target_name = os.path.join(cls.test_dir, "FileCopied")
        cls.file_copy_target_path = os.path.join(cls.file_copy_target_dir, cls.file_copy_target_name)

        os.mkdir(cls.file_copy_target_dir)

        # Copy dir vars
        cls.dir_copy_source_path = cls.static_dir
        cls.dir_copy_target_name = "DirCopied"
        cls.dir_copy_target_dir = cls.static_dir
        cls.dir_copy_target_path = cls.dir_copy_target_dir + cls.dir_copy_target_name
        cls.dir_copy_target_dirs = ["D1", "D2"]
        cls.dir_copy_target_files = ["A", "B"]

        # Others
        cls.file_delete = os.path.join(cls.test_dir, "FileDelete")
        cls.file_create = os.path.join(cls.test_dir, "FileCreate")
        cls.file_create_contents = "Abcdefg123"

        cls.dir_create_name = "D1"
        cls.dir_create_path = os.path.join(cls.test_dir, cls.dir_create_name)

        # Create the specified files

        with open(cls.file_move_source_path, "w") as f:
            f.write("Abcdefg123")

        with open(cls.file_copy_source_path, "w") as f:
            f.write("Abcdefg123")

        with open(cls.file_delete, "w") as f:
            f.write("Abcdefg123")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)

    ''' FS.01
        The system is required to create a file at a specified location and optionally populate it with content.
        The test is successful given the file has been created and matches the expected contents.
    '''

    def test_FS01_create_file(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemDirectory(self.test_dir)
        e.create_file("FileCreate")

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemDirectory")

        os.remove(self.file_create)

        fsprocs = FileSystemProcedures()
        fsprocs.create_file(self.file_create)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemProcedures")

    def test_FS01_create_file_contents(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile
        e = FileSystemDirectory(self.test_dir)
        e.create_file("FileCreate", self.file_create_contents)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemDirectory")

        with open(self.file_create) as f:
            self.assertEquals(f.read(), self.file_create_contents, "File contents after FileSystemDirectory.create_file"
                                                                   " do not match")

        os.remove(self.file_create)

        fsprocs = FileSystemProcedures()
        fsprocs.create_file(self.file_create)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemProcedures")

        with open(self.file_create) as f:
            self.assertEquals(f.read(), self.file_create_contents, "File contents after "
                                                                   "FileSystemProcedures.create_file do not match")

    ''' FS.02
        The system is required to create a directory in a specified location.
        Test is successful given the directory has been created.
    '''

    def test_FS02_create_directory(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemDirectory(self.test_dir)
        e.create_directory(self.dir_create_name)

        self.assertTrue(os.path.isdir(self.dir_create_path), "FileSystemDirectory didn't manage to create a directory")

    ''' FS.03
        The system is required to move a file-system entity to another location in the file system.
        This can be a file or a directory. Test is successful given the owner, location, contents,
        and attributes of the moved entity are the same as of before it was moved.
        The system must not interact with files that are not owned by the current user.
    '''

    def test_FS03_move_entity(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemEntity(self.file_move_source_path)
        d = FileSystemDirectory(self.file_move_target_dir)

        # Note: second parameter can be optional (current name is used)
        e.move_to(d, self.file_move_target_name)

        self.assertTrue(os.path.isfile(self.file_move_target_path), "FileSystemEntity didn't move file - "
                                                                    "It does not exist in target directory")
        self.assertFalse(os.path.isfile(self.file_move_source_path), "FileSystemEntity didn't move file -"
                                                                     "it still exists in source directory")

    ''' FS.04
        The system is required to delete a file from the file-system.
        The test is successful if the system is able to delete a file that must belong to the current user.
    '''

    def test_FS04_remove_entity(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemEntity(self.file_delete)
        e.remove()
        self.assertFalse(os.path.isfile(self.file_delete), "FileSystemEntity didn't delete specified file")

    ''' FS.05
        The system is required to copy a file to a specified location within the user's file-system.
        In order for the test to be successful the file must have the same contents,
        attributes and permissions of the original file.
    '''

    def test_FS05_copy_entity(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemEntity(self.file_copy_source_path)
        d = FileSystemDirectory(self.file_copy_target_dir)

        # Note: second parameter can be optional (current name is used)
        e.copy_to(d, self.file_copy_target_name)

        self.assertTrue(os.path.isfile(self.file_copy_target_path), "FileSystemEntity didn't copy file - "
                                                                    "It does not exist in target directory")
        self.assertTrue(os.path.isfile(self.file_copy_source_path), "FileSystemEntity deleted original file on copy")
        pass

    ''' FS.06
        The system is required to perform a deep copy of a folder.
        This involves recursively copying child directories and copying files in each of them.
        The owners, attributes and contents must be the same in order for the test to pass.
    '''

    def test_FS06_copy_directory(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        sd = FileSystemDirectory(self.dir_copy_source_path)
        td = FileSystemDirectory(self.dir_copy_target_dir)
        sd.copy_to(td, self.dir_copy_target_name)

        self.assertTrue(os.path.isdir(self.dir_copy_target_path),
                        "FileSystemDirectory didn't manage to copy a directory")

        for file_str in self.dir_copy_target_files:
            self.assertTrue(os.path.isfile(self.dir_copy_target_path + "/" + file_str),
                            "FileSystemDirectory didn't manage to copy directory sub files")

        for dir_str in self.dir_copy_target_dirs:
            self.assertTrue(os.path.isdir(self.dir_copy_target_path + "/" + dir_str),
                            "FileSystemDirectory didn't manage to copy directory sub directories")

        self.assertTrue(os.path.isdir(self.dir_copy_source_path),
                        "FileSystemDirectory didn't leave copy source directory intact")

        for file_str in self.dir_copy_target_files:
            self.assertTrue(os.path.isfile(self.dir_copy_source_path + "/" + file_str),
                            "FileSystemDirectory didn't leave copy source directory files intact")

        for dir_str in self.dir_copy_target_dirs:
            self.assertTrue(os.path.isdir(self.dir_copy_source_path + "/" + dir_str),
                            "FileSystemDirectory didn't leave copy source directory sub-directories intact")

    ''' FS.07
        The system is required to list the contents of a directory supporting various formats of results
        (type of entity, size, and other metadata).
        The test is successful once a correct directory listing is matched with static data.
    '''

    def test_FS07_list_directory(self):
        from fsentity import FileSystemEntity, FileSystemDirectory, FileSystemFile

        e = FileSystemDirectory(self.static_dir)
        l = e.list()
        self.assertListEqual(l, self.expected_static_list)

        # TODO: Expand to cover multi list formats

        pass