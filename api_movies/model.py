from typing import Optional
from fastapi import HTTPException
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel
from enum import Enum


class Genre(str, Enum):
    ACTION = "action"
    COMEDY = "comedy"
    ROMANCE = "romance"
    SCIFI = "scifi"
    HORROR = "horror"

    @classmethod
    def from_string(cls, genre_str: str) -> Optional["Genre"]:
        try:
            return cls(genre_str.lower())
        except ValueError:
            return None


class Movie(SQLModel, table=True):
    model_config = ConfigDict(use_enum_values=True)
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    release_year: Optional[int] = Field(default=None, index=True)
    description: Optional[str] = Field(default=None)
    genre: Genre = Field(index=True)
