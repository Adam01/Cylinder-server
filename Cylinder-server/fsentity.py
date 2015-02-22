__author__ = 'Adam'

# import watchdog for monitoring file system events
import os
import stat
import copy
import sys
import getpass
from enum import Enum

types = Enum('FSEntityType', 'file directory other')


class EntityMetadata:
    def __init__(self, path):
        self.path = path
        stat_result = os.stat(self.path)
        self.mode = stat_result.st_mode
        self.created = stat_result.st_ctime
        self.accessed = stat_result.st_atime
        self.modified = stat_result.st_mtime
        self.owner = None

        if sys.platform.startswith("win"):
            import win32security

            sd = win32security.GetFileSecurity(self.path, win32security.OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            self.owner, _domain, _type = win32security.LookupAccountSid(None, owner_sid)
        elif sys.platform.startswith("linux"):
            import pwd

            self.owner = pwd.getpwuid(stat_result.st_uid).pw_name


def get_enum_type(mode):
    if stat.S_ISDIR(mode):
        return types.directory
    elif stat.S_ISREG(mode):
        return types.file
    else:
        return types.other


'''
        Paths must be absolute when creating FileSystem* instances, these classes represent an existing entity in
        the file system and won't take into account the current working directory.
'''


class FileSystemEntity:
    def __init__(self, path):
        self.meta = EntityMetadata(path)
        self.type = get_enum_type(self.meta.mode)

    def get_meta(self):
        return self.meta

    def update_meta(self):
        self.meta = EntityMetadata(self.meta.path)
        self.type = get_enum_type(self.meta.mode)
        return self.meta

    def get_path(self):
        return self.meta.path

    def get_type(self):
        return self.type

    def get_owner(self):
        return self.get_meta().owner

    def same_process_user(self):
        return self.get_owner() == getpass.getuser()

    def get_base_name(self):
        return os.path.basename(self.get_path())

    def get_dir_name(self):
        return os.path.dirname(self.get_path())

    def is_file(self):
        return self.get_type() == types.file

    def is_directory(self):
        return self.get_type() == types.directory

    def get_type_instance(self):
        if self.get_type() == types.file:
            return FileSystemFile(self)
        elif self.get_type() == types.directory:
            return FileSystemDirectory(self)
        else:
            # TODO: Raise type error
            pass

    def get_size(self):
        return os.path.getsize(self.meta.path)

    def move_to(self, target_dir, target_name=None):
        if not isinstance(target_dir, FileSystemDirectory):
            target_dir = FileSystemDirectory(target_dir)
        if target_name is None:
            target_name = self.get_base_name()
        if target_dir.exists(target_name):
            # TODO: raise entity exists error
            pass

        target_path = target_dir.join_name(target_name)
        os.rename(self.get_path(), target_path)
        self.meta = EntityMetadata(target_path)

    def remove(self):
        os.remove(self.get_path())


class FileSystemDirectory(FileSystemEntity):
    def __init__(self, path_base):
        if isinstance(path_base, FileSystemEntity):
            self.__dict__.update(copy.deepcopy(path_base.__dict__))
        else:
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

    def exists(self, name):
        return os.path.exists(os.path.join(self.get_path(), name))

    def join_name(self, name):
        return os.path.join(self.get_path(), name)

    def create_file(self, name, contents=None):
        file_path = os.path.join(self.get_path(), name)
        if os.path.exists(file_path):
            # TODO: throw error
            pass
        with open(file_path, 'w') as fh:
            if contents is not None:
                fh.write(contents)
            pass
        return FileSystemFile(file_path)

    def create_directory(self, name):
        dir_path = os.path.join(self.get_path(), name)
        if os.path.exists(dir_path):
            # TODO: throw error
            pass
        os.mkdir(dir_path)
        return FileSystemDirectory(dir_path)


class FileSystemFile(FileSystemEntity):
    def __init__(self, path_base):
        if isinstance(path_base, FileSystemEntity):
            self.__dict__.update(copy.deepcopy(path_base.__dict__))
        else:
            FileSystemEntity.__init__(self, path_base)

    def get_type(self):
        return types.file

    def get_contents(self):
        with open(self.get_path()) as f:
            return f.read()

    def set_contents(self, data):
        with open(self.get_path(), "w") as f:
            f.write(data)
