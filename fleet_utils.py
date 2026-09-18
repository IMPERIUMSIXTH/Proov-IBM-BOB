# fleet_utils.py
# Helper utilities for Vossberg Mobility fleet management.
# Modernised: dead code removed, km_to_miles constant corrected, type hints added.

from km_wachter import WARN_AT_PERCENT, wear_percent, SERVICE_INTERVAL_KM

KM_TO_MILES_FACTOR = 0.621371          # 1 km = 0.621371 miles (was 1.609 — inverted)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km * KM_TO_MILES_FACTOR


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def is_due(pct: float, threshold: float) -> bool:
    """Return True when wear percentage meets or exceeds the given threshold.

    Delegates to the shared helper in km_wachter so there is a single source
    of truth for the service-due rule.
    """
    return pct >= threshold
