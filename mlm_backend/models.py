"""Domain models for the MLM commission system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Iterable, List, Optional


class CommissionStatus(str, Enum):
    """Represents the lifecycle state of a commission."""

    AVAILABLE = "available"
    PENDING = "pending"


@dataclass
class CommissionRecord:
    """Stores a commission generated from a downline purchase."""

    from_user_id: str
    level: int
    amount: int
    status: CommissionStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    released_at: Optional[datetime] = None

    def mark_available(self) -> None:
        """Update the commission to an available state."""

        if self.status == CommissionStatus.PENDING:
            self.status = CommissionStatus.AVAILABLE
            self.released_at = datetime.utcnow()


@dataclass
class Wallet:
    """Aggregates the commissions earned by a user."""

    commissions: List[CommissionRecord] = field(default_factory=list)

    def add_commission(self, record: CommissionRecord) -> None:
        self.commissions.append(record)

    def release_pending(self, level: int) -> List[CommissionRecord]:
        """Mark all pending commissions for a level as available."""

        released: List[CommissionRecord] = []
        for record in self.commissions:
            if record.level == level and record.status == CommissionStatus.PENDING:
                record.mark_available()
                released.append(record)
        return released

    @property
    def available_balance(self) -> int:
        return sum(record.amount for record in self.commissions if record.status == CommissionStatus.AVAILABLE)

    @property
    def pending_balance(self) -> int:
        return sum(record.amount for record in self.commissions if record.status == CommissionStatus.PENDING)

    def total_by_level(self, level: int, *, status: Optional[CommissionStatus] = None) -> int:
        records: Iterable[CommissionRecord] = (r for r in self.commissions if r.level == level)
        if status is not None:
            records = (r for r in records if r.status == status)
        return sum(r.amount for r in records)


@dataclass
class User:
    """Represents an affiliate in the MLM tree."""

    id: str
    name: str
    referrer_id: Optional[str]
    wallet: Wallet = field(default_factory=Wallet)
    direct_referrals: List[str] = field(default_factory=list)

    def add_direct_referral(self, user_id: str) -> None:
        self.direct_referrals.append(user_id)

    @property
    def direct_referral_count(self) -> int:
        return len(self.direct_referrals)


@dataclass
class DashboardLevelSummary:
    level: int
    requirement: int
    direct_referrals: int
    unlocked: bool
    pending_amount: int
    available_amount: int


@dataclass
class DashboardSummary:
    """Serializable structure for presenting a user's dashboard."""

    user_id: str
    name: str
    direct_referrals: int
    available_balance: int
    pending_balance: int
    levels: List[DashboardLevelSummary]

    @property
    def total_balance(self) -> int:
        return self.available_balance + self.pending_balance
