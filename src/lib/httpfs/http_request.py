LINE_BREAK = "\r\n"


class HttpRequest:
    def __init__(self, raw):
        self.__raw = raw.split(LINE_BREAK)

    def get_formatted_request(self):
        request = ""
        for line in self.__raw:
            if line == "":
                request += "\n"
            else:
                request += line + "\n"
        return request

    def get_http_method(self):
        return self.__raw[0].split(" ")[0]

    def get_path(self):
        path = self.__raw[0].split(" ")[1]
        return path.split("?")[0]

    def get_query_params(self):
        path = self.__raw[0].split(" ")[1]
        return path.split("?")[1]

    def get_header(self, header):
        for line in self.__raw:
            if line == "":
                return None
            else:
                parsed_header = line.split(":")
                if parsed_header[0] == header:
                    if len(parsed_header) == 3:
                        return (parsed_header[1] + parsed_header[2]).strip()
                    else:
                        return parsed_header[1].strip()
        return None

    def get_body(self):
        is_body = False
        body = ""
        for line in self.__raw:
            if line == "":
                is_body = True
            elif is_body:
                body += line
        return body
