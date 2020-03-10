

class MinidException(Exception):
    """A general minid exception"""
    pass


class LoginRequired(MinidException):
    """An exception happened because a login is required"""
    pass


class UnknownIdentifier(MinidException):
    """The given identifier is not a known type in the Minid ecosystem."""
    pass
