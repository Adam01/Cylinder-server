__author__ = 'Adam'

import unittest
import sys
import os


class TestFileSystemProcedures(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    ''' FS.01
        The system is required to create a file at a specified location and optionally populate it with content.
        The test is successful given the file has been created and matches the expected contents.
    '''

    def test_create_file(self):
        path = ""
        e = FileSystemDirectory(path)
        e.create_file("name")

        pass


    def test_create_file_contents(self):
        path = ""
        e = FileSystemDirectory(path)
        e.create_file("name", "contents")
        pass

    ''' FS.02
        The system is required to create a directory in a specified location.
        Test is successful given the directory has been created.
    '''

    def test_create_directory(self):
        path = ""
        e = FileSystemDirectory(path)
        e.create_directory("name")
        pass

    ''' FS.03
        The system is required to move a file-system entity to another location in the file system.
        This can be a file or a directory. Test is successful given the owner, location, contents,
        and attributes of the moved entity are the same as of before it was moved.
        The system must not interact with files that are not owned by the current user.
    '''

    def test_move_entity(self):
        path = ""
        e = FileSystemEntity(path)
        d = FileSystemDirectory(newpath)
        e.move_to(d)
        pass

    ''' FS.04
        The system is required to delete a file from the file-system.
        The test is successful if the system is able to delete a file that must belong to the current user.
    '''

    def test_delete_entity(self):
        path = ""
        e = FileSystemEntity(path)
        e.delete()
        pass

    ''' FS.05
        The system is required to copy a file to a specified location within the user's file-system.
        In order for the test to be successful the file must have the same contents,
        attributes and permissions of the original file.
    '''

    def test_copy_entity(self):
        path = ""
        e = FileSystemEntity(path)
        d = FileSystemDirectory(newpath)
        e.copy_to(d)
        pass

    ''' FS.06
        The system is required to perform a deep copy of a folder.
        This involves recursively copying child directories and copying files in each of them.
        The owners, attributes and contents must be the same in order for the test to pass.
    '''

    def test_copy_directory(self):
        path = ""
        e = FileSystemEntity(path)
        d = FileSystemDirectory(newpath)
        e.copy_to(d, True)

        e = FileSystemDirectory(path)
        e.copy_to(d, True)

        FileSystemProcedures(dict(...))

    ''' FS.07
        The system is required to list the contents of a directory supporting various formats of results
        (type of entity, size, and other metadata).
        The test is successful once a correct directory listing is matched with static data.
    '''

    def test_list_directory(self):
        path = ""
        e = FileSystemDirectory(path)
        e.list()
        e.get_iterator()
        e.list_basic()
        e.list_recursive(e, list_basic)

        pass