from datetime import datetime

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def is_valid_time(time_string):
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False