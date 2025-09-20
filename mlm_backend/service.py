"""Service layer containing the MLM business logic."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .config import COMMISSION_PLAN, LevelConfig
from .models import (
    CommissionRecord,
    CommissionStatus,
    DashboardLevelSummary,
    DashboardSummary,
    User,
)
from .repository import InMemoryUserRepository, UserNotFound


@dataclass
class MLMService:
    """Coordinates user registrations and commission distribution."""

    user_repo: InMemoryUserRepository
    commission_plan: Dict[int, LevelConfig] = field(default_factory=lambda: dict(COMMISSION_PLAN))

    def register_user(self, *, user_id: str, name: str, referrer_id: Optional[str] = None) -> User:
        """Register a new user and trigger commission distribution."""

        if referrer_id is not None:
            # Ensure the referrer exists before creating the user.
            self.user_repo.get(referrer_id)

        user = User(id=user_id, name=name, referrer_id=referrer_id)
        self.user_repo.add(user)

        if referrer_id is not None:
            self._attach_referral(referrer_id, user_id)

        self._distribute_commissions(user_id)
        return user

    def _attach_referral(self, referrer_id: str, new_user_id: str) -> None:
        referrer = self.user_repo.get(referrer_id)
        referrer.add_direct_referral(new_user_id)
        self._unlock_commissions(referrer)
        self.user_repo.update(referrer)

    def _distribute_commissions(self, new_user_id: str) -> None:
        current_referrer_id = self.user_repo.get(new_user_id).referrer_id
        level = 1
        while current_referrer_id is not None and level in self.commission_plan:
            referrer = self.user_repo.get(current_referrer_id)
            config = self.commission_plan[level]
            status = (
                CommissionStatus.AVAILABLE
                if referrer.direct_referral_count >= config.direct_requirement
                else CommissionStatus.PENDING
            )
            record = CommissionRecord(
                from_user_id=new_user_id,
                level=level,
                amount=config.payout,
                status=status,
            )
            referrer.wallet.add_commission(record)
            if status == CommissionStatus.AVAILABLE:
                # Persist the updated wallet state immediately.
                self.user_repo.update(referrer)
            else:
                # Pending commissions will be persisted after unlocking.
                self.user_repo.update(referrer)

            current_referrer_id = referrer.referrer_id
            level += 1

    def _unlock_commissions(self, user: User) -> None:
        direct_count = user.direct_referral_count
        for level, config in self.commission_plan.items():
            if direct_count >= config.direct_requirement:
                released = user.wallet.release_pending(level)
                if released:
                    # Persisting happens in caller.
                    continue

    def get_dashboard(self, user_id: str) -> DashboardSummary:
        user = self.user_repo.get(user_id)
        levels: List[DashboardLevelSummary] = []
        for level, config in self.commission_plan.items():
            unlocked = user.direct_referral_count >= config.direct_requirement
            levels.append(
                DashboardLevelSummary(
                    level=level,
                    requirement=config.direct_requirement,
                    direct_referrals=user.direct_referral_count,
                    unlocked=unlocked,
                    pending_amount=user.wallet.total_by_level(level, status=CommissionStatus.PENDING),
                    available_amount=user.wallet.total_by_level(level, status=CommissionStatus.AVAILABLE),
                )
            )

        return DashboardSummary(
            user_id=user.id,
            name=user.name,
            direct_referrals=user.direct_referral_count,
            available_balance=user.wallet.available_balance,
            pending_balance=user.wallet.pending_balance,
            levels=levels,
        )

    def list_users(self) -> List[User]:
        return list(self.user_repo.all())
