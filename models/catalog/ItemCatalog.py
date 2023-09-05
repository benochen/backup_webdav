from mongoengine import *
from models.catalog.FileState import FileState
from models.entities.Entity import Entity
class ItemCatalog(EmbeddedDocument):


    path=StringField(required=True)
    hash_file=StringField(required=True)
    type=StringField(required=True)
    file_state=EnumField(FileState)
    file_size=IntField(required=True)


