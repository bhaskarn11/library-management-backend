from pydantic import BaseModel
from typing import Union, List, Literal, Any, Dict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
