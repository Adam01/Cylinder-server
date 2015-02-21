__author__ = 'Adam'

import unittest
import sys
import os


class TestFileContentProcedures(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    '''
        The system is required to be able to obtain the content of a file.
        This test is successful if the content is matched as is with expected data.
    '''

    def test_get_file_contents(self):
        path = ""
        f = FileSystemFile(path)
        f.get_contents()
        pass


    '''
        The system must be able to set the contents of a file.
        Test is successful if changes are made that match the expected outcome.
    '''

    def test_set_file_contents(self):
        path = ""
        e = FileSystemEntity(path)
        f = e.getFile()
        f.set_contents("abc")
        pass

    '''
        The system will need to update a file's contents from a differential format.
        The test is successful if the resulting file contents matches the result of the original content with
        a supplied delta.
    '''

    def test_set_file_from_diff(self):
        path = ""
        e = FileSystemEntity(path)
        f = e.getFile()
        f.set_from_diff("abc")
        pass


    ''' Identify byte encoding '''

    def test_identify_encoding(self):
        path = ""
        e = FileSystemEntity(path)
        f = e.getFile()
        f.identify_encoding()
        pass

    ''' Identify EOL format '''

    def test_identify_line_ending(self):
        path = ""
        e = FileSystemEntity(path)
        f = e.getFile()
        f.identify_line_ending()
        pass

    ''' ... code style? '''

    def test_identify_format(self):
        pass