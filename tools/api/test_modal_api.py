import asyncio
import json
from pathlib import Path

from starlette.requests import Request

import modal_api
from board import _course_center_x


class MemoryBoard(dict):
    def put(self, key, value):
        self[key] = value


def _path(count, *, start_z=-6, finish_z=-901):
    start_x = _course_center_x(start_z)
    finish_x = _course_center_x(finish_z)
    return [
        [
            start_x + (finish_x - start_x) * index / (count - 1),
            0,
            start_z + (finish_z - start_z) * index / (count - 1),
            0,
            0,
        ]
        for index in range(count)
    ]


def _entry(index):
    return {
        "name": f"Rider{index}",
        "time": 40 + index,
        "penalties": 0,
        "bonus": 0,
        "topSpeed": 30,
        "ts": index,
    }


def _request(body):
    payload = json.dumps(body).encode()

    async def receive():
        return {"type": "http.request", "body": payload, "more_body": False}

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/run",
            "headers": [(b"x-forwarded-for", b"192.0.2.1")],
            "client": ("127.0.0.1", 1234),
        },
        receive,
    )


def test_get_leaderboard_returns_up_to_top_size(monkeypatch):
    monkeypatch.setattr(modal_api, "board", MemoryBoard())
    modal_api.board[modal_api.TOP_KEY] = [_entry(index) for index in range(55)]

    result = asyncio.run(modal_api.get_leaderboard())

    assert len(result["top"]) == 50
    assert result["top"][0]["name"] == "RID"
    assert result["top"][-1]["name"] == "RID"


def test_post_run_returns_top_size(monkeypatch):
    board = MemoryBoard()
    board[modal_api.TOP_KEY] = [_entry(index) for index in range(50)]
    monkeypatch.setattr(modal_api, "board", board)
    run = {
        "name": "new",
        "time": 30,
        "penalties": 0,
        "bonus": 0,
        "topSpeed": 42,
        "crashes": 0,
        "otterHits": 0,
        "maxAir": 0,
        "ghost": {"dt": 0.1, "frames": _path(300)},
    }

    result = asyncio.run(modal_api.post_run(_request(run)))

    assert result["rank"] == 1
    assert len(result["top"]) == 50
    assert result["top"][0]["name"] == "NEW"


def test_get_leaderboard_clips_legacy_names_without_mutating_storage(monkeypatch):
    board = MemoryBoard()
    board[modal_api.TOP_KEY] = [{
        **_entry(0),
        "name": "Long Legacy Name",
    }]
    board[modal_api.BEST_GHOST_KEY] = {
        "name": "Long Ghost Name",
        "frames": [[0, 1, 2, 0, 0]],
        "dt": 0.1,
    }
    monkeypatch.setattr(modal_api, "board", board)

    result = asyncio.run(modal_api.get_leaderboard())

    assert result["top"][0]["name"] == "LON"
    assert result["ghost"]["name"] == "LON"
    assert board[modal_api.TOP_KEY][0]["name"] == "Long Legacy Name"
    assert board[modal_api.BEST_GHOST_KEY]["name"] == "Long Ghost Name"


def test_get_leaderboard_serves_legacy_records_without_mutating_storage(monkeypatch):
    board = MemoryBoard()
    legacy_entries = [
        {
            "name": "legacy lower-case long name",
            "time": 40,
            "penalties": 1,
            "topSpeed": 30,
            "ts": 1,
        }
    ]
    legacy_ghost = {
        "name": "legacy",
        "dt": 20.0,
        "frames": [[0, 0, 0, 0, 0]],
    }
    board[modal_api.TOP_KEY] = legacy_entries
    board[modal_api.BEST_GHOST_KEY] = legacy_ghost
    monkeypatch.setattr(modal_api, "board", board)

    result = asyncio.run(modal_api.get_leaderboard())

    assert result["top"][0]["name"] == "LEG"
    assert result["ghost"]["name"] == "LEG"
    assert result["ghost"]["dt"] == 20.0
    assert result["ghost"]["frames"] == [[0, 0, 0, 0, 0]]
    assert board[modal_api.TOP_KEY] == legacy_entries
    assert board[modal_api.BEST_GHOST_KEY] == legacy_ghost


def test_post_run_accepts_real_fixture_with_legacy_entries(monkeypatch):
    fixture_path = Path(__file__).parent / "fixtures" / "real_client_run.json"
    with fixture_path.open() as fixture_file:
        run = json.load(fixture_file)
    board = MemoryBoard()
    board[modal_api.TOP_KEY] = [{
        "name": "legacy",
        "time": 60,
        "penalties": 0,
        "topSpeed": 30,
        "ts": 1,
    }]
    monkeypatch.setattr(modal_api, "board", board)

    result = asyncio.run(modal_api.post_run(_request(run)))

    assert result["rank"] == 1
    assert result["top"][0]["name"] == "YO"
    assert board[modal_api.BEST_GHOST_KEY] == {
        "name": "YO",
        "time": run["time"],
        "dt": run["ghost"]["dt"],
        "frames": run["ghost"]["frames"],
    }


def test_commentary_audio_is_optional_without_voice_id(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setattr(modal_api, "ELEVENLABS_VOICE_ID", None)
    monkeypatch.setattr(modal_api, "board", MemoryBoard())

    result = asyncio.run(modal_api._commentary_audio("Nice run"))

    assert result is None
