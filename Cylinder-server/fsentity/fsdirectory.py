import os
import copy
import shutil

import fsentity
from fsentity import FileSystemEntity, types


class NotADirectory(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Path is not a directory: '%s'" % self.path

class FileSystemDirectory(FileSystemEntity):
    def __init__(self, path_base):
        if isinstance(path_base, FileSystemEntity):
            if path_base.get_type() != types.directory:
                raise NotADirectory(path_base.get_path())
            self.__dict__.update(copy.deepcopy(path_base.__dict__))

        else:
            if not os.path.isdir(path_base):
                raise NotADirectory(path_base)

            FileSystemEntity.__init__(self, path_base)

    def get_type(self):
        return types.directory

    def get_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.get_path()):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def count_entities(self, recursive=False):
        count = 0
        for dirpath, dirnames, filenames in os.walk(self.get_path()):
            count += len(dirnames) + len(filenames)
        return count

    def count_files(self, recursive=False):
        count = 0
        for dirpath, dirnames, filenames in os.walk(self.get_path()):
            count += len(filenames)
        return count

    def exists(self, name):
        return os.path.exists(os.path.join(self.get_path(), name))

    def remove(self):
        shutil.rmtree(self.get_path())

    def join_name(self, name):
        return os.path.join(self.get_path(), name)

    def create_file(self, name, contents=None):
        file_path = os.path.join(self.get_path(), name)

        if os.path.exists(file_path):
            # TODO: throw error
            pass

        with open(file_path, 'w'):
            pass

        created_file = fsentity.FileSystemFile(file_path)

        if contents is not None:
            created_file.set_contents(contents)

        return created_file

    def create_directory(self, name):
        dir_path = os.path.join(self.get_path(), name)
        if os.path.exists(dir_path):
            # TODO: throw error
            pass
        os.mkdir(dir_path)
        return FileSystemDirectory(dir_path)

    def list_basic(self):
        list = os.listdir(self.get_path())
        list.sort()
        return list

    def list_contents(self):
        collection = list()
        for title in self.list_basic():
            collection.append(FileSystemEntity(self.join_name(title)).get_info())
        return collection


    def copy_to(self, target_dir, target_name=None, recursive=True, on_enter_dir=None, on_copied_file=None):
        if not isinstance(target_dir, FileSystemDirectory):
            target_dir = FileSystemDirectory(target_dir)
        if target_name is None:
            target_name = self.get_base_name()
        if target_dir.exists(target_name):
            # TODO: raise entity exists error
            pass

        contents = self.list_basic()

        # target path  = target dir/this name/
        target_path = target_dir.join_name(target_name)
        os.mkdir(target_path)

        # where all the child entities go into (target dir/this name)
        target_path_dir = FileSystemDirectory(target_path)

        if on_enter_dir:
            on_enter_dir(original_dir=self, target_dir=target_dir, target_path_dir=target_path_dir,
                         target_name=target_name)

        for name in contents:
            to_copy = FileSystemEntity(self.join_name(name)).get_type_instance()
            if to_copy is None:
                if os.path.islink(self.join_name(name)):
                    linkto = os.readlink(self.join_name(name))
                    os.symlink(linkto, target_dir.join_name(name))
                # TODO: warn of unknown entity
            elif to_copy.is_file():
                copied = to_copy.copy_to(target_dir=target_path_dir, target_name=None)
                if on_copied_file:
                    on_copied_file(original_dir=self, target_dir=target_dir, target_path_dir=target_path_dir,
                                   original=to_copy, copied=copied)
            elif to_copy.is_directory():
                copied = to_copy.copy_to(target_dir=target_path_dir, recursive=recursive, on_enter_dir=on_enter_dir,
                                         on_copied_file=on_copied_file)

        return target_path_dir


fsentity.FileSystemDirectory = FileSystemDirectory