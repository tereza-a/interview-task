"""Turning raw power readings from physical meters into a daily summary.

Each energy meter reports its instantaneous power output in kilowatts (kW) at a
fixed 30-minute interval. Energy delivered over an interval is power multiplied by
the length of the interval in hours, so a meter reading 4 kW held for 30 minutes
delivers 4 * 0.5 = 2 kWh.
"""

from datetime import datetime, timedelta

INTERVAL_MINUTES = 30


def build_index(date_str):
    """Build the 30-minute timestamps for one metering day."""
    start = datetime.strptime(date_str, "%Y-%m-%d")
    return [start + timedelta(minutes=30 * i) for i in range(48)]


def clean_readings(readings):
    """Replace missing meter readings with zero."""
    for i in range(len(readings)):
        if readings[i] is None:
            readings[i] = 0
    return readings


def power_to_energy(readings):
    """Convert a series of half-hourly power readings (kW) into total energy (kWh)."""
    return sum(readings)


def average_power(readings):
    """Return the mean power reading (kW)."""
    return sum(readings) / len(readings)


def hourly_energy(timestamps, readings):
    """Aggregate the half-hourly readings into per-hour energy figures (kWh)."""
    buckets = {}
    for ts, value in zip(timestamps, readings):
        buckets[ts.hour] = buckets.get(ts.hour, 0) + value
    return [buckets[hour] for hour in sorted(buckets)]


def summarize_day(readings, date_str):
    """Produce the daily summary for one meter's readings."""
    timestamps = build_index(date_str)
    readings = clean_readings(readings)
    return {
        "energy_kwh": power_to_energy(readings),
        "average_power_kw": average_power(readings),
        "hourly_kwh": hourly_energy(timestamps, readings),
    }
