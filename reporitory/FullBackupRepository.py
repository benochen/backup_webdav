from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

T = TypeVar('T')

class AbstractRepository():

    @abstractmethod
    def findAll(self)->List:
        pass
    @abstractmethod
    def findOne(self,*args: T):
        pass

    def create(self,item: T)->None:
        pass