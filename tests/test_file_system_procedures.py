__author__ = 'Adam'

import unittest
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

        cls.expected_static_list = ["A", "B", "D1", "D2"]

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
        cls.dir_copy_target_dir = cls.test_dir
        cls.dir_copy_target_path = os.path.join(cls.dir_copy_target_dir, cls.dir_copy_target_name)
        cls.dir_copy_target_dirs = ["D1", "D2"]
        cls.dir_copy_target_files = ["A", "B"]

        cls.expected_copy_calls = 2
        cls.expected_enter_calls = 3

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

    def create_RPC(self, func_name, **kwargs):
        return {"id": 0, "method": func_name, "params": dict(kwargs)}

    ''' FS.01
        The system is required to create a file at a specified location and optionally populate it with content.
        The test is successful given the file has been created and matches the expected contents.
    '''

    def test_FS01_create_file(self):
        from fsentity import FileSystemDirectory
        from fsprocedures import FileSystemProcedures

        e = FileSystemDirectory(self.test_dir)

        # TODO: test f
        f = e.create_file("FileCreate")

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemDirectory")

        os.remove(self.file_create)

        fsprocs = FileSystemProcedures()
        json_obj = self.create_RPC("create_file",
                                   path=self.test_dir,
                                   name=self.file_create)
        fsprocs(json_obj)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemProcedures")

    def test_FS01_create_file_contents(self):
        from fsentity import FileSystemDirectory
        from fsprocedures import FileSystemProcedures

        e = FileSystemDirectory(self.test_dir)
        f = e.create_file("FileCreate", self.file_create_contents)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemDirectory")

        with open(self.file_create) as f:
            self.assertEquals(f.read(), self.file_create_contents, "File contents after FileSystemDirectory.create_file"
                                                                   " do not match")

        os.remove(self.file_create)

        fsprocs = FileSystemProcedures()
        json_obj = self.create_RPC("create_file",
                                   path=self.test_dir,
                                   name=self.file_create,
                                   contents=self.file_create_contents)
        fsprocs(json_obj)

        self.assertTrue(os.path.isfile(self.file_create), "CreateFile was not created by FileSystemProcedures")

        with open(self.file_create) as f:
            self.assertEquals(f.read(), self.file_create_contents, "File contents after "
                                                                   "FileSystemProcedures.create_file do not match")

    ''' FS.02
        The system is required to create a directory in a specified location.
        Test is successful given the directory has been created.
    '''

    def test_FS02_create_directory(self):
        from fsentity import FileSystemDirectory
        from fsprocedures import FileSystemProcedures

        e = FileSystemDirectory(self.test_dir)
        # TODO: test d
        d = e.create_directory(self.dir_create_name)

        self.assertTrue(os.path.isdir(self.dir_create_path), "FileSystemDirectory didn't manage to create a directory")

        os.rmdir(self.dir_create_path)

        fsprocs = FileSystemProcedures()
        json_obj = self.create_RPC("create_directory",
                                   path=self.test_dir,
                                   name=self.dir_create_name)
        fsprocs(json_obj)

        self.assertTrue(os.path.isdir(self.dir_create_path), "CreateDirectory was not created by FileSystemProcedures")

    ''' FS.03
        The system is required to move a file-system entity to another location in the file system.
        This can be a file or a directory. Test is successful given the owner, location, contents,
        and attributes of the moved entity are the same as of before it was moved.
        The system must not interact with files that are not owned by the current user.
    '''

    def test_FS03_move_entity(self):
        from fsentity import FileSystemEntity, FileSystemDirectory
        from fsprocedures import FileSystemProcedures

        entity = FileSystemEntity(self.file_move_source_path)
        target_directory = FileSystemDirectory(self.file_move_target_dir)

        # Note: second parameter can be optional (current name is used)
        entity.move_to(target_directory, self.file_move_target_name)

        self.assertTrue(os.path.isfile(self.file_move_target_path), "FileSystemEntity didn't move file - "
                                                                    "It does not exist in target directory")
        self.assertFalse(os.path.isfile(self.file_move_source_path), "FileSystemEntity didn't move file -"
                                                                     "it still exists in source directory")

        self.assertEqual(self.file_move_target_path, entity.get_path(),
                         "FileSystemEntity didn't update its path after move")

        fsprocs = FileSystemProcedures()
        json_obj = self.create_RPC("move_entity",
                                   source=self.file_move_target_path,
                                   target=self.file_move_source_path)

        fsprocs(json_obj)

        self.assertTrue(os.path.isfile(self.file_move_source_path), "FileSystemProcedures didn't move file - "
                                                                    "It does not exist in target directory")
        self.assertFalse(os.path.isfile(self.file_move_target_path), "FileSystemProcedures didn't move file -"
                                                                     "it still exists in source directory")


    ''' FS.04
        The system is required to delete a file from the file-system.
        The test is successful if the system is able to delete a file that must belong to the current user.
    '''

    def test_FS04_remove_entity(self):
        from fsentity import FileSystemEntity
        from fsprocedures import FileSystemProcedures

        e = FileSystemEntity(self.file_delete)
        e.remove()

        # TODO: test e now fails

        self.assertFalse(os.path.isfile(self.file_delete), "FileSystemEntity didn't delete specified file")

        with open(self.file_delete, "w") as f:
            f.write("Abcdefg123")

        fsprocs = FileSystemProcedures()
        json_obj = self.create_RPC("remove_entity",
                                   path=self.file_delete)
        fsprocs(json_obj)
        self.assertFalse(os.path.isfile(self.file_delete), "FileSystemProcedures didn't delete specified file")

    ''' FS.05
        The system is required to copy a file to a specified location within the user's file-system.
        In order for the test to be successful the file must have the same contents,
        attributes and permissions of the original file.
    '''

    def test_FS05_copy_entity(self):
        from fsentity import FileSystemFile, FileSystemDirectory

        e = FileSystemFile(self.file_copy_source_path)
        d = FileSystemDirectory(self.file_copy_target_dir)

        # Note: second parameter can be optional (current name is used)
        new_entity = e.copy_to(d, self.file_copy_target_name)

        # TODO: test new_entity, fsprocs

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
        from fsentity import FileSystemDirectory

        # TODO: fsprocs

        self.total_copy_calls = 0
        self.total_enter_calls = 0

        def onFileCopy(original_dir, target_dir, target_path_dir, original=None, copied=None, target_name=None):
            if original is not None:
                self.total_copy_calls += 1
                # print "Copied file from %s\nto %s" % (original.get_path(), copied.get_path())

            if target_name is not None:
                self.total_enter_calls += 1
                #print "Entered directory %s\nCopying to %s" % (original_dir.get_path(), target_path_dir.get_path())

        # def onFileCopy(**kwargs):
        #    print dict(kwargs)

        sd = FileSystemDirectory(self.dir_copy_source_path)
        td = FileSystemDirectory(self.dir_copy_target_dir)
        new_dir = sd.copy_to(td, self.dir_copy_target_name, on_copied_file=onFileCopy, on_enter_dir=onFileCopy)


        # TODO: test new_dir

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

        # Test callbacks

        self.assertEqual(self.expected_copy_calls, self.total_copy_calls)
        self.assertEqual(self.expected_enter_calls, self.total_enter_calls)

    ''' FS.07
        The system is required to list the contents of a directory supporting various formats of results
        (type of entity, size, and other metadata).
        The test is successful once a correct directory listing is matched with static data.
    '''

    def test_FS07_list_directory(self):
        from fsentity import FileSystemDirectory

        e = FileSystemDirectory(self.static_dir)
        l = e.list()
        self.assertListEqual(l, self.expected_static_list)

        # TODO: Expand to cover multi list formats

        pass