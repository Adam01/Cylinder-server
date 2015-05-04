import types

__author__ = 'Adam'

from json_callable import JSONCallable, JSONError
from fsentity import FileSystemDirectory, FileSystemEntity, FileSystemFile, EntityException
import os
from subject import EventSubject
from twisted.internet import reactor
import functools


class ResponseBase:
    def __init__(self, _id, method, status):
        self.id = _id
        self.method = method
        self.status = status


class TaskError(ResponseBase, Exception):
    def __init__(self, _id, method, err):
        ResponseBase.__init__(self, _id, method, "Error")
        self.error = err



class TaskInitiated(ResponseBase):
    def __init__(self, _id, method, data=None):
        ResponseBase.__init__(self, _id, method, "Initiated")
        self.data = data


class TaskProgressing(ResponseBase):
    def __init__(self, _id, method, progress, data):
        ResponseBase.__init__(self, _id, method, "Progressing")
        self.progress = progress
        self.data = data


class TaskCompleted(ResponseBase):
    def __init__(self, _id, method, result, data):
        ResponseBase.__init__(self, _id, method, "Completed")
        self.result = result
        self.data = data


class CopyTaskHandler:
    def __init__(self, fsprocs, _id, method, source, target, total):
        self.fsprocs = fsprocs
        self.id = _id
        self.method = method
        self.source = source
        self.target = target
        self.total = float(total)
        self.count = 0.0

    def on_enter_dir(self, original_dir, target_dir, target_path_dir,
                     target_name):
        data = dict()
        data["source"] = self.source
        data["target"] = self.target
        data["msg"] = "Copying directory: '%s' to '%s'" % (
            original_dir.get_path(), target_dir.get_path()
        )

        task = TaskProgressing(self.id, self.method, self.count / self.total,
                               data)
        self.fsprocs.notify("Tasks", task.__dict__)

    def on_copied_file(self, original_dir, target_dir, target_path_dir,
                       original, copied):
        self.count += 1
        data = dict()
        data["source"] = self.source
        data["target"] = self.target
        data["msg"] = "Copied file: '%s' to '%s'" % (
            original.get_path(), copied.get_path()
        )

        task = TaskProgressing(self.id, self.method, self.count / self.total,
                               data)
        self.fsprocs.notify("Tasks", task.__dict__)

    def perform_copy(self, entity, target_dir, target_name):
        on_enter_dir = functools.partial(reactor.callFromThread,
                                         self.on_enter_dir)
        on_copied_file = functools.partial(reactor.callFromThread,
                                           self.on_copied_file)

        entity.copy_to(target_dir=target_dir,
                       target_name=target_name,
                       recursive=True,
                       on_enter_dir=on_enter_dir,
                       on_copied_file=on_copied_file
                       )
        reactor.callLater(0, self.fsprocs.notify, "Tasks",
                          TaskCompleted(self.id, self.method, True,
                                        {"source": self.source,
                                         "target": self.target,
                                         "count": self.count}
                                        ).__dict__
                          )

    def initialise(self, entity, target_dir, target_name):
        reactor.callInThread(self.perform_copy, entity=entity,
                             target_dir=target_dir, target_name=target_name)
        return TaskInitiated(self.id, self.method,
                             {"source": self.source, "target": self.target,
                              "total": self.total})


class FileSystemProcedures(JSONCallable, EventSubject):
    def __init__(self, username, user_dir):
        JSONCallable.__init__(self)
        EventSubject.__init__(self)
        self.username = username
        self.user_dir = FileSystemDirectory(user_dir)

    def raise_error(self, err):
        raise TaskError(self.current_id, self.current_method, err)

    def on_exception(self):
        if isinstance(self.current_exception, TaskError):
            self.current_result = self.current_exception
        elif isinstance(self.current_exception, EntityException):
            self.current_result = TaskError(self.current_id, self.current_method, str(self.current_exception))
        else:
            return False
        return True

    def post_process(self):
        if isinstance(self.current_result, ResponseBase):
            self.current_result = self.current_result.__dict__
        elif not isinstance(self.current_result, types.DictType):
            raise JSONError("unhandled return type: %s" % str(type(self.current_result)))

        if "callback_id" in self.current_input:
            self.current_result["callback_id"] = self.current_input["callback_id"]


    def correct_path(self, path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        if not self.user_dir.parent_of(path):
            # log.err("%s not in %s" % (path, self.user_dir.get_path()))
            print "%s not in %s" % (path, self.user_dir.get_path())
            self.raise_error("Path is outside user area")

        return path

    def complete_task(self, result, data=dict()):
        return TaskCompleted(self.current_id, self.current_method, result,
                             data)

    def jsonrpc_create_file(self, path, name, contents=None):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        try:
            new_file = fsdir.create_file(name, contents)
        except OSError, e:
            return self.raise_error(str(e))
        return self.complete_task(True, {"path": new_file.get_path()})

    def jsonrpc_create_directory(self, path, name):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        try:
            new_dir = fsdir.create_directory(name)
        except OSError, e:
            return self.raise_error(str(e))

        return self.complete_task(True, {"path": new_dir.get_path()})

    def jsonrpc_move_entity(self, source, target):
        source = self.correct_path(source)
        target = self.correct_path(target)

        entity = FileSystemEntity(source).get_type_instance()

        target_dir_path = os.path.dirname(target)
        target_name = os.path.basename(target)

        target_dir = FileSystemDirectory(target_dir_path)

        if target_dir.exists(target_name):
            raise self.raise_error("Target entity already exists")

        try:
            entity.move_to(target_dir, target_name)
        except OSError, e:
            return self.raise_error(str(e))

        return self.complete_task(True, {"source": source, "target": target})

    def jsonrpc_copy_entity(self, source, target):
        source = self.correct_path(source)
        target = self.correct_path(target)

        entity = FileSystemEntity(source).get_type_instance()

        target_dir_path = os.path.dirname(target)
        target_name = os.path.basename(target)

        target_dir = FileSystemDirectory(target_dir_path)

        if target_dir.exists(target_name):
            raise self.raise_error("Target entity already exists")

        if isinstance(entity, FileSystemDirectory):
            total = entity.count_files(recursive=True)
            handler = CopyTaskHandler(self, self.current_id,
                                      self.current_method, source, target,
                                      total)
            return handler.initialise(entity, target_dir, target_name)
        elif isinstance(entity, FileSystemFile):
            try:
                entity.copy_to(target_dir, target_name)
            except OSError, e:
                return self.raise_error(str(e))
            return self.complete_task(True, {"source": source, "target": target})
        else:
            self.raise_error("Unhandled file type")

    def jsonrpc_remove_entity(self, path):
        path = self.correct_path(path)
        entity = FileSystemEntity(path)
        try:
            entity.remove()
        except OSError, e:
            return self.raise_error(str(e))

        return self.complete_task(True, path)

    def jsonrpc_list_dir(self, path):
        path = self.correct_path(path)
        data = {
            "path": path,
            "list": FileSystemDirectory(path).list_contents()
        }
        return self.complete_task(True, data)

    def jsonrpc_get_path_separator(self):
        return self.complete_task(True, os.sep)

    def jsonrpc_get_file_contents(self, path):
        path = self.correct_path(path)
        file = FileSystemFile(path)
        file_data, encoding = file.get_contents()
        line_ending = file.get_line_ending(known_encoding=encoding)[0]
        file_mime = file.get_mime_type()
        file_lang = file.get_programming_language()
        data = dict()
        data["path"] = path
        data["encoding"] = encoding
        data["eol"] = line_ending
        data["data"] = file_data.encode("utf-8")
        data["lang"] = file_lang
        data["mime"] = file_mime
        return self.complete_task(True, data)

    def jsonrpc_set_file_contents(self, path, data, encoding="current"):
        path = self.correct_path(path)

        file = FileSystemFile(path)
        data = data.decode("utf-8")
        try:
            file.set_contents(data, encoding)
        except OSError, e:
            return self.raise_error(str(e))
        return self.complete_task(True)