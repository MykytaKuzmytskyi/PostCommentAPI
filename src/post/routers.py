from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.dependencies import get_db
from src.post import crud, schemas
from src.user import auth
from src.user.models import User

router = APIRouter()


@router.get("/posts", response_model=list[schemas.PostReadDetail])
async def read_posts(db: AsyncSession = Depends(get_db)):
    posts = await crud.get_posts(db)
    return [schemas.PostReadDetail.from_orm(post) for post in posts]


@router.get("/post/{post_id}", response_model=schemas.PostReadDetail)
async def post_read_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud.get_post_by_id(db, post_id)
    return schemas.PostReadDetail.from_orm(post)


@router.post("/posts", response_model=schemas.PostCreateResponse)
async def post_create(
    post_data: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.current_user),
):
    post = await crud.post_create(db=db, post_data=post_data, user=user)
    return post


@router.patch(
    "/post/{post_id}",
)
async def post_update(
    post_id: int,
    post_data: schemas.PostUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.current_user),
):
    return await crud.post_update(db=db, post_id=post_id, post_data=post_data)


@router.delete(
    "/post/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route(
    db: AsyncSession = Depends(get_db),
    post_id: int = None,
    user: User = Depends(auth.current_user),
):
    return await crud.post_delete(db=db, post_id=post_id)
