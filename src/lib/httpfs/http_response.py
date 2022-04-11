from datetime import datetime

HTTP_VERSION = 1.0
SERVER = "test"
LINE_BREAK = "\r\n"


def get_http_date():
    date = datetime.now()
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][date.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, date.day, month,
                                                    date.year, date.hour, date.minute, date.second)


class HttpResponse:
    def __init__(self, status, content_type, body=""):
        self.__status = status
        self.__content_type = content_type
        self.__body = body
        self.__headers = []
        self.__raw = ""

    def add_header(self, key, value):
        self.__headers.append((key, value))

    def build(self):
        self.__raw = ""
        self.__raw = "HTTP/{0} {1} {2}{3}".format(HTTP_VERSION, int(self.__status), self.__status, LINE_BREAK)
        self.__raw += "Server: {0}{1}".format(SERVER, LINE_BREAK)
        self.__raw += "Date: {0}{1}".format(get_http_date(), LINE_BREAK)
        self.__raw += "Content-Type: {0}{1}".format(self.__content_type, LINE_BREAK)
        self.__raw += "Connection: close{0}".format(LINE_BREAK)
        self.__raw += "Content-Length: {0}{1}".format(len(self.__body.encode()), LINE_BREAK)

        for header in self.__headers:
            self.__raw += "{0}: {1}{2}".format(header[0], header[1], LINE_BREAK)

        self.__raw += LINE_BREAK
        self.__raw += self.__body
        self.__raw += LINE_BREAK
        return self.__raw
