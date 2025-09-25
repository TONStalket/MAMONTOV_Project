"""Pydantic schemas for request and response models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=500)


class UserPublic(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class PostCreate(PostBase):
    pass


class PostPublic(PostBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FeedResponse(BaseModel):
    posts: List[PostPublic]


class FollowersResponse(BaseModel):
    followers: List[UserPublic]
    following: List[UserPublic]
