import os
import glob
from .http_response import HttpResponse
from .http_status import HttpStatus
from .content_type import ContentType


class FileManager:
    def __init__(self, data_dir):
        self.__data_dir = data_dir

    def get_list_of_files(self):
        try:
            files = self.__list_of_files()
            return HttpResponse(HttpStatus.OK, ContentType.PLAIN, str(files)).build()
        except Exception as e:
            return HttpResponse(HttpStatus.INTERNAL_SERVER_ERROR, ContentType.PLAIN).build()

    def get_file(self, path):
        try:
            if "../" in path:
                return HttpResponse(HttpStatus.FORBIDDEN, ContentType.PLAIN).build()
            if path[1:] not in self.__list_of_files():
                return HttpResponse(HttpStatus.NOT_FOUND, ContentType.PLAIN).build()
            with open(self.__data_dir + path, "r") as file:
                return HttpResponse(HttpStatus.OK, ContentType.PLAIN, file.read()).build()
        except Exception:
            return HttpResponse(HttpStatus.INTERNAL_SERVER_ERROR, ContentType.PLAIN).build()

    def create_file(self, path, body):
        try:
            if "../" in path:
                return HttpResponse(HttpStatus.FORBIDDEN, ContentType.PLAIN).build()
            dir = path.rsplit('/', 1)[0]
            os.makedirs(self.__data_dir + dir, exist_ok=True)
            with open(self.__data_dir + path, "w") as file:
                file.write(body)
                if path not in self.__list_of_files():
                    return HttpResponse(HttpStatus.CREATED, ContentType.PLAIN).build()
                else:
                    return HttpResponse(HttpStatus.OK, ContentType.PLAIN).build()
        except Exception:
            return HttpResponse(HttpStatus.INTERNAL_SERVER_ERROR, ContentType.PLAIN).build()

    def __list_of_files(self):
        files = []
        for file in glob.iglob("./" + self.__data_dir + "/**", recursive=True):
            files.append(file.split("./" + self.__data_dir + "/")[1])
        return [f for f in files if os.path.isfile("./" + self.__data_dir + "/" + f)]


