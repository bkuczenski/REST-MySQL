from re import A
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, session
from sqlalchemy.sql.functions import current_user
from starlette.status import HTTP_406_NOT_ACCEPTABLE
from security_handler import SecurityHandler
import models, schemas
from sqlalchemy import inspect

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_type_by_id(db: Session, user_type_id: int):
    return db.query(models.UserType).filter(models.UserType.user_type_id == user_type_id).first() 

def get_user_type_by_type(db: Session, user_type: str):
    return db.query(models.UserType).filter(models.UserType.user_type == user_type).first() 

def create_user(db: Session, user: schemas.UserInDB):
    security_handler_obj = SecurityHandler()
    hashed_password = security_handler_obj.hash_password(user.password)
    curr_user_type = get_user_type_by_type(db, user.user_type)
    if not curr_user_type:
        raise HTTPException(status_code=400, detail="User type not available")
    db_user = models.User(name=user.name, email=user.email, password=hashed_password, user_type=curr_user_type.user_type_id, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_type_same(db: Session, user: models.User, put_user: schemas.UserInDB):
    user_type = get_user_type_by_id(db, user.user_type)
    if put_user.user_type != user_type.user_type:
        raise HTTPException(status_code=400, detail="Changing user type not available")
    return user_type.user_type_id

def update_user(db: Session, user: models.User, put_user: schemas.UserInDB):
    put_user_type_id = get_user_type_same(db, user, put_user)
    security_handler_obj = SecurityHandler()
    hashed_password = security_handler_obj.hash_password(put_user.password)

    put_user.user_type = put_user_type_id
    put_user.password = hashed_password
    db.query(models.User).filter(models.User.email == put_user.email).update(put_user.dict())
    db.commit()
    return get_user_by_email(db, put_user.email)

def delete_user(db: Session, user: schemas.User):
    db.query(models.User).filter(models.User.user_id == user.user_id).delete()
    db.commit()


def model_as_dict(model):
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
