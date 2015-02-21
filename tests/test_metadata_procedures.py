__author__ = 'Adam'

import unittest
import sys
import os


class TestSSLConnectivity(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_entity_owner(self):
        path = ""
        e = FileSystemEntity(path)
        e.get_owner()
        pass

    def test_get_entity_group(self):
        path = ""
        e = FileSystemEntity(path)
        e.get_owner_group()
        pass

    def test_get_entity_permissions(self):
        path = ""
        e = FileSystemEntity(path)
        e.get_access_matrix()
        e.get_user_acccess()
        e.get_group_access()
        e.get_global_access()
        e.get_read_access()
        e.get_write_access()
        e.get_execute_access()
        pass

    def test_get_entity_timestamps(self):
        path = ""
        e = FileSystemEntity(path)
        e.get_last_accessed()
        e.get_last_modified()
        e.get_created()
        pass

    def test_get_entity_sizes(self):
        path = ""
        e = FileSystemEntity(path)
        e.get_size()  # by default uses stat along
        e.get_file().get_size()  # count contents
        e.get_directory().get_size()  # count size of contents, recursively
        e.get_directory().get_content_count()  # get number of child items

        pass
