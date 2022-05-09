from mongoengine import *
from models.entities.Entity import Entity
from models.catalog.Status import Status
import TypeBackup
import AbstractCatalog

class FullBackupCatalog(AbstractCatalog):
    backup_type=StringField(TypeBackup.)
    def __init__(self):
        super.__init__()