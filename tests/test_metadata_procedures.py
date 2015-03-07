__author__ = 'Adam'

import unittest
import os
import getpass
import tempfile
import random
import string


class TestMetaDataProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = getpass.getuser()
        handle, cls.file_path = tempfile.mkstemp()
        cls.file_size = random.randint(1000, 100000)
        cls.file_data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(cls.file_size))
        os.write(handle, cls.file_data)
        os.close(handle)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.file_path)

    def test_get_entity_owner(self):
        from fsentity.fsentity import EntityMetadata

        e = EntityMetadata(self.file_path)
        self.assertEquals(e.owner, self.user, "Owner of file does not match current user")

    def test_get_entity_permissions(self):
        from fsentity.fsentity import EntityMetadata

        e = EntityMetadata(self.file_path)
        e.get_access_matrix()
        e.get_user_acccess()
        e.get_group_access()
        e.get_global_access()
        e.get_read_access()
        e.get_write_access()
        e.get_execute_access()
        pass

    def test_get_entity_timestamps(self):
        from fsentity.fsentity import EntityMetadata

        e = EntityMetadata(self.file_path)
        print e.accessed
        print e.created
        print e.modified

    def test_get_entity_sizes(self):
        from fsentity.fsentity import FileSystemEntity

        e = FileSystemEntity(self.file_path)
        self.assertEquals(e.get_size(), self.file_size, "Expected file size not returned")
        self.assertEquals(e.get_type_instance().get_size(), self.file_size, "Expected file size not returned")

        e.get_type_instance().get_size()  # count size of contents, recursively
        e.get_type_instance().get_content_count()  # get number of child items

        pass
