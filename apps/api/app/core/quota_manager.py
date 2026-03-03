"""Shared quota manager for Gemini free-tier-safe request throttling."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Literal, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

QuotaBucketName = Literal["text_generation", "embedding"]
WARNING_THRESHOLDS = (0.70, 0.85, 0.95)
DAY_SECONDS = 86400


@dataclass(frozen=True)
class QuotaSnapshot:
    """Current usage and limits for one bucket."""

    bucket: QuotaBucketName
    rpm_limit: int
    tpm_limit: int
    rpd_limit: int
    window_seconds: int
    rpm_used: int
    tpm_used: int
    rpd_used: int

    @property
    def rpm_utilization(self) -> float:
        if self.rpm_limit <= 0:
            return 0.0
        return min(1.0, self.rpm_used / self.rpm_limit)

    @property
    def tpm_utilization(self) -> float:
        if self.tpm_limit <= 0:
            return 0.0
        return min(1.0, self.tpm_used / self.tpm_limit)

    @property
    def rpd_utilization(self) -> float:
        if self.rpd_limit <= 0:
            return 0.0
        return min(1.0, self.rpd_used / self.rpd_limit)

    def to_dict(self) -> Dict[str, float | int | str]:
        return {
            "bucket": self.bucket,
            "rpm_limit": self.rpm_limit,
            "tpm_limit": self.tpm_limit,
            "rpd_limit": self.rpd_limit,
            "window_seconds": self.window_seconds,
            "rpm_used": self.rpm_used,
            "tpm_used": self.tpm_used,
            "rpd_used": self.rpd_used,
            "rpm_utilization": round(self.rpm_utilization, 4),
            "tpm_utilization": round(self.tpm_utilization, 4),
            "rpd_utilization": round(self.rpd_utilization, 4),
        }


@dataclass(frozen=True)
class QuotaDecision:
    """Outcome of a quota reservation attempt."""

    bucket: QuotaBucketName
    allowed: bool
    wait_seconds: float
    reason: str
    snapshot: QuotaSnapshot

    def to_dict(self) -> Dict[str, object]:
        return {
            "bucket": self.bucket,
            "allowed": self.allowed,
            "wait_seconds": round(self.wait_seconds, 6),
            "reason": self.reason,
            "snapshot": self.snapshot.to_dict(),
        }


class QuotaExceededError(RuntimeError):
    """Raised when daily request quota is exhausted."""

    def __init__(self, bucket: QuotaBucketName, snapshot: QuotaSnapshot):
        self.bucket = bucket
        self.snapshot = snapshot
        super().__init__(
            f"{bucket} daily quota exhausted: {snapshot.rpd_used}/{snapshot.rpd_limit}"
        )


class _BucketLimiter:
    """Async-safe rolling-window limiter for one quota bucket."""

    def __init__(
        self,
        *,
        bucket: QuotaBucketName,
        rpm_limit: int,
        tpm_limit: int,
        rpd_limit: int,
        window_seconds: int,
    ):
        self.bucket = bucket
        self.rpm_limit = max(1, int(rpm_limit))
        self.tpm_limit = max(1, int(tpm_limit))
        self.rpd_limit = max(1, int(rpd_limit))
        self.window_seconds = max(1, int(window_seconds))
        self._lock = asyncio.Lock()
        self._events: Deque[Tuple[float, int]] = deque()
        self._daily_events: Deque[float] = deque()
        self._warned_levels: set[float] = set()

    def _prune(self, now: float) -> None:
        while self._events and now - self._events[0][0] >= self.window_seconds:
            self._events.popleft()
        while self._daily_events and now - self._daily_events[0] >= DAY_SECONDS:
            self._daily_events.popleft()

    def _snapshot(self, now: float) -> QuotaSnapshot:
        self._prune(now)
        return QuotaSnapshot(
            bucket=self.bucket,
            rpm_limit=self.rpm_limit,
            tpm_limit=self.tpm_limit,
            rpd_limit=self.rpd_limit,
            window_seconds=self.window_seconds,
            rpm_used=len(self._events),
            tpm_used=sum(tokens for _, tokens in self._events),
            rpd_used=len(self._daily_events),
        )

    def _time_until_tokens_available(self, now: float, required_tokens: int) -> float:
        if required_tokens <= 0:
            return 0.0

        rolling_tokens = 0
        for timestamp, tokens in self._events:
            rolling_tokens += tokens
            if rolling_tokens >= required_tokens:
                return max(0.0, (timestamp + self.window_seconds) - now)
        return 0.0

    def _log_rpd_warnings(self, snapshot: QuotaSnapshot) -> None:
        ratio = snapshot.rpd_utilization
        if snapshot.rpd_used == 0:
            self._warned_levels.clear()
            return

        for threshold in WARNING_THRESHOLDS:
            if ratio >= threshold and threshold not in self._warned_levels:
                self._warned_levels.add(threshold)
                logger.warning(
                    "Quota warning bucket=%s level=%.0f%% used=%s/%s",
                    self.bucket,
                    threshold * 100,
                    snapshot.rpd_used,
                    snapshot.rpd_limit,
                )

    async def reserve(
        self,
        request_tokens: int,
        *,
        wait_for_capacity: bool,
    ) -> QuotaDecision:
        request_tokens = max(1, int(request_tokens))
        total_wait = 0.0

        while True:
            async with self._lock:
                now = time.time()
                snapshot = self._snapshot(now)

                if snapshot.rpd_used >= self.rpd_limit:
                    raise QuotaExceededError(self.bucket, snapshot)

                rpm_blocked = snapshot.rpm_used >= self.rpm_limit
                tpm_blocked = (snapshot.tpm_used + request_tokens) > self.tpm_limit

                if not rpm_blocked and not tpm_blocked:
                    self._events.append((now, request_tokens))
                    self._daily_events.append(now)
                    updated_snapshot = self._snapshot(time.time())
                    self._log_rpd_warnings(updated_snapshot)
                    return QuotaDecision(
                        bucket=self.bucket,
                        allowed=True,
                        wait_seconds=total_wait,
                        reason="allowed",
                        snapshot=updated_snapshot,
                    )

                wait_for_rpm = 0.0
                if rpm_blocked and self._events:
                    wait_for_rpm = max(
                        0.0, (self._events[0][0] + self.window_seconds) - now
                    )

                required_tokens = (snapshot.tpm_used + request_tokens) - self.tpm_limit
                wait_for_tpm = self._time_until_tokens_available(now, required_tokens)
                wait_seconds = max(wait_for_rpm, wait_for_tpm, 0.01)

                if not wait_for_capacity:
                    return QuotaDecision(
                        bucket=self.bucket,
                        allowed=False,
                        wait_seconds=wait_seconds,
                        reason="throttled",
                        snapshot=snapshot,
                    )

            await asyncio.sleep(wait_seconds)
            total_wait += wait_seconds


class QuotaManager:
    """Centralized process-level quota manager."""

    def __init__(
        self,
        *,
        llm_rpm_limit: int,
        llm_tpm_limit: int,
        llm_rpd_limit: int,
        embedding_rpm_limit: int,
        embedding_tpm_limit: int,
        embedding_rpd_limit: int,
        window_seconds: int,
        enforcement_enabled: bool,
    ):
        self.enforcement_enabled = bool(enforcement_enabled)
        self._limiters: Dict[QuotaBucketName, _BucketLimiter] = {
            "text_generation": _BucketLimiter(
                bucket="text_generation",
                rpm_limit=llm_rpm_limit,
                tpm_limit=llm_tpm_limit,
                rpd_limit=llm_rpd_limit,
                window_seconds=window_seconds,
            ),
            "embedding": _BucketLimiter(
                bucket="embedding",
                rpm_limit=embedding_rpm_limit,
                tpm_limit=embedding_tpm_limit,
                rpd_limit=embedding_rpd_limit,
                window_seconds=window_seconds,
            ),
        }

    async def reserve(
        self,
        bucket: QuotaBucketName,
        request_tokens: int,
        *,
        wait_for_capacity: bool = True,
    ) -> QuotaDecision:
        limiter = self._limiters[bucket]
        if not self.enforcement_enabled:
            snapshot = limiter._snapshot(time.time())
            return QuotaDecision(
                bucket=bucket,
                allowed=True,
                wait_seconds=0.0,
                reason="enforcement_disabled",
                snapshot=snapshot,
            )

        return await limiter.reserve(
            request_tokens=request_tokens,
            wait_for_capacity=wait_for_capacity,
        )

    def snapshot(self, bucket: QuotaBucketName) -> QuotaSnapshot:
        return self._limiters[bucket]._snapshot(time.time())

    def snapshot_all(self) -> Dict[str, Dict[str, float | int | str]]:
        return {
            bucket: limiter._snapshot(time.time()).to_dict()
            for bucket, limiter in self._limiters.items()
        }


_quota_manager: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Return process singleton quota manager."""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager(
            llm_rpm_limit=settings.llm_rpm_limit,
            llm_tpm_limit=settings.llm_tpm_limit,
            llm_rpd_limit=settings.llm_rpd_limit,
            embedding_rpm_limit=settings.embedding_rpm_limit,
            embedding_tpm_limit=settings.embedding_tpm_limit,
            embedding_rpd_limit=settings.embedding_rpd_limit,
            window_seconds=settings.rate_window_seconds,
            enforcement_enabled=settings.quota_enforcement_enabled,
        )
        logger.info(
            "Quota manager initialized profile=%s enforcement=%s",
            settings.quota_profile_name,
            settings.quota_enforcement_enabled,
        )
    return _quota_manager


def reset_quota_manager() -> None:
    """Reset singleton (test helper)."""
    global _quota_manager
    _quota_manager = None

