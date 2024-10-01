from typing import Union, Annotated

from fastapi import FastAPI, Depends, HTTPException
from models import Base, User
from schemas import UserSchema, UserUpdate
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import auth
from auth import get_current_user
from sqlalchemy.orm.exc import UnmappedInstanceError



Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# dp_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]


@app.get("/all")
def all_users(user:user_dependency,db:Session=Depends(get_db)):
    if user is None:
        return HTTPException(status_code=401, detail="Authentication Failed")
    users = db.query(User).all()
    return users

@app.get("/user/{user_name}")
def get_users(user:user_dependency,user_name, db:Session=Depends(get_db)):
    if user is None:
        return HTTPException(status_code=401, detail="Authentication Failed")
    
    user = db.query(User).filter(User.name == user_name).first()
    return user

@app.post("/adduser")
def add_user(user:user_dependency, request:UserSchema,db:Session=Depends(get_db)):
    if user is None:
        return HTTPException(status_code=401, detail="Authentication Failed")
    
    user = User(name=request.name, email=request.email, nickname=request.nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



@app.put("/users/{user_id}", response_model=UserUpdate)
def update_user(user:user_dependency, user_id:int, user_update:UserUpdate, db:Session=Depends(get_db)):
    if user is None:
        return HTTPException(status_code=401, detail="Authentication Failed")
    user_to_update = db.query(User).filter(User.id == user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_to_update.name = user_update.name
    user_to_update.email = user_update.email
    user_to_update.nickname = user_update.nickname

    db.commit()
    db.refresh(user_to_update)

    return user_to_update

@app.delete("/users/{user_id}")
def delete_user_info(user:user_dependency, user_id:int,db:Session=Depends(get_db)):
    if user is None:
        return HTTPException(status_code=401, detail="Authentication Failed")
    
    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
        return {"Message": "User deleted Successfully!"}
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
    

