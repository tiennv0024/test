from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TrackBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    artist: str | None = Field(default=None, max_length=255)
    album: str | None = Field(default=None, max_length=255)
    genre: str | None = Field(default=None, max_length=255)


class TrackCreate(TrackBase):
    fma_id: int | None = None
    tags: str | None = None
    file_path: str
    duration_ms: int | None = None
    file_size: int | None = None


class TrackRead(TrackBase):
    id: int
    fma_id: int | None = None
    duration_ms: int | None = None
    file_size: int | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackDetail(TrackRead):
    tags: str | None = None
    created_at: datetime
    updated_at: datetime


class TrackListResponse(BaseModel):
    items: list[TrackRead]
    total: int
    page: int
    page_size: int
