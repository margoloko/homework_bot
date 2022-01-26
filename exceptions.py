import requests


class ServerError(requests.RequestException):
    pass


class TokenError(KeyError):
    pass
