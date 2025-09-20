"""Configuration for the MLM commission plan."""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LevelConfig:
    """Represents the payout and activation requirement for a level."""

    level: int
    payout: int
    direct_requirement: int


COURSE_PRICE = 3000
COMPANY_SHARE = 1000


COMMISSION_PLAN: Dict[int, LevelConfig] = {
    1: LevelConfig(level=1, payout=1000, direct_requirement=0),
    2: LevelConfig(level=2, payout=250, direct_requirement=10),
    3: LevelConfig(level=3, payout=250, direct_requirement=25),
    4: LevelConfig(level=4, payout=500, direct_requirement=50),
}
