from datetime import datetime
from re import A
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, session
from sqlalchemy.sql.functions import current_user
from starlette.status import HTTP_406_NOT_ACCEPTABLE
from security_handler import SecurityHandler
import models, schemas
from sqlalchemy import inspect

"""User methods"""
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

def create_user(db: Session, user: schemas.UserCreate):
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

def get_user_type_same(db: Session, user: models.User, put_user: schemas.UserCreate):
    user_type = get_user_type_by_id(db, user.user_type)
    if put_user.user_type != user_type.user_type:
        raise HTTPException(status_code=400, detail="Changing user type not available")
    return user_type.user_type_id

def update_user(db: Session, user: models.User, put_user: schemas.UserCreate):
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

"""Issuer methods"""
def check_issuer(db: Session, user_id):
    try:
        user_type = db.query(models.UserType, models.User) \
            .filter(models.UserType.user_type_id == models.User.user_type).filter(models.User.user_id == user_id).first()[0]
    except:
        raise HTTPException(status_code=400, detail="User provided for creating issuer not found")

    return user_type.user_type

def create_issuer(db: Session, issuer: schemas.IssuerCreate):    
    if check_issuer(db, issuer.issuer_user) != 'issuer':
        raise HTTPException(status_code=400, detail="User provided for creating issuer is not of type 'issuer'")
    # key_lifetime, private_key, public_key are mocked, expiry_date is current time
    db_issuer = models.Issuer(issuer_user=issuer.issuer_user, issuer_name=issuer.issuer_name, 
                            key_lifetime=0, private_key='mock', public_key='mock', expiry=datetime.now())
    db.add(db_issuer)
    db.commit()
    db.refresh(db_issuer)
    return db_issuer

def get_issuers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Issuer).offset(skip).limit(limit).all()

def get_issuer(db: Session, issuer_id: int):
    return db.query(models.Issuer).filter(models.Issuer.issuer_id == issuer_id).first()

def get_issuer_resources(db: Session, issuer_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).filter(models.Resource.issuer == issuer_id).offset(skip).limit(limit).all()

"""Resource methods"""
def get_interface_by_id(db: Session, interface_id: int):
    return db.query(models.Interface).filter(models.Interface.interface_id == interface_id).first() 

def get_interface_by_name(db: Session, interface_name: str):
    return db.query(models.Interface).filter(models.Interface.interface_name == interface_name).first() 

def create_resource(db: Session, resource: schemas.ResourceCreate):
    curr_interface = get_interface_by_name(db, resource.interface)
    if not curr_interface:
        raise HTTPException(status_code=400, detail="Interface name not available")
    
    try:
        # creation_date is current time, major/minor release and patch are mocked = 0
        db_resource = models.Resource(issuer=resource.issuer, origin=resource.origin, resource_name=resource.resource_name, 
                                    resource_description=resource.resource_description, 
                                    resource_url=resource.resource_url, interface=curr_interface.interface_id, 
                                    creation_date=datetime.now(), major_release=0, minor_release=0, patch=0)
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
    except:
        raise HTTPException(status_code=400, detail="Issuer provided for creating resource not found")
    return db_resource

def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Resource).offset(skip).limit(limit).all()

def get_resource(db: Session, resource_id: int):
    return db.query(models.Resource).filter(models.Resource.resource_id == resource_id).first()
    

def update_resource(db: Session, resource: models.Resource, put_resource: schemas.ResourceCreate):
    curr_interface = get_interface_by_name(db, put_resource.interface)
    if not curr_interface:
        raise HTTPException(status_code=400, detail="Interface name not available")

    put_resource.interface = curr_interface.interface_id
    try:
        db.query(models.Resource).filter(models.Resource.resource_id == resource.resource_id).update(put_resource.dict())
        db.commit()
    except:
        raise HTTPException(status_code=400, detail="Issuer provided for updating resource not found")
    return get_resource(db, resource.resource_id)

"""Grant methods"""
def create_grant(db: Session, grant: schemas.GrantCreate):
    try:
        # creation_date and expires are current time
        db_grant = models.Grant(user_id=grant.user_id, origin=grant.origin, resource_id=grant.resource_id, 
                                    grant_duration=grant.grant_duration, qdb=grant.qdb, values=grant.values,
                                    update=grant.update, has_quota=grant.has_quota, creation_date=datetime.now(), 
                                    expires=datetime.now(), token_quota=grant.token_quota, 
                                    token_count=grant.token_count, query_count=grant.query_count)
        db.add(db_grant)
        db.commit()
        db.refresh(db_grant)
    except:
        raise HTTPException(status_code=400, detail="User or Resource Id provided for creating grant not found")

    return db_grant

def get_grants_by_resource_id(db: Session, resource_id: int):
    return db.query(models.Grant).filter(models.Grant.resource_id == resource_id).all()

def get_grants_by_user_id(db: Session, user_id: int):
    return db.query(models.Grant).filter(models.Grant.user_id == user_id).all()

def get_grant(db: Session, grant_id: int):
    return db.query(models.Grant).filter(models.Grant.grant_id == grant_id).first()
    
def get_grants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Grant).offset(skip).limit(limit).all()

def update_grant(db: Session, grant: schemas.Grant, put_grant: schemas.GrantCreate):
    try:
        db.query(models.Grant).filter(models.Grant.grant_id == grant.grant_id).update(put_grant.dict())
        db.commit()
    except:
        raise HTTPException(status_code=400, detail="User or Resource Id provided for updating grant not found")
    return get_grant(db, grant.grant_id)

def delete_grant(db: Session, grant: schemas.Grant):
    db.query(models.Grant).filter(models.Grant.grant_id == grant.grant_id).delete()
    db.commit()

def model_as_dict(model):
    return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
