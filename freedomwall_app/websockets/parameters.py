from typing import Optional


class Params:
    def __init__(
        self,
        id: Optional[int] = None,
        creator: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.id = id
        self.creator = creator
        self.title = title
