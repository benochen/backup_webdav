from mongoengine import *
from models.entities.Entity import Entity
from models.catalog.Status import Status
from models.catalog.TypeBackup import SourceBackup

class AbstractCatalog(Document):
    meta = {
        'abstract' : True,
        'allow_inheritance': True
    }
    host = StringField(required=True)
    source_type=EnumField(SourceBackup)
    entity=ReferenceField(Entity)
    root=StringField(require=True)
    size=IntField(required=True)
    store_zip=StringField(required=True)
    hash_zip=StringField(required=True)
    creation_time=DateTimeField(required=True)
    expiration_time=DateTimeField(required=True)
    status=EnumField(Status)
