from database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    creator = relationship("User", back_populates="posts")
    user_id = Column(Integer, ForeignKey("users.id"))

class User(Base):
    
     __tablename__ = "users"

     id = Column(Integer, primary_key=True, index=True)
     name = Column(String)
     email = Column(String)
     password = Column(String)
     posts = relationship("Post", back_populates="creator")