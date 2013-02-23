from datetime import datetime

def get_datetime_now_formatted():
    # useful for user messages when creating or updating objects
    return datetime.now().strftime('%c')
