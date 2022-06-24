from mongoengine import *
from models.entities.Entity import Entity
from models.catalog.AbstractCatalog import AbstractCatalog
class ItemCatalog(AbstractCatalog):


    path=StringField(required=True)
    hash_file=StringField(required=True)
    type=StringField(required=True)
    file_size=IntField(required=True)



