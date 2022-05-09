from mongoengine import *
from models.entities.Entity import Entity
from models.catalog.Status import Status
import TypeBackup

class AbstractCatalog(Document):
    host = StringField(required=True)
    source_type=EnumField(TypeBackup)
    entity=ReferenceField(Entity)
    root=StringField(require=True)
    size=IntField(required=True)
    store_zip=StringField(required=True)
    hash_zip=StringField(required=True)
    creation_time=DateTimeField(required=True)
    expiration_time=DateTimeField(required=True)
    status=EnumField(Status)
