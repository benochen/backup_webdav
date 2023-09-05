import logzero
from logzero import logger, logfile
from ErrorCode.ErrorCode import StatusCodes
import json

class JSONLogger:
    def __init__(self, filename):
        logzero.json()
        self.logger = logzero.setup_logger(name='json_logger', logfile=filename)
        logzero.logfile(filename)
        self.webdav_username=""
        self.entity=""

    def __init__(self, filename,webdav_user,entity):
        logzero.json()
        logzero.logfile(filename)
        self.logger = logzero.setup_logger(name='json_logger', logfile=filename)
        self.webdav_username=webdav_user
        self.entity=entity


    def info(self, message, reason, status_code, *args):
        logger.log(logzero.INFO, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason' : reason,
            'status_code': status_code,

        })

    def info_status(self, message, status_code, *args):
        logger.log(logzero.INFO, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason' : "",
            'status_code': status_code
        })

    def info(self, message, *args):
        logger.log(logzero.INFO, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason': "",
            'status_code': StatusCodes.CONTINUE.value
        })

    def debug(self, message, *args):
        logger.log(logzero.DEBUG, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason': "",
            'status_code': StatusCodes.CONTINUE.value
        })

    def error(self, message, reason, status_code, *args):
        logger.log(logzero.ERROR, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason' : reason,
            'status_code': status_code
        })
    def error(self, message, status_code, *args):
        logger.log(logzero.ERROR, message % args, extra={
            'webdav_username': self.webdav_username,
            'entity': self.entity,
            'reason' :"",
            'status_code': status_code
        })