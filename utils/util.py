from datetime import datetime
import re


def format_date_to_airbnb(date: datetime, verbose: bool = True):
    """
    Formats a datetime object into a string representation suitable for Airbnb.

    Args:
        date (datetime): The date to be formatted.
        verbose (bool, optional): If True, includes the full weekday and month
                                  names in the output. Defaults to True.

    Returns:
        str: The formatted date string.
             - If verbose is True, the format is "day, weekday, month year".
             - If verbose is False, the format is "month_abbr day".
    """

    day = date.day
    month = date.strftime("%B")
    year = date.year
    weekday = date.strftime("%A")

    if verbose:
        return f"{day}, {weekday}, {month} {year}"
    return f"{month[:3]} {day}"


def parse_dates(dates_str: str) -> tuple[datetime, datetime]:
    """
    Parses a date string into start and end datetime objects.

    Args:
        dates_str (str): A string containing date information.

    Returns:
        tuple[datetime, datetime]: A tuple containing the start and end dates as datetime objects.
    """

    # First the year

    if "," not in dates_str:
        year = datetime.now().year
    else:
        year = int(dates_str.split(",")[1].strip())
        dates_str = dates_str.split(",")[0].strip()

    # Split to check-in and check-out
    parts = dates_str.split("–")

    # Check-in
    start_part = parts[0].strip()
    start_month, start_day = start_part.split()
    start_day = int(start_day)
    start_month_num = datetime.strptime(start_month, "%b").month
    start_date = datetime(year, start_month_num, start_day)

    # Check-out - more complex
    end_part = parts[1].strip()

    if " " in end_part:
        # Then th format is as the start part
        end_month, end_day = end_part.split()
        end_day = int(end_day)
        end_month_num = datetime.strptime(end_month, "%b").month
        end_date = datetime(year, end_month_num, end_day)
    else:
        # Then it's only the days, same month
        end_day = int(end_part)
        end_date = datetime(year, start_month_num, end_day)

    return start_date, end_date


def parse_guests(guests_str: str):
    """
    Parse the number of guests from a string.

    The string can be one of the following formats:
    - "X guests"
    - "X adults, Y children"

    Returns:
        tuple[int, int, int]: A tuple containing:
            - The total number of guests.
            - The number of adults (-1 if not specified).
            - The number of children (-1 if not specified).
    """

    if "guest" in guests_str:
        num = int(guests_str.split()[0].strip())
        return num, -1, -1

    adults = 0
    children = 0

    # Check for adults
    adult_match = re.search(r"(\d+)\s+adult", guests_str)
    if adult_match:
        adults = int(adult_match.group(1))

    # Check for children
    child_match = re.search(r"(\d+)\s+child", guests_str)
    if child_match:
        children = int(child_match.group(1))

    total = adults + children

    return total, adults, children
