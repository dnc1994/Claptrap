REQUEST = 0
RESPONSE = 1

REQUEST_PARAMS = {
    'LOGIN': ['Username', 'Password'],
    'LOGOUT': [],
    'CREATE_ROOM': ['Room-Name'],
    'LIST_ROOMS': [],
    'LIST_MEMBERS': [],
    'JOIN_ROOM': ['Room-Name'],
    'LEAVE_ROOM': ['Room-Name'],
    'SEND_MSG': ['Content-Length', 'Content'],
    'RECV_MSG': []
}
REQUEST_METHODS = REQUEST_PARAMS.keys()

RESPONSE_PARAMS = {
    'RESP_LOGIN': ['Status'],
    'BYEBYE': [],
    'RESP_CREATE_ROOM': ['Status'],
    'RESP_LIST_ROOMS': [],
    'RESP_LIST_MEMBERS': [],
    'RESP_JOIN_ROOM': [],
    'SEE_YOU': [],
    'RESP_SEND_MSG': ['Status'],
    'NO_NEW_MSG': [],
    'NEW_MSG': ['From', 'Time', 'Content-Length', 'Content']
}
RESPONSE_METHODS = RESPONSE_PARAMS.keys()

PARSE_EXCEPTIONS = ['BAD_METHOD', 'INCOMPLETE_PARAMS', 'CONTENT_LENGTH_MISMATCH']

CONSTANTS = [(REQUEST_METHODS, REQUEST_PARAMS), (RESPONSE_METHODS, RESPONSE_PARAMS)]

def parse(data, type):
    try:
        METHODS, PARAMS = CONSTANTS[type]
    except:
        # todo: logging
        return 'UNSUPPORTED_TYPE', None

    lines = data.split('\n')
    method = lines[0].strip()
    if method not in METHODS:
        return 'BAD_METHOD', None

    required_params = PARAMS[method]
    params = {}
    content = None

    for (index, line) in enumerate(lines[1:]):
        if line == '\n':
            if 'Content' in required_params:
                content = ''.join(lines[index+1:])
            break
        (k, v) = line.strip().split(': ')
        params[k] = v
    params['Content'] = 'Placeholder'

    if required_params and (not all([params.has_key(rp) for rp in required_params])):
        return 'INCOMPLETE_PARAMS', None

    if 'Content' in required_params:
        if not content or len(content) != params['Content-Length']:
            return 'CONTENT_LENGTH_MISMATCH', None
        else:
            params['Content'] = content
    else:
        del params['Content']

    return method, params
