from pydantic import BaseModel

class UserSchema(BaseModel):
    name:str
    email:str
    nickname:str


class CreateUserRequest(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class UserUpdate(BaseModel):
    name:str
    email:str
    nickname:str