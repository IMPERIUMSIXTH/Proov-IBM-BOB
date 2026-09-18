# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Modernised and crash bugs fixed.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float:
    """Return wear percentage for a car.

    Uses last_service_km if present; falls back to the car's current odometer
    (i.e. 0 km since service) so a missing reading never crashes the report.
    """
    odometer = car["odometer"]
    last = car.get("last_service_km", odometer)   # missing → treat as freshly serviced
    return wear_percent(odometer - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list) -> dict:
    """Return a summary dict: count, due count, and average wear (float, 4 d.p.)."""
    total = 0.0
    due = 0
    for car in fleet:
        total += car_wear(car)
        if needs_service(car):
            due += 1
    average = round(total / len(fleet), 4)   # true division, not floor
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list) -> None:
    """Print the nightly fleet-health report and flush the log."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.2f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # The partner garage in England wants distance in miles (since 2015).
    print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))
