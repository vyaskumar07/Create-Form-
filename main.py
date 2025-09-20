"""Example script demonstrating the MLM backend logic."""
from pprint import pprint

from mlm_backend import InMemoryUserRepository, MLMService


def bootstrap_demo() -> None:
    repo = InMemoryUserRepository()
    service = MLMService(user_repo=repo)

    # Company/root user without a referrer.
    service.register_user(user_id="company", name="Company")

    # First affiliate directly connected to company.
    service.register_user(user_id="mentor", name="Mentor", referrer_id="company")

    # Downline chain to showcase multi-level distribution.
    service.register_user(user_id="trader_a", name="Trader A", referrer_id="mentor")
    service.register_user(user_id="trader_b", name="Trader B", referrer_id="trader_a")
    service.register_user(user_id="trader_c", name="Trader C", referrer_id="trader_b")

    # Enroll additional direct partners for mentor to unlock level 2 earnings.
    for index in range(1, 10):
        service.register_user(
            user_id=f"mentor_ref_{index}",
            name=f"Mentor Referral {index}",
            referrer_id="mentor",
        )

    print("=== Mentor dashboard ===")
    pprint(service.get_dashboard("mentor"))

    print("\n=== Company dashboard ===")
    pprint(service.get_dashboard("company"))


if __name__ == "__main__":
    bootstrap_demo()
