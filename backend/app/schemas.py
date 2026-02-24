from pydantic import BaseModel
from typing import Optional


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    image: Optional[str] = None