from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.dependencies import get_db
from src.post import crud, schemas
from src.post.comment.schemas import CommentCreate, CommentsRead, CommentTree
from src.user import auth
from src.user.models import User

router = APIRouter()


@router.get(
    "/posts",
    response_model=list[schemas.PostReadDetail],
    tags=["Post"],
)
async def read_posts(db: AsyncSession = Depends(get_db)):
    return await crud.get_posts(db)


@router.get(
    "/post/{post_id}",
    response_model=schemas.PostReadDetail,
    tags=["Post"],
)
async def post_read_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_post_by_id(db, post_id)


@router.post(
    "/posts",
    response_model=schemas.PostCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Post"],
)
async def post_create(
    post_data: schemas.PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.current_user),
):
    post = await crud.post_create(db=db, post_data=post_data, user=user)
    return post


@router.patch(
    "/post/{post_id}",
    response_model=schemas.PostCreateResponse,
    tags=["Post"],
)
async def post_update(
    post_id: int,
    post_data: schemas.PostUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.current_user),
):
    post = await crud.post_update(db=db, post_id=post_id, post_data=post_data)
    return schemas.PostCreateResponse.from_orm(post)


@router.delete(
    "/post/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Post"],
)
async def delete_post(
    db: AsyncSession = Depends(get_db),
    post_id: int = None,
    user: User = Depends(auth.current_user),
):
    return await crud.post_delete(db=db, post_id=post_id)


@router.get(
    "/post/{post_id}/comments",
    response_model=list[CommentTree],
    tags=["Comment"],
)
async def get_comments_by_post_id(post_id: int, db: AsyncSession = Depends(get_db)):
    # comments = await crud.get_comments_by_post(post_id, db)
    return await crud.get_comments_tree(db, post_id)


@router.get(
    "/comments/{comment_id}",
    response_model=CommentsRead,
    tags=["Comment"],
)
async def get_children_comments_by_parent_id(
    comment_id: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_comment_by_comment_id(db, comment_id)


@router.get(
    "/comments/{parent_id}/children",
    response_model=list[CommentsRead],
    tags=["Comment"],
)
async def get_children_comments_by_parent_id(
    parent_id: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_children_comments(db, parent_id)


@router.post(
    "/posts/{post_id}/comment",
    response_model=CommentsRead,
    tags=["Comment"],
    status_code=status.HTTP_201_CREATED,
)
async def comment_create(
    post_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth.current_user),
):
    return await crud.create_comment(
        post_id=post_id, db=db, comment_data=comment_data, user=user
    )


@router.delete(
    "/comments/{comment_id}",
    tags=["Comment"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    db: AsyncSession = Depends(get_db),
    comment_id: int = None,
    user: User = Depends(auth.current_user),
):
    return await crud.delete_comment(db=db, comment_id=comment_id)
