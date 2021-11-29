from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Interface(Base):
    __tablename__ = 'Interfaces'

    interface_id = Column('InterfaceId', Integer, primary_key=True)
    interface_name = Column('InterfaceName', Text, nullable=False)


class UserType(Base):
    __tablename__ = 'UserTypes'

    user_type_id = Column('UserTypeId', Integer, primary_key=True)
    user_type = Column('UserType', Text, nullable=False)

class User(Base):
    __tablename__ = 'Users'

    user_id = Column('UserId', Integer, primary_key=True)
    name = Column('Name',Text, nullable=False)
    email = Column('Email', Text, nullable=False)
    password = Column('HashedPassword', Text, nullable=False)
    user_type = Column('UserType', ForeignKey('UserTypes.UserTypeId'), nullable=False, index=True)
    is_active = Column('IsActive', Boolean, nullable=False, default=0)

    user_type1 = relationship('UserType')


class Grant(Base):
    __tablename__ = 'Grants'

    grant_id = Column('GrantId', Integer, primary_key=True)
    user_id = Column('UserId', ForeignKey('Users.UserId'), nullable=False, index=True)
    origin = Column('Origin', Text, nullable=False)
    resource_id = Column('ResourceId', ForeignKey('Resources.ResourceId'), nullable=False, index=True)
    grant_duration = Column('GrantDuration', Integer, nullable=False)
    qdb = Column('Qdb', Boolean, nullable=False)
    values = Column('Values', Boolean, nullable=False)
    update = Column('Update', Boolean, nullable=False)
    has_quota = Column('HasQuota', Boolean, nullable=False)
    creation_date = Column('CreationDate', DateTime, nullable=False)
    expires = Column('Expires', DateTime, nullable=False)
    token_quota = Column('TokenQuota', Integer, nullable=False)
    token_count = Column('TokenCount', Integer, nullable=False)
    query_count = Column('QueryCount', Integer, nullable=False)

    resource = relationship('Resource')
    user = relationship('User')


class Issuer(Base):
    __tablename__ = 'Issuers'

    issuer_id = Column('IssuerId', Integer, primary_key=True)
    issuer_user = Column('IssuerUser', ForeignKey('Users.UserId'), nullable=False, index=True)
    issuer_name = Column('IssuerName', Text, nullable=False)
    key_lifetime = Column('KeyLifetime', Integer, nullable=False)
    private_key = Column('PrivateKey', Text, nullable=False)
    public_key = Column('PublicKey', Text, nullable=False)
    expiry = Column('Expiry', DateTime, nullable=False)

    user = relationship('User')


class Resource(Base):
    __tablename__ = 'Resources'

    resource_id = Column('ResourceId', Integer, primary_key=True)
    issuer = Column('Issuer' ,ForeignKey('Issuers.IssuerId'), nullable=False, index=True)
    origin = Column('Origin', Text, nullable=False)
    resource_name = Column('ResourceName', Text, nullable=False)
    resource_description = Column('ResourceDescription', Text, nullable=False)
    resource_url = Column('ResourceUrl', Text, nullable=False)
    interface = Column('Interface', ForeignKey('Interfaces.InterfaceId'), nullable=False, index=True)
    creation_date = Column('CreationDate', DateTime, nullable=False)
    major_release = Column('MajorRelease', Integer, nullable=False)
    minor_release = Column('MinorRelease', Integer, nullable=False)
    patch = Column('Patch', Integer, nullable=False)

    interface1 = relationship('Interface')
    issuer1 = relationship('Issuer')