from datetime import datetime

def get_datetime_now_formatted():
    # useful for user messages when creating or updating objects
    return datetime.now().strftime('%c')

def get_message(request):
    if len(request.query.get('message', '')) > 0:
        return request.query.get('message', '')
    else:
        return None
