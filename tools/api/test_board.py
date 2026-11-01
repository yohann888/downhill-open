import math

import pytest

from board import consume_slot, insert_top, quantize_ghost, validate_run


class MemoryStore(dict):
    def put(self, key, value, skip_if_exists=False):
        if skip_if_exists and key in self:
            return False
        self[key] = value
        return True


def valid_run(**overrides):
    run = {
        "name": "AAA",
        "time": 30,
        "penalties": 2,
        "topSpeed": 42.5,
        "crashes": 1,
        "otterHits": 1,
        "maxAir": 1.4,
        "ghost": {
            "dt": 0.1,
            "frames": [[0, 1.234, 2, 0, 0] for _ in range(280)],
        },
    }
    run.update(overrides)
    return run


def test_validate_run_normalizes_initials_and_quantizes_ghost():
    run = validate_run(valid_run(name=" ab9 "))

    assert run["name"] == "AB9"
    assert run["ghost"]["frames"][0] == [0.0, 1.23, 2.0, 0.0, 0.0]
    assert run["bonus"] == 0


def test_validate_run_includes_bonus_in_simulated_ghost_duration():
    run = validate_run(valid_run(
        bonus=2,
        ghost={"dt": 0.1, "frames": [[0, 0, 0, 0, 0] for _ in range(300)]},
    ))

    assert run["bonus"] == 2


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"name": "   "}, "name"),
        ({"name": "name-too-long1"}, "name"),
        ({"name": "ABCD"}, "name"),
        ({"name": "bad/name"}, "name"),
        ({"time": 20}, "time"),
        ({"time": 600}, "time"),
        ({"topSpeed": math.inf}, "topSpeed"),
        ({"maxAir": math.nan}, "maxAir"),
        ({"bonus": -0.1}, "bonus"),
        ({"bonus": 30}, "bonus"),
        ({"extra": math.nan}, "extra"),
        ({"crashes": 0.5}, "whole numbers"),
        (
            {"ghost": {"dt": 0.1, "frames": [[0, 0, 0, 0, 0] for _ in range(100)]}},
            "duration",
        ),
    ],
)
def test_validate_run_rejects_invalid_values(overrides, message):
    with pytest.raises(ValueError, match=message):
        validate_run(valid_run(**overrides))


def test_quantize_ghost_rejects_oversized_and_nonfinite_frames():
    with pytest.raises(ValueError, match="at most"):
        quantize_ghost({"dt": 0.1, "frames": [[0, 0, 0, 0, 0]] * 6001})
    with pytest.raises(ValueError, match="finite"):
        quantize_ghost({"dt": 0.1, "frames": [[0, 0, float("inf"), 0, 0]]})


def test_insert_top_sorts_by_time_caps_at_fifty_and_returns_rank():
    existing = [
        {"name": f"Rider{i}", "time": 25 + i, "penalties": 0, "topSpeed": 20, "ts": i}
        for i in range(50)
    ]
    top, rank = insert_top(existing, {"name": "Fast", "time": 21, "penalties": 0, "topSpeed": 40}, timestamp=100)

    assert len(top) == 50
    assert top[0]["name"] == "Fast"
    assert rank == 1

    top, rank = insert_top(top, {"name": "Slow", "time": 1000, "penalties": 0, "topSpeed": 10}, timestamp=101)
    assert rank is None
    assert all(item["name"] != "Slow" for item in top)


def test_insert_top_returns_existing_rank_for_duplicate_name_and_time():
    existing = [
        {"name": "Rider", "time": 29.5, "penalties": 0, "topSpeed": 40, "ts": 1},
        {"name": "Rider", "time": 30.0, "penalties": 2, "topSpeed": 42, "ts": 2},
    ]

    top, rank = insert_top(
        existing,
        {"name": "Rider", "time": 30.0 + 0.5e-6, "penalties": 3, "topSpeed": 50},
        timestamp=100,
    )

    assert top == existing
    assert rank == 2


def test_insert_top_keeps_same_name_with_different_time():
    existing = [
        {"name": "Rider", "time": 30.0, "penalties": 0, "topSpeed": 40, "ts": 1},
    ]

    top, rank = insert_top(
        existing,
        {"name": "Rider", "time": 31.0, "penalties": 0, "topSpeed": 42},
        timestamp=2,
    )

    assert len(top) == 2
    assert rank == 2
    assert top[1]["time"] == 31.0


def test_consume_slot_allows_exactly_the_limit():
    store = MemoryStore()
    for _ in range(3):
        assert consume_slot(store, "test", 3)
    assert not consume_slot(store, "test", 3)


@pytest.mark.parametrize("hint", ["x", -1, 8, True])
def test_consume_slot_ignores_garbage_hints_without_exceeding_limit(hint):
    store = MemoryStore({"test:n": hint})

    for _ in range(3):
        assert consume_slot(store, "test", 3)
    assert not consume_slot(store, "test", 3)


def test_consume_slot_handles_two_callers_with_the_same_hint():
    class RacingStore(dict):
        hint_reads = 0

        def get(self, key, default=None):
            if key == "test:n" and self.hint_reads < 2:
                self.hint_reads += 1
                return 0
            return super().get(key, default)

        def put(self, key, value, skip_if_exists=False):
            if skip_if_exists and key in self:
                return False
            self[key] = value
            return True

    store = RacingStore()

    assert consume_slot(store, "test", 2)
    assert consume_slot(store, "test", 2)
    assert store["test:0"] == 1
    assert store["test:1"] == 1
    assert not consume_slot(store, "test", 2)
