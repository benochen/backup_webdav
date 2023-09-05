from enum import Enum


class StatusCodes(Enum):
    # 1xx Informational
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202

    # 3xx Redirection
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302

    # 4xx Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404

    # 5xx Server Error
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

    #6xx Integrity check

    HASHES_MATCH = 600
    HASHES_NOT_MATCH= 601