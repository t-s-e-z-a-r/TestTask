from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship

from database.config import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    auto_respond = Column(Boolean, default=False)
    respond_time = Column(Integer, default=5)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
