import datetime
import platform


def millisToDatetime(millis: int) -> datetime.datetime:
    """ This converts from milliseconds to a datetime object. """
    return datetime.datetime.fromtimestamp(millis / 1000)


def datetimeToMillis(dt: datetime.datetime) -> int:
    """ This converts from a datetime object to epoch millis. """
    return int(dt.timestamp() * 1000)


def formatDatetime(date: datetime.datetime):
    """ Formats a datetime into Month Abbr Day, Year Hour AM/PM"""
    if platform.system() == "Linux":
        return date.strftime('%b %-d, %Y %-I %p')
    else:
        formatted = date.strftime('%b %d, %Y %I %p')
        # Remove leading zeros from both day and hour
        formatted = formatted.replace(' 0', ' ')  # For hour

        # Replace day with leading zero
        parts = formatted.split()
        month = parts[0]
        day_with_comma = parts[1]

        # Remove leading zero from day if present
        if day_with_comma.startswith('0'):
            day_with_comma = day_with_comma.replace('0', '', 1)

        parts[1] = day_with_comma
        return ' '.join(parts)


def formatDate(date):
    return date.isoformat()

