class Response:
    def __init__(self, raw):
        self.__raw = raw

    def get_formatted_response(self):
        response = ""
        for line in self.__raw:
            if line == "":
                response += "\n"
            else:
                response += line + "\n"
        return response

    def get_status(self):
        return self.__raw[0].split(" ")[2]

    def get_status_code(self):
        return int(self.__raw[0].split(" ")[1])

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
