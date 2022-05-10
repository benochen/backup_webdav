from mongoengine import *
from models.entities.Entity import Entity
from models.catalog.Status import Status
from models.catalog.TypeBackup import SourceBackup
from models.catalog.AbstractCatalog import AbstractCatalog
class FullBackupCatalog(AbstractCatalog):
    backup_type=StringField(default="FULL")
