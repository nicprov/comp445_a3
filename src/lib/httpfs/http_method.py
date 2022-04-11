from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __neg__(self, other):
        return self.value != other
