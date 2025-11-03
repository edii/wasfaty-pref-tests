# Define a custom filter for formatting datetimes
def datetimeformat(value, format='%Y-%m-%dT%H:%M:%SZ'):
    return value.strftime(format)
