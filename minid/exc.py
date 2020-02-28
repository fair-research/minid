

class MinidException(Exception):
    """A general minid exception"""
    pass


class LoginRequired(MinidException):
    """An exception happened because a login is required"""
    pass
