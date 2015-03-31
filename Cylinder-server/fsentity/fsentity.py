__author__ = 'Adam'

# TODO: import watchdog for monitoring file system events
import os
import stat
import sys
import getpass
from enum import Enum
import shutil

types = Enum('FSEntityType', 'file directory other')

FileSystemFile = None
FileSystemDirectory = None


class EntityException(Exception):
    def __init__(self, path, err):
        self.path = path
        self.error = err

    def __str__(self):
        return self.path + ": " + self.error


class EntityAccessError(EntityException):
    def __init__(self, path, err):
        EntityException.__init__(self, path, err)

class EntityMetadata:
    def __init__(self, path):
        self.path = path
        self.__stat = os.stat(self.path)
        self.mode = self.__stat.st_mode
        self.created = self.__stat.st_ctime
        self.accessed = self.__stat.st_atime
        self.modified = self.__stat.st_mtime
        self.owner = None

        if sys.platform.startswith("win"):
            import win32security

            sd = win32security.GetFileSecurity(
                self.path, win32security.OWNER_SECURITY_INFORMATION
            )

            owner_sid = sd.GetSecurityDescriptorOwner()
            self.owner, _domain, _type = win32security.LookupAccountSid(
                None, owner_sid
            )
        elif sys.platform.startswith("linux"):
            import pwd

            self.owner = pwd.getpwuid(self.__stat.st_uid).pw_name

    def copy_to(self, target_entity):
        shutil.copystat(self.path, target_entity.get_path())

        if sys.platform.startswith("linux"):
            os.chown(
                target_entity.get_path(), self.__stat.st_uid,
                self.__stat.st_gid
            )

        target_entity.update_meta()


def get_enum_type(mode):
    if stat.S_ISDIR(mode):
        return types.directory
    elif stat.S_ISREG(mode):
        return types.file
    else:
        return types.other


"""
Paths must be absolute when creating FileSystem* instances, these classes
represent an existing entity in the file system and won't take into account
the current working directory.
"""


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

    def get_dir_obj(self):
        return FileSystemDirectory(self.get_dir_name())

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
            return None

    def get_size(self):
        return os.path.getsize(self.meta.path)

    def is_under(self, target_dir):
        if not isinstance(target_dir, FileSystemDirectory):
            target_dir = FileSystemDirectory(target_dir)
        return self.get_path().startswith(target_dir.get_path())

    def parent_of(self, path):
        return os.path.normcase(path).startswith(
            os.path.normcase(self.get_path()))

    def equals(self, path):
        return os.path.normcase(os.path.abspath(path)) == os.path.normcase(
            self.get_path())

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
        self.__init__(target_path)

    """
    These aren't very smart
    """

    # def copy_to(self, target_dir, target_name=None, recursive=True,
    #             on_enter_dir=None, on_copied_file=None):
    #     instance = self.get_type_instance()
    #     if isinstance(instance, FileSystemDirectory):
    #         return instance.copy_to(target_dir, target_name,
    #                                 recursive=recursive,
    #                                 on_enter_dir=on_enter_dir,
    #                                 on_copied_file=on_copied_file)
    #     elif isinstance(instance, FileSystemFile):
    #         return instance.copy_to(target_dir, target_name)
    #     return None

    def call_instance_func(self, func_str, **kwargs):
        entity_type = self.get_type_instance()
        if entity_type is not None:
            if hasattr(type, func_str):
                return getattr(entity_type, func_str)(**kwargs)
        return None

    def remove(self):
        os.remove(self.get_path())

    def get_info(self):
        info = dict()
        info["title"] = self.get_base_name()
        info["size"] = self.get_size()

        ftype = self.get_type()
        if ftype is types.directory:
            info["type"] = "directory"
        elif ftype is types.file:
            info["type"] = "file"
        else:
            info["type"] = "unknown"

        meta = self.get_meta()

        info["created"] = meta.created
        info["modified"] = meta.modified
        info["accessed"] = meta.accessed
        info["path"] = meta.path
        info["owner"] = meta.owner

        return info
