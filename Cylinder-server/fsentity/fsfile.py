import chardet
from chardet.universaldetector import UniversalDetector
import codecs
import copy
import shutil

import fsentity
from fsentity import FileSystemEntity, types


class FileSystemFile(FileSystemEntity):
    def __init__(self, path_base):
        if isinstance(path_base, FileSystemEntity):
            self.__dict__.update(copy.deepcopy(path_base.__dict__))
        else:
            FileSystemEntity.__init__(self, path_base)

    def get_type(self):
        return types.file

    def get_contents_raw(self):
        with open(self.get_path(), 'rb') as f:
            return f.read()

    def get_contents(self, known_encoding=None):
        if known_encoding is None:
            known_encoding = self.get_encoding()
        elif known_encoding.lower() == "raw":
            return self.get_contents_raw()

        with codecs.open(self.get_path(), 'rb', encoding=known_encoding) as f:
            return f.read(), known_encoding

    """
        set_contents

        Write data in the form of target_encoding.
        'detect' will, if supplied a byte string, use chardet to figure out the encoding and write it as is
        if a supplied unicode, 'detect' will assume utf-8

        'current' will use the encoding currently in the file

        'raw' will bypass encoding
    """

    def set_contents(self, data, target_encoding="detect"):
        if target_encoding.lower() == "raw":
            self.set_contents_raw(data)

        if isinstance(data, str) or isinstance(data, bytes):
            if target_encoding.lower() == "detect":
                target_encoding = chardet.detect(data)["encoding"]
            elif target_encoding.lower() == "current":
                target_encoding = self.get_encoding()

        elif isinstance(data, unicode):
            if target_encoding.lower() == "detect":
                target_encoding = "utf-8"
            elif target_encoding.lower() == "current":
                target_encoding = self.get_encoding()

        # print "writing", target_encoding, data
        with codecs.open(self.get_path(), 'wb', encoding=target_encoding) as f:
            f.write(data)


    def set_contents_raw(self, data):
        with open(self.get_path(), "wb") as f:
            f.write(data)


    def copy_to(self, target_dir, target_name=None):
        if not isinstance(target_dir, fsentity.FileSystemDirectory):
            target_dir = fsentity.FileSystemDirectory(target_dir)
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

    def get_encoding(self, default_to="ascii"):
        detector = UniversalDetector()
        for line in file(self.get_path(), 'rb'):
            detector.feed(line)
            if detector.done: break
        detector.close()
        return detector.result["encoding"] or default_to


    def get_line_ending(self, known_encoding=None):
        import codecs

        if known_encoding is None:
            known_encoding = self.get_encoding()

        with codecs.open(self.get_path(), 'rb', encoding=known_encoding) as f:
            sample = f.read(1000)  # If a new line isn't in this, it's probably not a text file

        # This counts the occurrences of LF, CR, and CRLF's in the sample string
        results = dict()
        results["LF"] = 0
        results["CRLF"] = 0
        results["CR"] = 0

        start = 0

        while True:
            lf_loc = sample.find('\n', start)
            cr_loc = sample.find('\r', start)

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

        return most_used, results

    def get_eol_char(self, known_line_ending=None, known_encoding=None, default_to="\n"):
        if known_line_ending is None:
            known_line_ending, unused = self.get_line_ending(known_encoding=known_encoding)
        if known_line_ending == "CR":
            return '\r'
        elif known_line_ending == "CRLF":
            return "\r\n"
        elif known_line_ending == "LF":
            return "\n"
        else:
            return default_to

    def get_programming_language(self):
        from pygments.lexers import guess_lexer, guess_lexer_for_filename

        with open(self.get_path(), "r") as f:
            return guess_lexer_for_filename(self.get_base_name(), f.read()).name

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

        temp_dir = fsentity.FileSystemDirectory(tempfile.mkdtemp())
        in_file_obj = self.copy_to(temp_dir)

        # TODO investigate whether encoding is needed
        in_file = codecs.open(in_file_obj.get_path(), 'rb', encoding=known_encoding)

        self.remove()
        out_file = codecs.open(self.get_path(), "wb", encoding=known_encoding)

        temp_crc = 0
        current_line = 1

        line_list = sorted(diff_obj)
        last_line = line_list[-1]
        for line in line_list:
            ops = diff_obj[line]

            while current_line < line:
                preserved_data = in_file.readline()
                temp_crc = zlib.crc32(preserved_data, temp_crc)
                out_file.write(preserved_data)
                current_line += 1
                # print current_line-1, "Preserving:", preserved_data[:-1]

            # The file pointer is now at the start of the line we want to modify

            op_count = len(ops) - 1
            for op_i, op in enumerate(ops):
                last_op = (last_line == line) and (op_i == op_count)
                if op.startswith("- "):
                    #removed_data =
                    in_file.readline()
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
            # print "Remaining data:", remaining_data
            temp_crc = zlib.crc32(remaining_data, temp_crc)
            out_file.write(remaining_data)

        in_file.close()
        out_file.close()

        # print original_crc, temp_crc

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


fsentity.FileSystemFile = FileSystemFile