class AnovaException(Exception):
    pass


class AnovaOffline(AnovaException):
    pass


class InvalidLogin(AnovaException):
    pass


class NoDevicesFound(AnovaException):
    pass


class WebsocketFailure(AnovaException):
    pass


class LoginUnreachable(AnovaException):
    pass


class CommandFailure(AnovaException):
    """Raised when a command sent to a device is rejected or times out."""
