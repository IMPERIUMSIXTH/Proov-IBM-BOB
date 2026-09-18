# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernised and bugs fixed.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return wear as a percentage (0-100+) of one service interval."""
    ratio = km_since_service / interval   # true division — floor was silently zeroing near-due cars
    return ratio * 100


def _service_due(pct: float) -> bool:
    """Return True when wear percentage meets or exceeds the warning threshold."""
    return pct >= WARN_AT_PERCENT


def needs_service(car: dict) -> bool:
    """Return True if the car is due for service.

    A car with no last_service_km reading is treated as freshly serviced
    (odometer value used as baseline) so it is never wrongly flagged.
    """
    odometer = car["odometer"]
    last = car.get("last_service_km", odometer)   # missing → freshly serviced, not 0
    km_since = odometer - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return _service_due(pct)


def check_fleet(fleet: list) -> list:
    """Return a list of IDs for cars that need service."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
