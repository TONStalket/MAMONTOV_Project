"""Post management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_active_user, get_db

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=schemas.PostPublic, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
) -> schemas.PostPublic:
    post = models.Post(author_id=current_user.id, content=post_in.content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/", response_model=schemas.FeedResponse)
def list_posts(db: Session = Depends(get_db), current_user: models.User = Depends(get_active_user)) -> schemas.FeedResponse:
    followed_ids = [user.id for user in current_user.following] + [current_user.id]
    posts = (
        db.query(models.Post)
        .filter(models.Post.author_id.in_(followed_ids))
        .order_by(models.Post.created_at.desc())
        .all()
    )
    return schemas.FeedResponse(posts=posts)


@router.get("/{post_id}", response_model=schemas.PostPublic)
def get_post(post_id: int, db: Session = Depends(get_db)) -> schemas.PostPublic:
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
