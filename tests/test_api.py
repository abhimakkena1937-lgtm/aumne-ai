import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app


# ---------------------------------------------------------
# TEST DATABASE CONFIGURATION
# ---------------------------------------------------------

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ---------------------------------------------------------
# DATABASE DEPENDENCY OVERRIDE
# ---------------------------------------------------------

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------
# TEST CLIENT AND FIXTURES
# ---------------------------------------------------------

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------
# TEST 1: ROOT ENDPOINT
# ---------------------------------------------------------

def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "Aumne AI"


# ---------------------------------------------------------
# TEST 2: CREATE A POST
# ---------------------------------------------------------

def test_create_post(client):
    payload = {
        "title": "Learning Artificial Intelligence",
        "content": (
            "Artificial intelligence helps computers perform "
            "tasks that normally require human intelligence."
        ),
    }

    response = client.post("/posts/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["status"] == "draft"
    assert data["id"] is not None


# ---------------------------------------------------------
# TEST 3: REJECT AN EMPTY TITLE
# ---------------------------------------------------------

def test_create_post_with_empty_title(client):
    payload = {
        "title": "   ",
        "content": (
            "This is a sample article with enough content "
            "to demonstrate the API validation process."
        ),
    }

    response = client.post("/posts/", json=payload)

    assert response.status_code == 422


# ---------------------------------------------------------
# TEST 4: FLAG SHORT CONTENT
# ---------------------------------------------------------

def test_submit_short_post(client):
    payload = {
        "title": "Short Article",
        "content": "This is too short.",
    }

    create_response = client.post("/posts/", json=payload)

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.post(
        f"/posts/{post_id}/submit/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "flagged"
    assert any(
        "at least 50 characters" in reason
        for reason in data["flagged_reasons"]
    )


# ---------------------------------------------------------
# TEST 5: APPROVE ACCEPTABLE CONTENT
# ---------------------------------------------------------

def test_submit_acceptable_post(client):
    payload = {
        "title": "Learning Python",
        "content": (
            "Python is a versatile programming language used "
            "in web development, automation, data analysis, "
            "and machine learning. Regular practice helps "
            "developers improve their programming skills."
        ),
    }

    create_response = client.post("/posts/", json=payload)

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.post(
        f"/posts/{post_id}/submit/"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


# ---------------------------------------------------------
# TEST 6: LIST POSTS
# ---------------------------------------------------------

def test_list_posts(client):
    response = client.get("/posts/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------
# TEST 7: FILTER POSTS BY STATUS
# ---------------------------------------------------------

def test_filter_posts_by_status(client):
    payload = {
        "title": "Filtering Test",
        "content": (
            "This is a sample post used to test filtering "
            "posts according to their current status."
        ),
    }

    client.post("/posts/", json=payload)

    response = client.get(
        "/posts/",
        params={"status": "draft"},
    )

    assert response.status_code == 200

    for post in response.json():
        assert post["status"] == "draft"


# ---------------------------------------------------------
# TEST 8: GET A SPECIFIC POST
# ---------------------------------------------------------

def test_get_post(client):
    payload = {
        "title": "Specific Post Test",
        "content": (
            "This sample post demonstrates retrieving a "
            "single record using its unique database ID."
        ),
    }

    create_response = client.post("/posts/", json=payload)

    post_id = create_response.json()["id"]

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id


# ---------------------------------------------------------
# TEST 9: RETURN 404 FOR A MISSING POST
# ---------------------------------------------------------

def test_get_missing_post(client):
    response = client.get("/posts/999999")

    assert response.status_code == 404


# ---------------------------------------------------------
# TEST 10: PREVENT PUBLISHING A DRAFT
# ---------------------------------------------------------

def test_cannot_publish_draft(client):
    payload = {
        "title": "Draft Publication Test",
        "content": (
            "This post remains in draft status until it "
            "passes the content moderation requirements."
        ),
    }

    create_response = client.post("/posts/", json=payload)

    post_id = create_response.json()["id"]

    response = client.patch(
        f"/posts/{post_id}/publish/"
    )

    assert response.status_code == 409


# ---------------------------------------------------------
# TEST 11: PUBLISH AN APPROVED POST
# ---------------------------------------------------------

def test_publish_approved_post(client):
    payload = {
        "title": "Publishing Test",
        "content": (
            "Responsible software development involves "
            "testing, documentation, code review, and "
            "continuous improvement throughout a project."
        ),
    }

    create_response = client.post("/posts/", json=payload)

    post_id = create_response.json()["id"]

    submit_response = client.post(
        f"/posts/{post_id}/submit/"
    )

    assert submit_response.status_code == 200

    assert submit_response.json()["status"] == "approved"

    publish_response = client.patch(
        f"/posts/{post_id}/publish/"
    )

    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"


# ---------------------------------------------------------
# TEST 12: RETURN 404 WHEN SUBMITTING A MISSING POST
# ---------------------------------------------------------

def test_submit_missing_post(client):
    response = client.post(
        "/posts/999999/submit/"
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------

@pytest.fixture(autouse=True)
def cleanup_overrides():
    yield
    app.dependency_overrides.pop(get_db, None)