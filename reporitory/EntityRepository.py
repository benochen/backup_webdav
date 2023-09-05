from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

import mongoengine
from logzero import logger

from reporitory.AbstractRepository import AbstractRepository
from models.entities.Entity import Entity
from mongoengine import *
T = TypeVar('T')

class EntityRepository(AbstractRepository):

    def __init__(self,db:str):
        super().__init__(db)
        self.alias="default"


    def findAll(self)->List:
        res=list()
        for iterable_object in EntityRepository.objects():
            res.append(iterable_object)
        logger.debug("Collection entity correctly loaded")
        return res

    def findOne(self,*args: T)->Entity:
        name=args[0]
        if name is None:
            raise TypeError("Invalid argument provided for find one")
        logger.debug("Start searching entity with name="+name)
        self.open_connect(self.db,self.alias)
        if Entity.objects(name=name).count()>0:
            logger.debug("object with name="+name+" found")
            res=Entity.objects(name=name).first()
        else:
            logger.debug("object with name=" + name + "not found")
            res=None
        self.close_mongo_connect(self.alias)
        return res


    def insert(self,*args:T)->None:

        if(Entity.objects(name=args[0].name).count()==0):
            args[0].save()


    def create(self,item: T)->None:
        pass

