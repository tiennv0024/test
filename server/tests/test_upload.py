from pathlib import Path


def test_upload_valid_audio(client):
    response = client.post(
        "/api/v1/tracks",
        data={
            "title": "Uploaded Song",
            "artist": "Uploader",
            "album": "Uploads",
            "genre": "Test",
        },
        files={"file": ("song.mp3", b"not really mp3 but accepted by extension", "audio/mpeg")},
    )

    body = response.json()

    assert response.status_code == 201
    assert body["title"] == "Uploaded Song"
    assert body["file_size"] == len(b"not really mp3 but accepted by extension")


def test_upload_invalid_extension(client):
    response = client.post(
        "/api/v1/tracks",
        data={"title": "Bad Upload"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400


def test_uploaded_file_can_be_downloaded(client):
    upload = client.post(
        "/api/v1/tracks",
        data={"title": "Round Trip"},
        files={"file": ("roundtrip.mp3", b"round trip bytes", "audio/mpeg")},
    )
    track_id = upload.json()["id"]

    download = client.get(f"/api/v1/tracks/{track_id}/download")

    assert download.status_code == 200
    assert download.content == b"round trip bytes"


def test_upload_does_not_keep_part_files(client, monkeypatch):
    response = client.post(
        "/api/v1/tracks",
        data={"title": "Tiny"},
        files={"file": ("tiny.mp3", b"x", "audio/mpeg")},
    )
    assert response.status_code == 201

    storage = Path(__import__("os").environ["AUDIO_STORAGE_PATH"])
    assert not list(storage.glob("*.part"))
