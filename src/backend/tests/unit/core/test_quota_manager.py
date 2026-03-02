"""Unit tests for shared quota manager behavior."""

import pytest

from app.core.quota_manager import QuotaExceededError, QuotaManager


@pytest.mark.asyncio
async def test_sliding_window_rpm_tpm_accounting(monkeypatch):
    now = {"value": 0.0}

    def fake_time():
        return now["value"]

    monkeypatch.setattr("app.core.quota_manager.time.time", fake_time)

    manager = QuotaManager(
        llm_rpm_limit=2,
        llm_tpm_limit=10,
        llm_rpd_limit=10,
        embedding_rpm_limit=10,
        embedding_tpm_limit=100,
        embedding_rpd_limit=100,
        window_seconds=60,
        enforcement_enabled=True,
    )

    first = await manager.reserve("text_generation", 5, wait_for_capacity=False)
    assert first.allowed is True

    now["value"] = 1.0
    second = await manager.reserve("text_generation", 5, wait_for_capacity=False)
    assert second.allowed is True

    now["value"] = 2.0
    blocked = await manager.reserve("text_generation", 5, wait_for_capacity=False)
    assert blocked.allowed is False
    assert blocked.reason == "throttled"

    # Window expires -> capacity is available again.
    now["value"] = 61.0
    after_window = await manager.reserve("text_generation", 5, wait_for_capacity=False)
    assert after_window.allowed is True


@pytest.mark.asyncio
async def test_rpd_fail_fast_and_rollover(monkeypatch):
    now = {"value": 0.0}

    def fake_time():
        return now["value"]

    monkeypatch.setattr("app.core.quota_manager.time.time", fake_time)

    manager = QuotaManager(
        llm_rpm_limit=100,
        llm_tpm_limit=1000,
        llm_rpd_limit=2,
        embedding_rpm_limit=100,
        embedding_tpm_limit=1000,
        embedding_rpd_limit=100,
        window_seconds=60,
        enforcement_enabled=True,
    )

    await manager.reserve("text_generation", 10)
    now["value"] = 1.0
    await manager.reserve("text_generation", 10)
    now["value"] = 2.0

    with pytest.raises(QuotaExceededError):
        await manager.reserve("text_generation", 10)

    # 24h rollover clears RPD usage.
    now["value"] = 86401.0
    decision = await manager.reserve("text_generation", 10)
    assert decision.allowed is True


@pytest.mark.asyncio
async def test_wait_for_capacity_tracks_wait_time(monkeypatch):
    now = {"value": 0.0}
    sleep_calls: list[float] = []

    def fake_time():
        return now["value"]

    async def fake_sleep(seconds: float):
        sleep_calls.append(seconds)
        now["value"] += seconds

    monkeypatch.setattr("app.core.quota_manager.time.time", fake_time)
    monkeypatch.setattr("app.core.quota_manager.asyncio.sleep", fake_sleep)

    manager = QuotaManager(
        llm_rpm_limit=1,
        llm_tpm_limit=1000,
        llm_rpd_limit=100,
        embedding_rpm_limit=100,
        embedding_tpm_limit=1000,
        embedding_rpd_limit=100,
        window_seconds=10,
        enforcement_enabled=True,
    )

    await manager.reserve("text_generation", 10)
    second = await manager.reserve("text_generation", 10)

    assert second.allowed is True
    assert second.wait_seconds >= 10.0
    assert sleep_calls

