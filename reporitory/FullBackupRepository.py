import datetime
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List
import jsonpickle
from datetime import date
import mongoengine
from logzero import logger
from models.entities.Entity import Entity
from models.catalog.Status import Status
from reporitory.AbstractRepository import AbstractRepository
from models.catalog.FullBackupCatalog import FullBackupCatalog
from mongoengine import *
import uuid
T = TypeVar('T')

#Comment class usage :
#This class is used to manage the FullBackupCatalog collection
class FullBackupRepository(AbstractRepository):

    #Comment method usage :
    #This method is used to initialize the FullBackupRepository class

    def __init__(self,db:str):
        super().__init__(db)
        self.alias="default"

    #Comment method usage :
    #This method is used to insert a new FullBackupCatalog object in the collection
    #pseudo code :
    #if the object is not already in the collection
    #   then insert the object in the collection
    #else
    #   do nothing
    def generateUUID(self,entity):
        backup_in_progress=self.findInProgressByEntity(entity)

        if backup_in_progress is None:
            return str(uuid.uuid4())
        else:
            return backup_in_progress.backup_id

    #comments and pseudo code :
    #if the object is not already in the collection
    #   then insert the object in the collection
    #else
    #   do nothing

    def findAll(self)->List:
        self.open_connect(self.db,self.alias)
        res=list()
        for iterable_object in FullBackupCatalog.objects():
            res.append(iterable_object)
        self.close_mongo_connect(self.alias)
        return res

    #comments describe usage , arguments and return value :
    #This method is used to find a FullBackupCatalog object in the collection
    #by the entity name
    #pseudo code :
    #if the object is in the collection
    #   then return the object
    #else
    #   return None
    def findInProgressByEntity(self,*args:T)->FullBackupCatalog:
        entity=args[0]
        self.open_connect(self.db,self.alias)
        if FullBackupCatalog.objects(entity=entity,status=Status.IN_PROGRESS).count()>0:
            print("InProgress entity Found")
            print(FullBackupCatalog.objects(entity=entity,status=Status.IN_PROGRESS).count())
            res = FullBackupCatalog.objects(entity=entity,status=Status.IN_PROGRESS).first()
        else:
            res=None
        self.close_mongo_connect(self.alias)
        return res

    #comments describe usage , arguments and return value :
    #This method is used to find a FullBackupCatalog object in the collection
    #by the backup_id
    #pseudo code :
    #if the object is in the collection
    #   then return the object
    #else
    #   return None
    def findOne(self,*args: T)->FullBackupCatalog:
        backup_id=args[0]
        logger.debug("Start searching Full backup catalog with backup_id="+backup_id)
        self.open_connect(self.db,self.alias)
        if FullBackupCatalog.objects(backup_id=backup_id).count()>0:
            logger.debug("Catalog with backup_id="+backup_id+" found")
            res=FullBackupCatalog.objects(backup_id=backup_id).first()
        else:
            logger.debug("object with name=" + backup_id + "not found")
            res=None
        self.close_mongo_connect(self.alias)
        return res

    #comments describe usage , arguments and return value :
    #This method is used to find a FullBackupCatalog object in the collection
    #by the entity name
    #pseudo code :
    #if the object is in the collection
    #   then return the object

    def delete(self,*args: T)->None:
        backup_id=args[0]
        logger.debug("check if backup_id is provided")
        if(backup_id is None):
            raise TypeError("")
        logger.debug("backup_id valid is %s",backup_id)
        logger.debug("Searching backup with backup_id=%s",backup_id)
        self.open_connect(self.db,self.alias)
        loaded_backup=FullBackupCatalog.objects(backup_id=backup_id)
        if loaded_backup.count()>0:
            logger.debug("Backup %s found. Proceed deletion",backup_id)
            loaded_backup.first().delete()
            logger.debug("backup %s deleted",backup_id)
        else:
            logger.debug("Backup %s not found.Do nothing",backup_id)
        self.close_mongo_connect(self.alias)

    def delete_by_status(self,status:str,entity:Entity)->None:
        status=status
        entity=entity
        logger.debug("check if backup_id is provided")
        available_statues= set(item.value  for item in Status)
        if(status is None and status  not in available_statues) :
            raise TypeError("The status should be a string with values {} ",format(available_statues))
        if(entity is not None and  not isinstance(entity,Entity)) :
            raise TypeError("The status should be a string with value")

        self.open_connect(self.db,self.alias)
        if entity is None:
            entity=None
            logger.debug("Found %s %s backup for entity=%s", str(FullBackupCatalog.objects(status=status).count()),
                         status, entity)
            for document in FullBackupCatalog.objects(status=status):
                document.delete()
                logger.debug("Document related to backup %s deleted", document.backup_id)

        else:
            logger.debug ("searching for backup with status=%s and entity=%s ",status,entity)
            logger.debug("Found %s %s backup for entity=%s",str(FullBackupCatalog.objects(status=status,entity=entity).count()),status,entity)
            for document in FullBackupCatalog.objects(status=status,entity=entity):
                document.delete()
                logger.debug("Document related to backup %s deleted",document.backup_id)
        self.close_mongo_connect(self.alias)


    def insert(self,updated_catalog_object:FullBackupCatalog)->None:
        if updated_catalog_object is None:
            raise TypeError("Invalid argument provided for insert should not be None")
        if not isinstance(updated_catalog_object,FullBackupCatalog):
            raise TypeError("Invalid argument. The parameter should be an instance of class FullBackupCatalog")
        backup_id=updated_catalog_object.backup_id

        logger.debug("Start insert Full backup catalog with backup_id="+updated_catalog_object.backup_id)
        self.open_connect(self.db,self.alias)
        if(FullBackupCatalog.objects(backup_id=backup_id).count()==0):
            logger.debug("catalog with backup_id="+backup_id+"not found.")
            logger.debug("start saving catalog with backup_id="+backup_id+".")
            updated_catalog_object.save()
            logger.debug("catalog with backup_id="+backup_id+" correctly saved")
        else:
            logger.debug("Catalog with backup_id="+backup_id+"already exist. Start updating")
            backup_catalog_loaded=FullBackupCatalog.objects(backup_id=backup_id).update_one(
                set__root=updated_catalog_object.root,
                set__files=updated_catalog_object.files,
                set__entity=updated_catalog_object.entity,
                set__host=updated_catalog_object.host,
                set__source_type=updated_catalog_object.source_type,
                set__zip_path=updated_catalog_object.zip_path,
                set__hash_zip=updated_catalog_object.hash_zip,
                set__start_at=updated_catalog_object.start_at,
                set__end_at=updated_catalog_object.end_at,
                set__expiration_time=updated_catalog_object.expiration_time,
                set__status=updated_catalog_object.status,
                set__backup_type=updated_catalog_object.backup_type
            )
        self.close_mongo_connect(self.alias)



    def getOnlyExpired(self)->List:
        self.open_connect(self.db,self.alias)
        res=list()
        for iterable_object in FullBackupCatalog.objects(expiration_time__lte=datetime.datetime.now()):
            res.append(iterable_object)
        self.close_mongo_connect(self.alias)
        return res

    def getValidStatus(self):
        #return only backup for which status are ACTIVE or IN_PROGRESS
        self.open_connect(self.db,self.alias)
        res=list()
        for iterable_object in FullBackupCatalog.objects(status__in=[Status.ACTIVE.value,Status.IN_PROGRESS.value]):
            res.append(iterable_object)
        self.close_mongo_connect(self.alias)
        return res

    def getInvalidStatus(self):
        # return only backup for which status are different from the status used in method getValidStatus
        self.open_connect(self.db,self.alias)
        res=list()
        for iterable_object in FullBackupCatalog.objects(status__nin=[Status.ACTIVE.value,Status.IN_PROGRESS.value]):
            res.append(iterable_object)
        self.close_mongo_connect(self.alias)
        return res





    def create(self,item: T)->None:
        pass

