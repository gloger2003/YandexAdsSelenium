from enum import Enum, auto


class STATUS(Enum):
    OK = (auto(), '')
    BAD = (auto(), '')
    BAD_URL = (auto(), '')
    BAD_PROXY = (auto(), '')
    FATAL_ERROR = (auto(), '')
    CONNECTION_ERROR = (auto(), '')
    INTERNAL_LINK_TAGS_NOT_FOUND = (auto(), '')
    INTERNAL_LINK_TAG_WAS_NOT_CLICKED = (auto(), '')

    def __init__(self, id: int, msg: str) -> None:
        self.id = id
        self.msg = msg
