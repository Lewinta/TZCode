from datetime import datetime, timedelta

def week_start(date=None):
    """
    Returns the start of the current week based on the given date.
    If no date is provided, it defaults to the current date.
    """
    if date is None:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Calculate the start of the current week (Monday)
    start_of_week = date - timedelta(days=date.weekday())

    return start_of_week

def week_end(date=None):
    """
    Returns the end of the current week based on the given date.
    If no date is provided, it defaults to the current date.
    """
    if date is None:
        date = datetime.now().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Calculate the start of the current week (Monday)
    start_of_week = date - timedelta(days=date.weekday())

    # Calculate the end of the current week (Sunday)
    end_of_week = start_of_week + timedelta(days=6)

    return end_of_week

