from packaging import version
import pkg_resources

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
