from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.track import TrackDetail, TrackListResponse, TrackRead
from app.services.track_service import InvalidAudioFileError, TrackService

router = APIRouter(prefix="/api/v1/tracks", tags=["tracks"])


@router.get("", response_model=TrackListResponse)
def list_tracks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    q: str | None = Query(default=None, max_length=255),
    db: Session = Depends(get_db),
) -> TrackListResponse:
    service = TrackService(db)
    items, total = service.list_tracks(page=page, page_size=page_size, q=q)
    return TrackListResponse(items=[TrackRead.model_validate(item) for item in items], total=total, page=page, page_size=page_size)


@router.get("/{track_id}", response_model=TrackDetail)
def get_track(track_id: int, db: Session = Depends(get_db)) -> TrackDetail:
    track = TrackService(db).get_track(track_id)
    if track is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return TrackDetail.model_validate(track)


@router.get("/{track_id}/download")
def download_track(track_id: int, db: Session = Depends(get_db)) -> FileResponse:
    path = TrackService(db).get_download_path(track_id)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file is unavailable")
    return FileResponse(path=path, filename=Path(path).name, media_type="application/octet-stream")


@router.post("", response_model=TrackRead, status_code=status.HTTP_201_CREATED)
def upload_track(
    file: UploadFile = File(...),
    title: str = Form(..., min_length=1, max_length=255),
    artist: str | None = Form(default=None, max_length=255),
    album: str | None = Form(default=None, max_length=255),
    genre: str | None = Form(default=None, max_length=255),
    db: Session = Depends(get_db),
) -> TrackRead:
    try:
        track = TrackService(db).create_uploaded_track(file, title, artist, album, genre)
    except InvalidAudioFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TrackRead.model_validate(track)
