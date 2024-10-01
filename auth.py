from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from models import Base, FrontendUser
from schemas import CreateUserRequest, Token
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


SECRET_KEY = "HelloWorld"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(db:db_dependency,create_user_request:CreateUserRequest):
    create_user_model = FrontendUser(
        user_name = create_user_request.username,
        password = bcrypt_context.hash(create_user_request.password)
    )

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user."
                            )
    token = create_access_token(username=user.user_name, user_id=user.id)
    return {'access_token': token, 'token_type':'bearer'}

def authenticate_user(username:str, password:str, db):
    user = db.query(FrontendUser).filter(FrontendUser.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username:str, user_id:int):
    encode1 = {'sub':username, 'id':user_id}
    return jwt.encode(encode1, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        user_id: int = payload.get('id')
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate User"
                )
        return {'username':username, "id":user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user'
                            )