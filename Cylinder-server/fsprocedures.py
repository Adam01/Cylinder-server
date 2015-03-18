__author__ = 'Adam'

from json_callable import *
from fsentity import *
import os


class UserAreaError(RuntimeError):
    def __str__(self):
        return "Tried to access directory outside user area"



class FileSystemProcedures(JSONCallable):
    def __init__(self, username, user_dir):
        JSONCallable.__init__(self)
        self.username = username
        self.user_dir = FileSystemDirectory(user_dir)

    def correct_path(self, path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        if not self.user_dir.parent_of(path):
            log.err("%s not in %s" % (path, self.user_dir.get_path()))
            raise UserAreaError()

        return path

    def jsonrpc_create_file(self, path, name, contents=None):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        fsdir.create_file(name, contents)

    def jsonrpc_create_directory(self, path, name):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        fsdir.create_directory(name)

    def jsonrpc_move_entity(self, source, target):
        source = self.correct_path(source)
        target = self.correct_path(target)

        entity = FileSystemEntity(source)

        target_dir_path = os.path.dirname(target)
        target_name = os.path.basename(target)

        target_dir = FileSystemDirectory(target_dir_path)

        if target_dir.exists(target_name):
            raise Exception("Target entity already exists")

        entity.move_to(target_dir, target_name)

    def jsonrpc_remove_entity(self, path):
        path = self.correct_path(path)
        entity = FileSystemEntity(path)
        entity.remove()

    # def jsonrpc_copy_entity(self, source, target):
    #    self.check_in_user_path(source)
    #    self.check_in_user_path(target)
    #    pass

    def jsonrpc_list_dir(self, path):
        path = self.correct_path(path)

        return FileSystemDirectory(path).list()