# coding: utf-8
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Pswd(Base):
    __tablename__ = 'PSWD'

    USR = Column(String(6), primary_key=True)
    NAME = Column(String(20))
