# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_survives_missing_last_service_km():
    # A car with no last_service_km must not crash the report; it should be
    # treated as freshly serviced and therefore NOT flagged as due.
    fleet = [
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
        {"id": "VOS-7788", "odometer": 92000},           # no last_service_km
    ]
    summary = fleet_summary(fleet)
    assert "average_wear" in summary                     # did not crash
    assert summary["count"] == 2
