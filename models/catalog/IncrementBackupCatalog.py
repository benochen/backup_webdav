from mongoengine import *
from models.catalog.AbstractCatalog import AbstractCatalog
class IncrementBackupCatalog(AbstractCatalog):
    backup_type=StringField(default="INCREMENT")
