__author__ = 'Adam'

# import watchdog for monitoring file system events
import os
import stat
import copy
import sys
import getpass
from enum import Enum
import shutil
from chardet.universaldetector import UniversalDetector

types = Enum('FSEntityType', 'file directory other')


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

            sd = win32security.GetFileSecurity(self.path, win32security.OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            self.owner, _domain, _type = win32security.LookupAccountSid(None, owner_sid)
        elif sys.platform.startswith("linux"):
            import pwd

            self.owner = pwd.getpwuid(self.__stat.st_uid).pw_name

    def copy_to(self, target_entity):
        shutil.copystat(self.path, target_entity.get_path())

        if sys.platform.startswith("linux"):
            os.chown(target_entity.get_path(), self.__stat.st_uid, self.__stat.st_gid)

        target_entity.update_meta()



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


    """ These aren't very smart
    def copy_to(self, target_dir, target_name=None, recursive=True, on_enter_dir=None, on_copied_file=None):
        instance = self.get_type_instance()
        if isinstance(instance, FileSystemDirectory):
            return instance.copy_to(target_dir, target_name, recursive=recursive, on_enter_dir=on_enter_dir,
                                    on_copied_file=on_copied_file)
        elif isinstance(instance, FileSystemFile):
            return instance.copy_to(target_dir, target_name)
        return None
    """

    def call_instance_func(self, func_str, **kwargs):
        type = self.get_type_instance()
        if type is not None:
            if hasattr(type, func_str):
                return getattr(type, func_str)(**kwargs)
        return None


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

        created_file = FileSystemFile(file_path)

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

    def list(self):
        return os.listdir(self.get_path())

    def copy_to(self, target_dir, target_name=None, recursive=True, on_enter_dir=None, on_copied_file=None):
        if not isinstance(target_dir, FileSystemDirectory):
            target_dir = FileSystemDirectory(target_dir)
        if target_name is None:
            target_name = self.get_base_name()
        if target_dir.exists(target_name):
            # TODO: raise entity exists error
            pass

        contents = self.list()

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
                # TODO: warn of unknown entity
                pass
            elif to_copy.is_file():
                copied = to_copy.copy_to(target_dir=target_path_dir, target_name=None)
                if on_copied_file:
                    on_copied_file(original_dir=self, target_dir=target_dir, target_path_dir=target_path_dir,
                                   original=to_copy, copied=copied)
            elif to_copy.is_directory():
                copied = to_copy.copy_to(target_dir=target_path_dir, recursive=recursive, on_enter_dir=on_enter_dir,
                                         on_copied_file=on_copied_file)

        return target_path_dir


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

    def copy_to(self, target_dir, target_name=None):
        if not isinstance(target_dir, FileSystemDirectory):
            target_dir = FileSystemDirectory(target_dir)
        if target_name is None:
            target_name = self.get_base_name()
        if target_dir.exists(target_name):
            # TODO: raise entity exists error
            pass

        target_path = target_dir.join_name(target_name)
        shutil.copy2(self.get_path(), target_path)

        target_entity = FileSystemEntity(target_path)
        self.meta.copy_to(target_entity)

        return target_entity

    def get_encoding(self):
        detector = UniversalDetector()
        for line in file(self.get_path(), 'rb'):
            detector.feed(line)
            if detector.done: break
        detector.close()
        return detector.result["encoding"].upper()


    def get_line_ending(self, known_encoding=None):
        import codecs

        if known_encoding is None:
            known_encoding = self.get_encoding()
        # Encoding is definitely needed for this
        f = codecs.open(self.get_path(), 'rb', encoding=known_encoding)
        s = f.read(1000)  # If a new line isn't in this, it's probably not a text file


        # This counts the occurrences of LF, CR, and CRLF's in the sample string
        results = dict()
        results["LF"] = 0
        results["CRLF"] = 0
        results["CR"] = 0

        start = 0

        while True:
            lf_loc = s.find('\n', start)
            cr_loc = s.find('\r', start)

            if cr_loc == -1 and lf_loc == -1:  # None found
                break
            elif lf_loc == -1:  # Only found CR TODO: check if the CR is at the end of the sample
                results["CR"] += 1
                break
            elif cr_loc == -1:  # Only found LF
                results["LF"] += 1
                break
            elif cr_loc == lf_loc - 1:  # Found CRLF
                results["CRLF"] += 1
                start = lf_loc + 1
            elif cr_loc > lf_loc:  # Found LF and then a CR, need to see if there's another LF after the CR
                results["LF"] += 1
                start = cr_loc
            elif lf_loc > cr_loc:  # Found CR and then a LF, count both
                results["CR"] += 1
                results["LF"] += 1
                start = lf_loc + 1

        most_used, ignored = max(results.iteritems(), key=lambda x: x[1])

        return most_used

    def get_eol_char(self, known_line_ending=None, known_encoding=None):
        if known_line_ending is None:
            known_line_ending = self.get_line_ending(known_encoding=known_encoding)
        if known_line_ending == "CR":
            return '\r'
        elif known_line_ending == "CRLF":
            return "\r\n"
        elif known_line_ending == "LF":
            return "\n"
        else:
            return None

    def get_programming_language(self):
        from pygments.lexers import guess_lexer, guess_lexer_for_filename

        with open(self.get_path(), "r") as f:
            return guess_lexer_for_filename(self.get_base_name(), f.read(2048)).name

    def get_crc32(self):
        import zlib

        prev = 0
        for eachLine in open(self.get_path(), "rb"):
            prev = zlib.crc32(eachLine, prev)
        return prev

    # Alter a files content from a compressed ndiff mapping (see useful.py : make_comp_diff ),
    def set_from_comp_diff(self, diff_obj, original_crc=None, known_encoding=None, known_eol_char=None,
                           known_line_ending=None):

        import codecs
        import tempfile
        import zlib

        if known_encoding is None:
            known_encoding = self.get_encoding()

        if known_eol_char is None:
            known_eol_char = self.get_eol_char(known_encoding=known_encoding, known_line_ending=known_line_ending)

        temp_dir = FileSystemDirectory(tempfile.mkdtemp())
        in_file_obj = self.copy_to(temp_dir)

        # TODO investigate whether encoding is needed
        in_file = codecs.open(in_file_obj.get_path(), 'rb', encoding=known_encoding)

        self.remove()
        out_file = codecs.open(self.get_path(), "wb", encoding=known_encoding)

        temp_crc = 0
        current_line = 1;

        line_list = sorted(diff_obj)
        last_line = line_list[-1]
        for line in line_list:
            ops = diff_obj[line]

            while current_line < line:
                preserved_data = in_file.readline()
                temp_crc = zlib.crc32(preserved_data, temp_crc)
                out_file.write(preserved_data)
                current_line += 1
                #print current_line-1, "Preserving:", preserved_data[:-1]

            #The file pointer is now at the start of the line we want to modify

            op_count = len(ops) - 1
            for op_i, op in enumerate(ops):
                last_op = (last_line == line) and (op_i == op_count)
                if op.startswith("- "):
                    removed_data = in_file.readline()
                    #print current_line, "Removing:", removed_data[:-1]
                elif op.startswith("+ "):
                    # Don't add a newline if last op in diff (I still don't know why this works)
                    added_data = ( op[2:] ) if last_op else ( op[2:] + known_eol_char)
                    temp_crc = zlib.crc32(added_data, temp_crc)
                    out_file.write(added_data)
                    #print current_line, "Adding:", added_data[:-1]

        # Write rest of file
        remaining_data = in_file.read()
        if len(remaining_data) > 0:
            #print "Remaining data:", remaining_data
            temp_crc = zlib.crc32(remaining_data, temp_crc)
            out_file.write(remaining_data)

        in_file.close()
        out_file.close()

        #print original_crc, temp_crc

        if original_crc is not None:
            if original_crc != temp_crc:
                self.remove()
                in_file_obj.move_to(self.get_dir_obj())
                self.update_meta()
                print "CRC's don't match"
                # TODO throw error
                return False

        temp_dir.remove()
        self.update_meta()

        return True
