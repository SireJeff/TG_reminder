# modules/date_conversion.py

"""
This module provides functions to parse date strings that may be in either
the Gregorian calendar or the Jalali (Iranian) calendar. If a date string
has a year between 1300 and 1500, it is assumed to be in the Jalali calendar
and will be converted to Gregorian using the jdatetime library.

Supported date formats:
    - Gregorian: "YYYY/MM/DD" or "YYYY-MM-DD" (e.g., "2023/03/21" or "2023-03-21")
    - Jalali: "YYYY/MM/DD" or "YYYY-MM-DD" (e.g., "1400/01/15" or "1400-01-15")
"""

import datetime
import jdatetime

def parse_date(date_str):
    """
    Parses a date string and returns a datetime.datetime object in the Gregorian calendar.

    The function supports two formats:
      - Gregorian dates in the format "YYYY/MM/DD" or "YYYY-MM-DD".
      - Jalali (Iranian) dates in the format "YYYY/MM/DD" or "YYYY-MM-DD",
        where the year is between 1300 and 1500.
        
    If the year is between 1300 and 1500, it is assumed to be Jalali and is
    converted to Gregorian.

    Args:
        date_str (str): The input date string.

    Returns:
        datetime.datetime: The corresponding Gregorian date (with time set to 00:00).

    Raises:
        ValueError: If the date_str is not in a valid format or conversion fails.
    """
    # Standardize delimiter: replace '-' with '/'
    date_str = date_str.replace("-", "/")
    parts = date_str.split("/")
    if len(parts) < 3:
        raise ValueError("Invalid date format. Expected format: YYYY/MM/DD")
    
    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
    except Exception as e:
        raise ValueError("Date components must be integers") from e

    # Determine if the date is Jalali or Gregorian based on the year.
    if 1300 <= year <= 1500:
        # Assume Jalali date and convert it to Gregorian using jdatetime.
        try:
            jalali_date = jdatetime.date(year, month, day)
            gregorian_date = jalali_date.togregorian()  # returns a datetime.date
            return datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        except Exception as e:
            raise ValueError("Error converting Jalali date to Gregorian") from e
    else:
        # Assume Gregorian date.
        try:
            return datetime.datetime(year, month, day)
        except Exception as e:
            raise ValueError("Error parsing Gregorian date") from e

if __name__ == "__main__":
    # Test cases to demonstrate date conversion.
    test_dates = [
        "1400/01/15",  # Expected to convert from Jalali to Gregorian.
        "2022/12/31",  # Gregorian.
        "1400-07-10",  # Jalali with hyphen delimiter.
        "2023-03-21"   # Gregorian with hyphen delimiter.
    ]
    
    for d in test_dates:
        try:
            converted = parse_date(d)
            print(f"Input: {d} --> Gregorian: {converted.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"Failed to parse {d}: {e}")
