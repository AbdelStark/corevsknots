"""
Time utilities for the Bitcoin Repository Health Analysis Tool.

This module provides functions for working with dates and times.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union

# Define ISO 8601 format
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_date(date_str: str) -> datetime:
    """
    Parse a date string into a datetime object.

    Args:
        date_str: ISO 8601 formatted date string

    Returns:
        Datetime object

    Raises:
        ValueError: If the date string is not in a recognized format
    """
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 with Z suffix
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with timezone offset
        "%Y-%m-%dT%H:%M:%S",  # ISO 8601 without timezone
        "%Y-%m-%d %H:%M:%S",  # Simple format with space
        "%Y-%m-%d",  # Date only
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")


def format_date(date: datetime, fmt: str = ISO_FORMAT) -> str:
    """
    Format a datetime object as a string.

    Args:
        date: Datetime object
        fmt: Format string (default: ISO 8601)

    Returns:
        Formatted date string
    """
    return date.strftime(fmt)


def months_ago(months: int) -> datetime:
    """
    Get a datetime object representing N months ago.

    Args:
        months: Number of months ago

    Returns:
        Datetime object representing N months ago
    """
    today = datetime.utcnow()

    # Calculate the year and month
    year = today.year
    month = today.month - months

    # Adjust year and month if needed
    while month <= 0:
        year -= 1
        month += 12

    # Create a new datetime object
    # Making sure to handle edge cases for days in month
    # (e.g., if today is May 31 and we go back 1 month, we want April 30, not an error)
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Adjust for leap years
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[1] = 29

    day = min(today.day, days_in_month[month - 1])

    return datetime(year, month, day, today.hour, today.minute, today.second)


def today_utc() -> datetime:
    """
    Get the current UTC date.

    Returns:
        Current UTC date
    """
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


def date_range(
    start_date: datetime, end_date: datetime, step: timedelta = timedelta(days=1)
) -> list:
    """
    Generate a range of dates.

    Args:
        start_date: Start date
        end_date: End date
        step: Step size (default: 1 day)

    Returns:
        List of dates
    """
    result = []
    current_date = start_date

    while current_date <= end_date:
        result.append(current_date)
        current_date += step

    return result
