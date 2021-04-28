import datetime

from flask import current_app, make_response, request
from functools import wraps, update_wrapper

import dash_uploader.settings as settings


def cross_domain(origin=None, methods=None, headers=None,
                 max_age=21600, attach_to_all=True,
                 automatic_options=True):
    '''
    A decorator for the cross-domain fixture.
    Modified by cainmagi@github
    This decorator is used for those APIs requiring the cross-domain
    access. Thanks for the work of rayitopy@stackoverflow
        https://stackoverflow.com/a/45054690

    Parameters
    ----------
    origin: str, or a sequence of str
        The allowed origin(s) from different domains. If set '*',
        all domains would be allowed. If set None, would use
        du.settings to configure the origin(s).
    methods: str, or a sequence of str
        The allowed methods of the cross-domain access. If set None,
        would use the default configuration of the flask.
    max_age: int or datetime.timedelta
        The max age (seconds) of the cross-domain requests.
    attach_to_all: bool
        Whether to attach the cross-domain headers to all required
        methods. If set False, the headers would be only added to
        OPTIONS request.
    automatic_options: bool
        Whether to use the flask default OPTIONS response. If set
        False, users need to implement OPTIONS response.

    Example
    -------
    @app.route('/api/v1/user', methods=['OPTIONS', 'POST'])
    @crossdomain(origin="*")
    def add_user():
        pass

    '''
    if methods is not None:
        if isinstance(methods, str):
            methods = [methods]
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if origin is None:
        origin = settings.allowed_origins
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, datetime.timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator
