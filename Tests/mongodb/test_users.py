from models.users.group import Group
from models.users.users import User
from models.entities.Entity import Entity
from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.ItemCatalog import ItemCatalog
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
file_1 = ItemCatalog(host="http://www.test.com",
                           entity=s2,
                           root="[MDC]",
                           size=500,
                           store_zip="12345654ezfsqdsd.zip",
                           hash_zip="eaef345532abcd45897",
                           start_at=date,
                           end_at=date,
                           expiration_time=date,
                           status="ACTIVE",
                           type="FULL",
                           path="/etc/password",
                          file_size=40,
                           hash_file="eaef345532abcd45897")


file_1 = ItemCatalog(host="http://www.test.com",
                         entity=s2,
                         root="[MDC]",
                         size=500,
                         store_zip="12345654ezfsqdsd.zip",
                         hash_zip="eaef345532abcd45897",
                         start_at=date,
                         end_at=date,
                         expiration_time=date,
                         status="ACTIVE",
                         type="FULL",
                         path="/etc/password"+str("toto"),
                         file_size=40+1,
                         hash_file="eaef345532abcd45897"+str("toto"))

print("load all catalog of item which is FULL")
my_Objects=ItemCatalog.objects(type="FULL",status="ACTIVE")
print(" End load all catalog of item which is FULL")

for x in my_Objects:
    print(x.path)
    print(x.hash)

ItemCatalog.objects(type="FULL",status="PROOGRESS").update(status="ACTIVE")