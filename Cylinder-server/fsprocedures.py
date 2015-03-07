__author__ = 'Adam'

from json_callable import *
from fsentity import *
import os

class FileSystemProcedures(JSONCallable):
    def jsonrpc_create_file(self, path, name, contents=None):
        # TODO: validate in user area

        fsdir = FileSystemDirectory(path)
        fsdir.create_file(name, contents)

    def jsonrpc_create_directory(self, path, name):
        # TODO: validate in user area

        fsdir = FileSystemDirectory(path)
        fsdir.create_directory(name)

    def jsonrpc_move_entity(self, source, target):
        # TODO: validate in user area
        entity = FileSystemEntity(source)

        target_dir_path = os.path.dirname(target)
        target_name = os.path.basename(target)

        target_dir = FileSystemDirectory(target_dir_path)

        if target_dir.exists(target_name):
            raise Exception("Target entity already exists")

        entity.move_to(target_dir, target_name)

    def jsonrpc_remove_entity(self, path):
        entity = FileSystemEntity(path)
        entity.remove()
