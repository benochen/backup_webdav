from mongoengine import *
from models.catalog.AbstractCatalog import AbstractCatalog
import json
class FullBackupCatalog(AbstractCatalog):
    meta = {'collection': 'full_backup_catalog'}
    backup_type=StringField(default="FULL")

    def toJson(self):
        fields={
            'backup_id':self.backup_id,
            'host':self.host,
            'source_type':self.source_type,
            'entity':self.entity,
            'zip_size':self.zip_size,
            'zip_path':self.zip_path,
            'hash_zip':self.hash_zip,
            'start_at':self.start_at,
            'end_at':self.end_at,
            'expiration_time':self.expiration_time,
            'file':self.files,
            'status':self.status,
            'backup_type':self.backup_type
            }
        return fields


    def setStatus(self,status):
        self.status=status

