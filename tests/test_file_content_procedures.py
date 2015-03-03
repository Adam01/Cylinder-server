__author__ = 'Adam'

import unittest
import sys
import os
import tempfile


class TestFileContentProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "./tests/data/"

        cls.text_file_name = "TextFile_UTF16_CRLF.txt"
        cls.text_file_path = os.path.join(cls.test_dir, cls.text_file_name)
        cls.text_file_encoding = "UTF-16"
        cls.text_file_eol = "CRLF"
        with open(cls.text_file_path, "r") as f:
            cls.text_file_contents = f.read()

        cls.script_file_name = "ScriptFile_UTF8_LF.py"
        cls.script_file_path = os.path.join(cls.test_dir, cls.script_file_name)
        cls.script_file_encoding = "UTF-8"
        cls.script_file_eol = "LF"
        with open(cls.script_file_path, "r") as f:
            cls.script_file_contents = f.read()

        cls.set_contents = cls.text_file_contents
        cls.set_name = "TestSetContents.txt"
        cls.set_path = os.path.join(cls.test_dir, cls.set_name)
        print "Test write file "


    def tearDown(self):
        pass

    '''
        The system is required to be able to obtain the content of a file.
        This test is successful if the content is matched as is with expected data.
    '''

    def test_get_file_contents(self):
        from fsentity import FileSystemFile
        from fsprocedures import FileSystemProcedures

        script_file = FileSystemFile(self.script_file_path)
        self.assertEquals(script_file.get_contents(), self.script_file_contents)

        text_file = FileSystemFile(self.text_file_path)
        self.assertEquals(text_file.get_contents(), self.text_file_contents)


    '''
        The system must be able to set the contents of a file.
        Test is successful if changes are made that match the expected outcome.
    '''

    def test_set_file_contents(self):
        from fsentity import FileSystemFile, FileSystemDirectory
        from fsprocedures import FileSystemProcedures

        d = FileSystemDirectory(self.test_dir)
        d.create_file(self.set_name, self.set_contents)

        file_data = ""

        with open(self.set_path, "r") as f:
            file_data = f.read()

        self.assertEquals(file_data, self.set_contents)

    '''
        The system will need to update a file's contents from a differential format.
        The test is successful if the resulting file contents matches the result of the original content with
        a supplied delta.
    '''

    def test_set_file_from_diff(self):
        from fsentity import FileSystemFile
        from fsprocedures import FileSystemProcedures
        path = ""
        e = FileSystemEntity(path)
        f = e.getFile()
        f.set_from_diff("abc")


    ''' Identify byte encoding '''

    def test_identify_encoding(self):
        from fsentity import FileSystemFile
        from fsprocedures import FileSystemProcedures

        text_file = FileSystemFile(self.text_file_path)
        self.failUnless(text_file.get_encoding().startswith(self.text_file_encoding))

        script_file = FileSystemFile(self.script_file_path)
        self.assertEqual(self.script_file_encoding, script_file.get_encoding())

    ''' Identify EOL format '''

    def test_identify_line_ending(self):
        from fsentity import FileSystemFile
        from fsprocedures import FileSystemProcedures

        f = FileSystemFile(self.text_file_path)
        self.assertEqual(self.text_file_eol, f.get_line_ending())

        f = FileSystemFile(self.script_file_path)
        self.assertEqual(self.script_file_eol, f.get_line_ending())

    ''' ... code style? '''

    def test_identify_format(self):
        from fsentity import FileSystemFile
        from fsprocedures import FileSystemProcedures

        lang = FileSystemFile(self.script_file_path).get_programming_language()
        self.assertEqual("Python", lang)