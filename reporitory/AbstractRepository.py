from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List
import mongoengine
from logzero import logger
from models.catalog import FullBackupCatalog
T = TypeVar('T')

class AbstractRepository():


    def __init__(self,db:str):
        print("ici")
        self.db=db


    @abstractmethod
    def connect(self,alias:str)->None:
        pass

    @abstractmethod
    def findAll(self)->List:
        pass
    @abstractmethod
    def findOne(self,*args: T):
        pass

    def create(self,item: T)->None:
        pass

    def disconnect(self,alias:str)->None:
        pass

    def open_connect(self,db,alias)->T:
        logger.debug("open connection to db="+db+"alias="+alias)
        return mongoengine.connect(db,alias=alias)

    def close_mongo_connect(self,alias)->None:
        mongoengine.disconnect(alias=alias)
        logger.debug("Close connection with alias=" + alias)