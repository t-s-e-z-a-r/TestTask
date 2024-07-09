from pydantic import BaseModel
from typing import Optional


class UserSchema(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    msg: str


class UserUpdateSchema(BaseModel):
    auto_respond: Optional[bool] = None
    respond_time: Optional[int] = None
