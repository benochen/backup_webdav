from models.users.group import Group
from models.users.users import User
from models.entities.Entity import Entity
from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.ItemCatalog import ItemCatalog
from datetime import datetime
from mongoengine import *

connect('backup_webdav')


s2 = Entity(name="MDC",read_group=[])
s2.save()
