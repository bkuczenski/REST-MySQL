from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from database import Base

class Interface(Base):
    __tablename__ = 'Interfaces'

    InterfaceId = Column(Integer, primary_key=True)
    InterfaceName = Column(Text, nullable=False)


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

    GrantId = Column(Integer, primary_key=True)
    UserId = Column(ForeignKey('Users.UserId'), nullable=False, index=True)
    Origin = Column(Text, nullable=False)
    InterfaceId = Column(ForeignKey('Interfaces.InterfaceId'), nullable=False, index=True)
    GrantDuration = Column(Integer, nullable=False)
    Qdb = Column(Boolean, nullable=False)
    Values = Column(Boolean, nullable=False)
    Update = Column(Boolean, nullable=False)
    HasQuota = Column(Boolean, nullable=False)
    CreationDate = Column(DateTime, nullable=False)
    Expires = Column(DateTime, nullable=False)
    TokenQuota = Column(Integer, nullable=False)
    TokenCount = Column(Integer, nullable=False)
    QueryCount = Column(Integer, nullable=False)

    Interface = relationship('Interface')
    User = relationship('User')


class Issuer(Base):
    __tablename__ = 'Issuers'

    IssuerId = Column(Integer, primary_key=True)
    IssuerUser = Column(ForeignKey('Users.UserId'), nullable=False, index=True)
    IssuerName = Column(Text, nullable=False)
    PrivateKey = Column(Text, nullable=False)
    PublicKey = Column(Text, nullable=False)
    Expiry = Column(DateTime, nullable=False)

    User = relationship('User')


class Resource(Base):
    __tablename__ = 'Resources'

    ResourceId = Column(Integer, primary_key=True)
    Issuer = Column(ForeignKey('Issuers.IssuerId'), nullable=False, index=True)
    Origin = Column(Text, nullable=False)
    ResourceName = Column(Text, nullable=False)
    ResourceDescription = Column(Text, nullable=False)
    ResourceUrl = Column(Text, nullable=False)
    Interface = Column(ForeignKey('Interfaces.InterfaceId'), nullable=False, index=True)
    CreationDate = Column(DateTime, nullable=False)
    MajorRelease = Column(Integer, nullable=False)
    MinorRelease = Column(Integer, nullable=False)
    Patch = Column(Integer, nullable=False)

    Interface1 = relationship('Interface')
    Issuer1 = relationship('Issuer')