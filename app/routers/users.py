"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_active_user, get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserPublic)
def read_current_user(current_user: models.User = Depends(get_active_user)) -> schemas.UserPublic:
    return current_user


@router.patch("/me", response_model=schemas.UserPublic)
def update_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
) -> schemas.UserPublic:
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/{user_id}/follow", response_model=schemas.UserPublic)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
) -> schemas.UserPublic:
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user in current_user.following:
        return target_user

    current_user.following.append(target_user)
    db.commit()
    db.refresh(target_user)
    return target_user


@router.get("/{user_id}/network", response_model=schemas.FollowersResponse)
def get_network(user_id: int, db: Session = Depends(get_db)) -> schemas.FollowersResponse:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return schemas.FollowersResponse(
        followers=list(user.followers),
        following=list(user.following),
    )
