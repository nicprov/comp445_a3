from lib.tcp import TCP
from .http_response import HttpResponse
from .http_request import HttpRequest
from .http_method import HttpMethod
from .http_status import HttpStatus
from .file_manager import FileManager
from .content_type import ContentType

BUFFER_SIZE = 1024


ROUTER_IP = "0.0.0.0"
ROUTER_PORT = 3000


class Http:
    def __init__(self, verbose, port, data_dir="."):
        self.__verbose = verbose
        self.__host = "localhost"
        self.__port = port
        self.__fileManager = FileManager(data_dir)

    # def start(self):
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     try:
    #         s.bind((self.__host, self.__port))
    #     except socket.error as e:
    #         print("Unable to bind to: {0}:{1}".format(self.__host, self.__port))
    #         exit(1)
    #     s.listen(1)
    #     print("Listening on port {0}".format(self.__port))
    #     try:
    #         while(True):
    #             conn, address = s.accept()
    #             data = conn.recv(BUFFER_SIZE)
    #             if data is None:
    #                 break
    #             self.__handle_request(conn, data)
    #     except KeyboardInterrupt as e:
    #         print("Gracefully exiting...")
    #         s.shutdown(socket.SHUT_RDWR)
    #         s.close()
    #         exit(0)


    def start(self):
        print("Listening on: %s" % self.__port)
        try:
            while True:
                conn = TCP(ROUTER_IP, ROUTER_PORT)
                conn.listen(self.__port)
                data = conn.recv()
                if data is None:
                    break
                self.__handle_request(conn, data)
        except KeyboardInterrupt:
            print("Gracefully exiting...")
            exit(0)

    def __handle_request(self, conn, data):
        request = HttpRequest(data)
        response = None

        # Check if valid http method (only GET/POST supported)
        method = request.get_http_method()
        if method != HttpMethod.GET and method != HttpMethod.POST:
            response = HttpResponse(HttpStatus.NOT_IMPLEMENTED, ContentType.PLAIN).build()
        else:
            if request.get_path() == "/" and request.get_http_method() == HttpMethod.GET:
                response = self.__fileManager.get_list_of_files()
            elif request.get_path().startswith("/") and request.get_http_method() == HttpMethod.GET:
                response = self.__fileManager.get_file(request.get_path())
            elif request.get_path().startswith("/") and request.get_http_method() == HttpMethod.POST:
                response = self.__fileManager.create_file(request.get_path(), request.get_body())

        if self.__verbose:
            print("-----REQUEST RECEIVED-----\n")
            print(request.get_formatted_request())
            print("-----SENDING RESPONSE-----\n")
            print(response)

        conn.send(response.encode())
