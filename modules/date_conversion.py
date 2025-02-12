# modules/date_conversion.py

"""
This module provides functions to parse date strings that may be in either
the Gregorian calendar or the Jalali (Iranian) calendar. If a date string
has a year between 1300 and 1500, it is assumed to be in the Jalali calendar
and will be converted to Gregorian using the jdatetime library.

Supported date formats:
    - Gregorian: "YYYY/MM/DD" or "YYYY-MM-DD" with optional time "HH:MM" (e.g., "2023/03/21 15:30")
    - Jalali: "YYYY/MM/DD" or "YYYY-MM-DD" with optional time "HH:MM" (e.g., "1400/01/15 08:45")
"""

import datetime
import jdatetime

def parse_date(date_str):
    """
    Parses a date string and returns a datetime.datetime object in the Gregorian calendar.
    
    The function supports input with an optional time part. If the time is not provided,
    it defaults to 00:00.
    
    Supported formats:
      - Gregorian: "YYYY/MM/DD" or "YYYY-MM-DD", optionally with "HH:MM"
      - Jalali: "YYYY/MM/DD" or "YYYY-MM-DD", optionally with "HH:MM",
        where the year is between 1300 and 1500.
        
    Args:
        date_str (str): The input date string.
        
    Returns:
        datetime.datetime: The corresponding Gregorian datetime.
        
    Raises:
        ValueError: If the date_str is not in a valid format or conversion fails.
    """
    # Split the input into date and time parts.
    parts = date_str.strip().split()
    date_part = parts[0]
    time_part = "00:00"
    if len(parts) > 1:
        time_part = parts[1]
    
    # Standardize date delimiter by replacing '-' with '/'
    date_part = date_part.replace("-", "/")
    date_components = date_part.split("/")
    if len(date_components) < 3:
        raise ValueError("Invalid date format. Expected format: YYYY/MM/DD")
    
    try:
        year = int(date_components[0])
        month = int(date_components[1])
        day = int(date_components[2])
    except Exception as e:
        raise ValueError("Date components must be integers") from e
    
    # Parse time components.
    time_components = time_part.split(":")
    if len(time_components) < 2:
        raise ValueError("Invalid time format. Expected format: HH:MM")
    try:
        hour = int(time_components[0])
        minute = int(time_components[1])
    except Exception as e:
        raise ValueError("Time components must be integers") from e

    # Determine if the date is Jalali or Gregorian based on the year.
    if 1300 <= year <= 1500:
        # Assume Jalali date and convert it to Gregorian using jdatetime.
        try:
            jalali_date = jdatetime.date(year, month, day)
            gregorian_date = jalali_date.togregorian()  # returns a datetime.date
            return datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day, hour, minute)
        except Exception as e:
            raise ValueError("Error converting Jalali date to Gregorian") from e
    else:
        # Assume Gregorian date.
        try:
            return datetime.datetime(year, month, day, hour, minute)
        except Exception as e:
            raise ValueError("Error parsing Gregorian date") from e

if __name__ == "__main__":
    # Test cases to demonstrate date conversion.
    test_dates = [
        "1400/01/15",             # Jalali date without time.
        "2022/12/31",             # Gregorian date without time.
        "1400-07-10 08:30",        # Jalali with hyphen and time.
        "2023-03-21 15:45"         # Gregorian with hyphen and time.
    ]
    
    for d in test_dates:
        try:
            converted = parse_date(d)
            print(f"Input: {d} --> Gregorian: {converted.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            print(f"Failed to parse {d}: {e}")
