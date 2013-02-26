from datetime import datetime

def get_datetime_now_formatted():
    # useful for user messages when creating or updating objects
    return datetime.now().strftime('%c')

def get_messages(request):
    """
    Can return an arbitrary number of messages from this method, passed via a number of methods.
    1. Query string can pass one message.
    2. UNFINISHED. Pass via template (number of messages unknown).
    Messages can have optional classes, which changes appearance
    """

    # message classes map to bootstrap css alert style names. n.b. default bootstrap alert is yellow (warning), but our default is blue (info)
    message_classes = {'info': 'alert-info', 'warning':'', 'success': 'alert-success', 'error': 'alert-error'}

    messages = []
    if len(request.query.get('message', '')) > 0:
        message = {}
        message['content'] = request.query.get('message', '')
        message['class'] = message_classes[request.query.get('message_class', 'info')]
        messages.append(message)

    if len(messages) > 0:
        return messages
    else:
        return None

def get_status_definition_strings():
    status_definitions = {'UNKNOWN': {'title': 'Unknown', 'description': 'The state of the translation was not decidable'},
                          'UP_TO_DATE': {'title': 'Correct', 'description': 'The string is technically correct and up to date'},
                          'OUT_OF_DATE': {'title': 'Outdated', 'description': 'A valid translation exists, but it needs review as a newer base language text exists'},
                          'INVALID': {'title': 'Invalid', 'description': 'A translation exists, but its string parameters do not match with the base language'},
                          'MISSING_OK': {'title': 'Missing', 'description': 'No translation could be found'}}
    return status_definitions
