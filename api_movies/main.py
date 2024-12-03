from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sqlmodel import select

from api_movies.model import Genre, Movie
from api_movies.database import create_db_and_tables, SessionDep

import logging


logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# Sanity check
@app.get("/", responses={200: {"description": "API is working"}})
async def read_root():
    """
    Health Check Endpoint

    Returns a simple message to verify the API is working.

    Returns:
        dict: A message indicating the API status
    """
    return JSONResponse(status_code=200, content={"message": "Movie API is working!"})


# Creates a movie
@app.post(
    "/movie",
    response_model=Movie,
    responses={
        201: {"description": "Movie created", "model": Movie},
        400: {"description": "Invalid genre"},
    },
)
async def create_movie(session: SessionDep, movie: Movie) -> Movie:
    """
    Movie Creation Endpoint

    Receives a movie object, creates it in the database, and returns it.

    Args:
        movie (object): The movie object to create

    Returns:
        movie (object): The created movie

    Raises:
        400: If the genre is invalid
    """
    if isinstance(movie.genre, str):
        movie.genre = Genre.from_string(movie.genre)
    if not movie.genre:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Invalid genre provided, valid genres are {[g.value for g in Genre]}"
            },
        )
    session.add(movie)
    await session.commit()
    await session.refresh(movie)
    return JSONResponse(status_code=201, content=movie.model_dump())


# Retrieves all movies, with a max of 100
@app.get(
    "/movie",
    response_model=list[Movie],
    responses={200: {"description": "Movies retrieved"}},
)
async def read_movies(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Movie]:
    """
    Movie ReadAll Endpoint

    Retrieves a maximum of 100 movies from the database.

    Returns:
        list[object]: A list of movies
    """
    movies = await session.execute(select(Movie).offset(offset).limit(limit))
    movies = movies.scalars().all()
    return JSONResponse(
        status_code=200, content=[movie.model_dump() for movie in movies]
    )


# Retrieves a movie with a given id
@app.get(
    "/movie/{movie_id}",
    response_model=Movie,
    responses={
        200: {"description": "Movie retrieved"},
        404: {"description": "Movie not found"},
    },
)
async def read_movie(session: SessionDep, movie_id: int) -> Movie:
    """
    Movie ReadOne Endpoint

    Retrieves a movie with a given id from the database.

    Args:
        movie_id (int): The id of the movie to retrieve

    Returns:
        movie (object): The movie with the desired id

    Raises:
        404: If the movie is not found
    """
    movie = await session.get(Movie, movie_id)
    if movie is None:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})
    return JSONResponse(status_code=200, content=movie.model_dump())


@app.delete(
    "/movie/{movie_id}",
    response_model=Movie,
    responses={
        200: {"description": "Movie deleted"},
        404: {"description": "Movie not found"},
    },
)
async def delete_movie(session: SessionDep, movie_id: int) -> Movie:
    """
    Movie Delete Endpoint

    Deletes a movie with a given id from the database.

    Args:
        movie_id (int): The id of the movie to delete

    Returns:
        movie (object): The deleted movie

    Raises:
        404: If the movie is not found
    """
    movie = await session.get(Movie, movie_id)
    if movie is None:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})
    await session.delete(movie)
    await session.commit()
    return JSONResponse(status_code=200, content=movie.model_dump())
