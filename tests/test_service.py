"""Unit tests for the MLM service."""
from mlm_backend import InMemoryUserRepository, MLMService


def create_service() -> MLMService:
    return MLMService(user_repo=InMemoryUserRepository())


def test_single_referral_earns_level_one_commission() -> None:
    service = create_service()
    service.register_user(user_id="company", name="Company")
    service.register_user(user_id="alice", name="Alice", referrer_id="company")

    dashboard = service.get_dashboard("company")
    assert dashboard.available_balance == 1000
    assert dashboard.pending_balance == 0
    level_one = next(level for level in dashboard.levels if level.level == 1)
    assert level_one.available_amount == 1000
    assert level_one.pending_amount == 0


def test_commissions_become_pending_until_unlock() -> None:
    service = create_service()
    service.register_user(user_id="top", name="Top")
    service.register_user(user_id="mid", name="Mid", referrer_id="top")
    service.register_user(user_id="bottom", name="Bottom", referrer_id="mid")

    top_dashboard = service.get_dashboard("top")
    level_two = next(level for level in top_dashboard.levels if level.level == 2)
    assert level_two.pending_amount == 250
    assert top_dashboard.pending_balance == 250
    assert top_dashboard.available_balance == 1000


def test_unlocking_releases_pending_commissions() -> None:
    service = create_service()
    service.register_user(user_id="root", name="Root")
    service.register_user(user_id="leader", name="Leader", referrer_id="root")

    # Create a downline that gives leader a level 1 commission and root a pending level 2 commission.
    service.register_user(user_id="student", name="Student", referrer_id="leader")

    root_dashboard = service.get_dashboard("root")
    assert root_dashboard.pending_balance == 250

    # Add additional direct referrals for root to satisfy the level 2 requirement (10 direct referrals total).
    for index in range(1, 10):
        service.register_user(
            user_id=f"root_ref_{index}",
            name=f"Root Referral {index}",
            referrer_id="root",
        )

    updated_dashboard = service.get_dashboard("root")
    assert updated_dashboard.pending_balance == 0
    level_two = next(level for level in updated_dashboard.levels if level.level == 2)
    assert level_two.available_amount == 250
    assert level_two.pending_amount == 0


def test_multiple_levels_unlocking_progressively() -> None:
    service = create_service()
    service.register_user(user_id="root", name="Root")

    # Create a chain of 4 levels.
    service.register_user(user_id="l1", name="Level1", referrer_id="root")
    service.register_user(user_id="l2", name="Level2", referrer_id="l1")
    service.register_user(user_id="l3", name="Level3", referrer_id="l2")
    service.register_user(user_id="l4", name="Level4", referrer_id="l3")

    root_dashboard = service.get_dashboard("root")
    assert root_dashboard.available_balance == 1000
    assert root_dashboard.pending_balance == 1000  # level 2, 3, 4 pending (250 + 250 + 500)

    # Unlock level 2 by adding more directs.
    for index in range(1, 10):
        service.register_user(user_id=f"root_l2_{index}", name=f"Root L2 {index}", referrer_id="root")
    level2_dashboard = service.get_dashboard("root")
    level2_summary = next(level for level in level2_dashboard.levels if level.level == 2)
    assert level2_summary.available_amount == 250
    assert level2_summary.pending_amount == 0
    assert level2_dashboard.pending_balance == 750

    # Unlock level 3 after 25 directs (already 10, need 15 more).
    for index in range(10, 25):
        service.register_user(user_id=f"root_l3_{index}", name=f"Root L3 {index}", referrer_id="root")
    level3_dashboard = service.get_dashboard("root")
    level3_summary = next(level for level in level3_dashboard.levels if level.level == 3)
    assert level3_summary.available_amount == 250
    assert level3_summary.pending_amount == 0
    assert level3_dashboard.pending_balance == 500

    # Unlock level 4 after 50 directs (already 25, need 25 more).
    for index in range(25, 50):
        service.register_user(user_id=f"root_l4_{index}", name=f"Root L4 {index}", referrer_id="root")
    final_dashboard = service.get_dashboard("root")
    level4_summary = next(level for level in final_dashboard.levels if level.level == 4)
    assert level4_summary.available_amount == 500
    assert level4_summary.pending_amount == 0
    assert final_dashboard.pending_balance == 0
