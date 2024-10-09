import logging
import sys
import time

from packaging.version import parse as parse_version

if sys.version_info < (3, 8):
    import pkg_resources

    DASH_VERSION_STR = pkg_resources.get_distribution("dash").version
else:
    from importlib.metadata import version as get_version

    DASH_VERSION_STR = get_version("dash")

DASH_VERSION = parse_version(DASH_VERSION_STR)


def dash_version_is_at_least(req_version="1.12"):
    """Check that the used version of dash is greater or equal
    to some version `req_version`.

    Will return True if current dash version is greater than
    the argument "req_version".
    This is a private method, and should not be exposed to users.
    """
    return DASH_VERSION >= parse_version(req_version)


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
