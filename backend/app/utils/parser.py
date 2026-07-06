from datetime import datetime, timedelta, date, time


def parse_date(date_str: str) -> date:
    """
    Convert different date formats into a Python date object.
    """

    value = date_str.strip().lower()

    today = datetime.today().date()

    if value == "today":
        return today

    if value == "tomorrow":
        return today + timedelta(days=1)

    formats = [
        "%Y-%m-%d",   # 2026-07-06
        "%d-%m-%Y",   # 06-07-2026
        "%d/%m/%Y",   # 06/07/2026
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Invalid date: {date_str}")


def parse_time(time_str: str) -> time:
    """
    Convert different time formats into a Python time object.
    """

    value = (
        time_str
        .replace(".", ":")
        .upper()
        .strip()
    )

    formats = [
        "%H:%M",
        "%H:%M:%S",
        "%I:%M %p",
        "%I:%M%p",
        "%I %p",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    raise ValueError(f"Invalid time: {time_str}")