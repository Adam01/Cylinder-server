import difflib
import shutil

__author__ = 'Adam'

import unittest
import os
import useful


class TestFileContentProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "./tests/data/"

        cls.text_file_name = "TextFile_UTF16_CRLF.txt"
        cls.text_file_path = os.path.join(cls.test_dir, cls.text_file_name)
        cls.text_file_encoding = "UTF-16BE"
        cls.text_file_eol = "CRLF"

        import codecs

        with codecs.open(cls.text_file_path, 'rb',
                         encoding=cls.text_file_encoding) as f:
            cls.text_file_contents = f.read()

        cls.script_file_name = "ScriptFile_UTF8_LF.py"
        cls.script_file_path = os.path.join(cls.test_dir, cls.script_file_name)
        cls.script_file_encoding = "UTF-8"
        cls.script_file_eol = "LF"

        with codecs.open(cls.script_file_path, 'rb',
                         encoding=cls.script_file_encoding) as f:
            cls.script_file_contents = f.read()

        cls.set_contents = cls.text_file_contents
        cls.set_name = "TestSetContents.txt"
        cls.set_path = os.path.join(cls.test_dir, cls.set_name)

        # diff testing
        cls.diff_target_path = os.path.join(cls.test_dir, "ScriptFile_Copy.py")
        shutil.copyfile(cls.script_file_path, cls.diff_target_path)

        cls.diff_new_path = os.path.join(cls.test_dir,
                                         "ScriptFile_Diff_Test.py")

        with open(cls.diff_target_path, "rb") as f:
            target_data = f.read().split("\n")

        with open(cls.diff_new_path, "rb") as f:
            new_data = f.read().split("\n")

        diff_data = difflib.ndiff(target_data, new_data)
        diff_data = list(diff_data)
        cls.comp_diff_data = useful.make_comp_diff(diff_data)

    @classmethod
    def tearDownClass(cls):
        # os.remove(cls.set_path)
        # os.remove(cls.diff_target_path)
        pass

    '''
    The system is required to be able to obtain the content of a file.
    This test is successful if the content is matched as is with expected data.
    '''

    def test_get_file_contents(self):
        from fsentity import FileSystemFile

        script_file = FileSystemFile(self.script_file_path)
        self.assertEquals(script_file.get_contents()[0],
                          self.script_file_contents)

        text_file = FileSystemFile(self.text_file_path)
        self.assertEquals(text_file.get_contents()[0], self.text_file_contents)

    '''
    The system must be able to set the contents of a file.
    Test is successful if changes are made that match the expected outcome.
    '''

    def test_set_file_contents(self):
        from fsentity import FileSystemDirectory

        d = FileSystemDirectory(self.test_dir)
        d.create_file(self.set_name, self.set_contents)

        import codecs

        with codecs.open(self.set_path, 'rb', encoding="utf-8") as f:
            file_data = f.read()

        # print file_data

        self.assertEquals(file_data, self.set_contents)

    '''
    The system will need to update a file's contents from a differential
    format.
    The test is successful if the resulting file contents matches the result
    of the original content with
    a supplied delta.
    '''

    def test_set_file_from_diff(self):
        from fsentity import FileSystemFile

        target_file = FileSystemFile(self.diff_target_path)
        diff_crc = FileSystemFile(self.diff_new_path).get_crc32()
        self.assertTrue(target_file.set_from_comp_diff(self.comp_diff_data,
                                                       original_crc=diff_crc))

    ''' Identify byte encoding '''

    def test_identify_encoding(self):
        from fsentity import FileSystemFile

        text_file = FileSystemFile(self.text_file_path)
        self.assertEqual(
            text_file.get_encoding().upper(),
            self.text_file_encoding
        )

        script_file = FileSystemFile(self.script_file_path)
        self.assertEqual(self.script_file_encoding,
                         script_file.get_encoding().upper())

    ''' Identify EOL format '''

    def test_identify_line_ending(self):
        from fsentity import FileSystemFile

        f = FileSystemFile(self.text_file_path)
        self.assertEqual(self.text_file_eol, f.get_line_ending()[0])

        f = FileSystemFile(self.script_file_path)
        self.assertEqual(self.script_file_eol, f.get_line_ending()[0])

    ''' ... code style? '''

    def test_identify_format(self):
        from fsentity import FileSystemFile

        lang = FileSystemFile(self.script_file_path).get_programming_language()
        self.assertEqual("Python", lang)
