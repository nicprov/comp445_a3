from enum import Enum


class ContentType(Enum):
    JSON = "application/json"
    XML = "application/text"
    PLAIN = "text/plain"
    HTML = "text/html"

    def __str__(self):
        return self.value
