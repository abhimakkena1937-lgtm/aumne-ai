import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Post
from backend.schemas import PostCreate, PostResponse, PostStatus
from backend.moderation import moderate_content
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------





app = FastAPI(
    title="Aumne AI",
    description="AI-Assisted Content Moderation and Publishing Platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://aumne-ai-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------------------------
# HELPER FUNCTION: SERIALIZE POST
# ---------------------------------------------------------

def serialize_post(post: Post) -> dict:
    """
    Convert a SQLAlchemy Post object into a dictionary
    suitable for the API response.
    """

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "status": post.status,
        "flagged_reasons": (
            json.loads(post.flagged_reasons)
            if post.flagged_reasons
            else None
        ),
        "created_at": post.created_at,
    }


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():
    """
    Check whether the Aumne AI API is running.
    """

    return {
        "application": "Aumne AI",
        "message": "Content Moderation API is running",
        "documentation": "/docs",
    }


# ---------------------------------------------------------
# 1. CREATE A NEW DRAFT POST
# ---------------------------------------------------------

@app.post(
    "/posts/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new post with draft status.
    """

    title = post_data.title.strip()

    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title cannot contain only whitespace.",
        )

    post = Post(
        title=title,
        content=post_data.content,
        status="draft",
        flagged_reasons=None,
    )

    try:
        db.add(post)
        db.commit()
        db.refresh(post)

        return serialize_post(post)

    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------------
# 2. SUBMIT A POST FOR MODERATION
# ---------------------------------------------------------

@app.post(
    "/posts/{post_id}/submit/",
    response_model=PostResponse,
)
def submit_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    Check a post against the moderation rules.

    If the content violates a rule:
        status = flagged

    If the content passes all rules:
        status = approved
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    if post.status == "published":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Published posts cannot be submitted again.",
        )

    if post.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Post has already been approved.",
        )

    reasons = moderate_content(post.content)

    if reasons:
        post.status = "flagged"
        post.flagged_reasons = json.dumps(reasons)
    else:
        post.status = "approved"
        post.flagged_reasons = None

    try:
        db.commit()
        db.refresh(post)

        return serialize_post(post)

    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------------
# 3. LIST POSTS WITH OPTIONAL STATUS FILTER
# ---------------------------------------------------------

@app.get(
    "/posts/",
    response_model=list[PostResponse],
)
def list_posts(
    post_status: PostStatus | None = Query(
        default=None,
        alias="status",
        description=(
            "Filter posts by status: "
            "draft, flagged, approved, or published."
        ),
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve all posts or filter by status.
    """

    query = db.query(Post)

    if post_status is not None:
        query = query.filter(
            Post.status == post_status
        )

    posts = (
        query
        .order_by(Post.id.desc())
        .all()
    )

    return [
        serialize_post(post)
        for post in posts
    ]


# ---------------------------------------------------------
# 4. PUBLISH AN APPROVED POST
# ---------------------------------------------------------

@app.patch(
    "/posts/{post_id}/publish/",
    response_model=PostResponse,
)
def publish_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    Publish a post only when its status is approved.
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    if post.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only approved posts can be published. "
                f"Current status: {post.status}."
            ),
        )

    post.status = "published"

    try:
        db.commit()
        db.refresh(post)

        return serialize_post(post)

    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------------
# 5. RETRIEVE A SPECIFIC POST
# ---------------------------------------------------------

@app.get(
    "/posts/{post_id}",
    response_model=PostResponse,
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single post using its ID.
    """

    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return serialize_post(post)