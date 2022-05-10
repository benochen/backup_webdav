
from models.users.group import Group
from models.users.users import User
from models.entities.Entity import Entity
from models.catalog.FullBackupCatalog import FullBackupCatalog
from datetime import datetime
from mongoengine import *

connect('backup_webdav')
u1=User(username='benochen', last_name='chen',given_name='beno')
u1.save()

u2=User(username='tioneb', last_name='tion',given_name='neb')
u2.save()
g1=Group(name="admin",members=[u1,u2])
g1.save()

groups = list()
groups.append(g1)

s2 = Entity(name="MDC",read_group=[g1])
s2.save()

date=datetime.now()
backup = FullBackupCatalog(host="http://www.test.com",entity=s2,root="[MDC]",size=500,store_zip="12345654ezfsqdsd.zip",hash_zip="eaef345532abcd45897",creation_time=date,expiration_time=date,status="ACTIVE")
backup.save()