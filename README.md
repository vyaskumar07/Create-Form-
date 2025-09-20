# MLM Course Commission Backend

This repository provides a Python implementation of a 4-level affiliate/MLM commission
structure for a ₹3000 stock market crash course. The business rules implemented are:

- ₹1000 from every sale goes to the company. The remaining ₹2000 are distributed
  across four affiliate levels.
- Level payouts: level 1 ₹1000, level 2 ₹250, level 3 ₹250, level 4 ₹500.
- Level activation thresholds: level 1 unlocked immediately, level 2 after 10 direct
  referrals, level 3 after 25 direct referrals, level 4 after 50 direct referrals.
- When a level is not yet unlocked the potential commission is tracked as *pending*
  and is released automatically once the direct referral requirement is met.

## Project layout

```
mlm_backend/
├── config.py         # Commission plan configuration
├── models.py         # Dataclasses describing users and commission records
├── repository.py     # In-memory repository abstraction
└── service.py        # Business logic for registrations and payouts
main.py               # Demonstration script
```

## Usage

The simplest way to explore the behaviour is to run the demo script:

```bash
python main.py
```

It bootstraps a small network, unlocks higher level commissions for the
`sponsor`, and prints two sample dashboards.

For programmatic access instantiate the service directly:

```python
from mlm_backend import InMemoryUserRepository, MLMService

repo = InMemoryUserRepository()
service = MLMService(user_repo=repo)

service.register_user(user_id="company", name="Company")
service.register_user(user_id="mentor", name="Mentor", referrer_id="company")
service.register_user(user_id="student", name="Student", referrer_id="mentor")

dashboard = service.get_dashboard("mentor")
print(dashboard.available_balance, dashboard.pending_balance)
```

## Running the tests

The repository contains unit tests that validate commission distribution and the
unlocking logic. To execute them run:

```bash
python -m pytest
```
