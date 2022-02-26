import logging
from typing import final
from packaging import version
import pkg_resources
import time

## Dash version
dash_version_str = pkg_resources.get_distribution("dash").version
dash_version = version.parse(dash_version_str)


def dash_version_is_at_least(req_version="1.12"):
    """Check that the used version of dash is greater or equal
    to some version `req_version`.

    Will return True if current dash version is greater than
    the argument "req_version".
    This is a private method, and should not be exposed to users.
    """
    if isinstance(dash_version, version.LegacyVersion):
        return False
    return dash_version >= version.parse(req_version)


def retry(wait_time, max_time):
    """
    decorator to call a function until success

    Parameters
    ----------
    wait_time: numeric
        The wait time in seconds between trials
    max_time: numeric
        Maximum time to wait
    """

    def add_callback(function):
        def wrapper(*args, **kwargs):
            t0 = time.time()
            i = 1
            while True:
                try:
                    if i > 1:
                        logtxt = (
                            f"Trying to call function '{function.__name__}'! Trial #{i}."
                            + f" Used time: {time.time() - t0:.2}s",
                        )
                        logging.warning(logtxt)
                    out = function(*args, **kwargs)
                    break
                except Exception as e:
                    if time.time() - t0 > max_time:
                        raise e
                    else:
                        time.sleep(wait_time)
                finally:
                    i += 1
            return out

        return wrapper

    return add_callback
