from .deps import *

from typing import Any, Optional

class Response(SQLModel):
    statusCode: int
    data: Optional[Any]
    message: str
    follows: Optional[Any] = None