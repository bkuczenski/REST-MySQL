from calendar import c
import re
from sqlalchemy.sql.functions import current_user
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
import uvicorn
from dataclasses import asdict

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import db_operations, models, schemas
from security_handler import SecurityHandler
from database import SessionLocal, engine
from fastapi_login import LoginManager
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_login.exceptions import InvalidCredentialsException

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Testing purposes
# @app.get("/users/me/", response_model=schemas.User)
# async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
#     return current_user

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user_db = db_operations.get_user_by_email(next(get_db()), email=token_data.email)
    if user_db is None:
        raise credentials_exception
    return schemas.User(**db_operations.model_as_dict(user_db))


def get_current_user_type(current_user: schemas.User):
    return db_operations.get_user_type_by_id(next(get_db()), current_user.user_type)

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post('/auth/token', response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    security_handler_obj = SecurityHandler()
    user = security_handler_obj.authenticate_user(next(get_db()), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserInDB, curr_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if get_current_user_type(curr_user).user_type != 'admin':
        raise HTTPException(status_code=401, detail="User is not authorized to perform operation")

    db_user = db_operations.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_operations.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, curr_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if get_current_user_type(curr_user).user_type != 'admin':
        raise HTTPException(status_code=401, detail="User is not authorized to perform operation")
    users = db_operations.get_users(db, skip=skip)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, curr_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if get_current_user_type(curr_user).user_type == 'issuer':
        raise HTTPException(status_code=401, detail="User is not authorized to perform operation")
    
    db_user = db_operations.get_user(db, user_id=user_id)
    if get_current_user_type(curr_user).user_type == 'admin':
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    elif get_current_user_type(curr_user).user_type == 'normal':
        if curr_user.user_id == db_user.user_id:
            return db_user
        else:
            raise HTTPException(status_code=404, detail="User is not authorized to perform operation")

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user: schemas.UserInDB, user_id: int, curr_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if get_current_user_type(curr_user) == 'issuer':
        raise HTTPException(status_code=401, detail="User is not authorized to perform operation")
    
    db_user = db_operations.get_user(db, user_id=user_id)
    if get_current_user_type(curr_user).user_type == 'admin':
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_operations.update_user(db, db_user, user)
        
    elif get_current_user_type(curr_user).user_type == 'normal':
        if curr_user.user_id == db_user.user_id:
            return db_operations.update_user(db, db_user, user)
        else:
            raise HTTPException(status_code=404, detail="User is not authorized to perform operation")

@app.delete("/users/{user_id}")
def delete_user(user_id: int, curr_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not get_current_user_type(curr_user).user_type == 'admin':
        raise HTTPException(status_code=404, detail="User is not authorized to perform operation")
    
    db_user = db_operations.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_operations.delete_user(db, db_user)
    return {'User with ID {} deleted successfully'.format(user_id)}

# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return db_operations.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = db_operations.get_items(db, skip=skip, limit=limit)
#     return items


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)