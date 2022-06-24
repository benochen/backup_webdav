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
    root=StringField (require=True)
    backup_id=StringField(required=True)
    zip_size=IntField(required=True)
    zip_path=StringField(required=True)
    hash_zip=StringField(required=True)
    start_at=DateTimeField(required=True)
    end_at = DateTimeField(required=True)
    expiration_time=DateTimeField(required=True)
    status=EnumField(Status)
