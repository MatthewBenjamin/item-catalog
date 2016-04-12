from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    name  = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    #email?
    #picture???

class Category(Base):
    __tablename__ = 'category'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    #serialize property

class Item(Base):
    __tablename__ = 'item'

    name = Column(String(250), nullable = False)
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    #serialize property