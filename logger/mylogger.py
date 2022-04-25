
from logzero import logger, logfile



class MyLogger:

    def __init__(self,file,formatter):
        self.file=file
        self.rotate=""
        self.logfile=logfile(file)
        self.formatter=formatter


    def debug(self,message):
      #  logger.Formatter(self.formatter)
        logger.debug(message)

    def info(self,message):
        logger.Formatter(self.formatter)
        logger.info(message)

    def error(self,message):
        logger.Formatter(self.formatter)
        logger.info(message)
