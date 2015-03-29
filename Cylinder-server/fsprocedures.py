__author__ = 'Adam'

from json_callable import JSONCallableEscape, JSONCallable
from fsentity import FileSystemDirectory, FileSystemEntity, FileSystemFile
import os
from subject import EventSubject
from twisted.internet import reactor
import functools


class ResponseBase:
    def __init__(self, _id, method, status):
        self.id = _id
        self.method = method
        self.status = status


class TaskError(ResponseBase, JSONCallableEscape):
    def __init__(self, _id, method, err):
        ResponseBase.__init__(self, id, method, "Error")
        self.error = err

    def __str__(self):
        return self.__dict__


class TaskInitiated(ResponseBase):
    def __init__(self, _id, method, data=None):
        ResponseBase.__init__(self, id, method, "Initiated")
        self.data = data


class TaskProgressing(ResponseBase):
    def __init__(self, _id, method, progress, data):
        ResponseBase.__init__(self, id, method, "Progressing")
        self.progress = progress
        self.data = data


class TaskCompleted(ResponseBase):
    def __init__(self, _id, method, result, data):
        ResponseBase.__init__(self, id, method, "Completed")
        self.result = result
        self.data = data


class CopyTaskHandler:
    def __init__(self, fsprocs, _id, method, source, target, total):
        self.fsprocs = fsprocs
        self.id = id
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

    def correct_path(self, path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        if not self.user_dir.parent_of(path):
            # log.err("%s not in %s" % (path, self.user_dir.get_path()))
            print "%s not in %s" % (path, self.user_dir.get_path())
            self.raise_error("Path is outside user area")

        return path

    def complete_task(self, result, data):
        return TaskCompleted(self.current_id, self.current_method, result,
                             data)

    def jsonrpc_create_file(self, path, name, contents=None):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        new_file = fsdir.create_file(name, contents)

        return self.complete_task(True, {path: new_file.get_path()})

    def jsonrpc_create_directory(self, path, name):
        path = self.correct_path(path)

        fsdir = FileSystemDirectory(path)
        new_dir = fsdir.create_directory(name)

        return self.complete_task(True, {path: new_dir.get_path()})

    def jsonrpc_move_entity(self, source, target):
        source = self.correct_path(source)
        target = self.correct_path(target)

        entity = FileSystemEntity(source).get_type_instance()

        target_dir_path = os.path.dirname(target)
        target_name = os.path.basename(target)

        target_dir = FileSystemDirectory(target_dir_path)

        if target_dir.exists(target_name):
            raise self.raise_error("Target entity already exists")

        entity.move_to(target_dir, target_name)

        return self.complete_task(True, {source: source, target: target})

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
            entity.copy_to(target_dir, target_name)
            return self.complete_task(True, {source: source, target: target})
        else:
            self.raise_error("Unhandled file type")

    def jsonrpc_remove_entity(self, path):
        path = self.correct_path(path)
        entity = FileSystemEntity(path)
        entity.remove()

        return self.complete_task(True, path)

    def jsonrpc_list_dir(self, path):
        path = self.correct_path(path)
        data = {
            "path": path,
            "list": FileSystemDirectory(path).list_contents()
        }
        return self.complete_task(True, data)
