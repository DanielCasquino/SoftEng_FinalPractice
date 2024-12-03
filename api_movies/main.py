from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Query, status
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
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    """
    Health Check Endpoint

    Returns a simple message to verify the API is working.

    Returns:
        dict: A message indicating the API status
    """
    return JSONResponse(status_code=200, content={"message": "Movie API is working!"})


# Creates a movie
@app.post("/movie", status_code=status.HTTP_201_CREATED)
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
    logger.debug(movie)
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
    logger.debug(movie)
    return JSONResponse(status_code=201, content=movie.model_dump())


# Retrieves all movies, with a max of 100
@app.get("/movie", status_code=status.HTTP_200_OK)
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
    logger.debug(movies)
    return JSONResponse(
        status_code=200, content=[movie.model_dump() for movie in movies]
    )


# Retrieves a movie with a given id
@app.get("/movie/{movie_id}", status_code=status.HTTP_200_OK)
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
    if not movie:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})
    return JSONResponse(status_code=200, content=movie.model_dump())


@app.delete("/movie/{movie_id}", status_code=status.HTTP_200_OK)
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
    if not movie:
        logger.debug("Movie not found")
        return JSONResponse(status_code=404, content={"message": "Movie not found"})
    logger.debug("Deleting movie")
    await session.delete(movie)
    await session.commit()
    return JSONResponse(status_code=200, content=movie.model_dump())
