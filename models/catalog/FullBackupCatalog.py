from mongoengine import *
from models.catalog.AbstractCatalog import AbstractCatalog
class FullBackupCatalog(AbstractCatalog):
    backup_type=StringField(default="FULL")
