from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.config import get_async_session
from database.models import User

from .schemas import UserSchema, MessageResponse, TokenResponse, UserUpdateSchema

from .services import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user,
)

from database.config import metadata, Base

auth_router = APIRouter()


@auth_router.post("/register", response_model=MessageResponse)
async def register(user: UserSchema, db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == user.username))
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        hashed_password = hash_password(user.password)
        new_user = User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        return {"msg": "User successfully registered"}


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    data: UserSchema,
    db: AsyncSession = Depends(get_async_session),
):
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == data.username))
        user = result.scalars().first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}


@auth_router.put("/user", response_model=MessageResponse)
async def update_user(
    user_update: UserUpdateSchema,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    async with db.begin():
        user = await db.get(User, user_id)
        if (
            not user
        ):  # It doesn't seem that we could receive this exception but it's better to have this verification
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user_update.auto_respond is not None:
            user.auto_respond = user_update.auto_respond

        if user_update.respond_time is not None:
            if user_update.respond_time <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Respond time must be greater than 0",
                )
            user.respond_time = user_update.respond_time

        await db.commit()
        return {"msg": "User updated successfully"}
