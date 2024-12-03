from fastapi.testclient import TestClient

from api_movies.main import app
import pytest


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Movie API is working!"}


def test_create_movie(client):
    movie_data = {
        "name": "TEST_CREATE_MOVIE",
        "release_year": 2024,
        "description": "TESTING",
        "genre": "scifi",
    }
    response = client.post("/movie", json=movie_data)
    assert response.status_code == 201
    assert response.json()["name"] == "TEST_CREATE_MOVIE"

    movie_data = {
        "name": "BAD_MOVIE",
        "release_year": 2024,
        "description": "A mind-bending thriller",
        "genre": "BAD_GENRE",
    }
    # testing genre validation
    response = client.post("/movie", json=movie_data)
    assert response.status_code == 400


def test_read_all_movies(client):
    response = client.get("/movie")
    for movie in response.json():
        assert isinstance(movie["id"], int)
        assert isinstance(movie["name"], str)
        assert isinstance(movie["description"], str)
        assert isinstance(movie["genre"], str)
        assert isinstance(movie["release_year"], int)


def test_read_movie(client):
    movie_data = {
        "name": "TEST_READ_MOVIE",
        "description": "TESTING",
        "genre": "scifi",
        "release_year": 2010,
    }
    create_response = client.post("/movie", json=movie_data)
    movie_id = int(create_response.json()["id"])
    print(movie_id)

    response = client.get(f"/movie/{movie_id}")
    print(response.status_code, response.json()["name"])

    assert response.status_code == 200
    assert response.json()["name"] == "TEST_READ_MOVIE"


def test_delete_movie(client):
    movie_data = {
        "name": "TEST_DELETE_MOVIE",
        "description": "TESTING",
        "genre": "scifi",
        "release_year": 2010,
    }
    create_response = client.post("/movie", json=movie_data)
    movie_id = create_response.json()["id"]
    response = client.delete(f"/movie/{movie_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "TEST_DELETE_MOVIE"

    response = client.delete(f"/movie/{0}")
    assert response.status_code == 404
