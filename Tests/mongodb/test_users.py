from models.users.group import Group
from models.users.users import User
from models.entities.Entity import Entity
from models.catalog.Status import Status
from models.catalog.FileState import FileState
from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.ItemCatalog import ItemCatalog
from datetime import date
from mongoengine import *

conn=connect('backup_webdav')
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

s1= Entity(name="chenal.org",read_group=[g1])
s1.save()

file_1=ItemCatalog(path="/home/myuser/plan.txt",
                   hash_file="12dfeaa234567af",
                   type='file',
                   file_state=FileState.ADDED,
                   file_size=12654
)

file_2=ItemCatalog(path="/home/myuser/Image/plan.jpg",
                   hash_file="22dfaaa234567ac",
                   type='file',
                   file_state=FileState.ADDED,
                   file_size=12654
)



fullback_1=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s2,
                             root="MyExample",
                             backup_id="111-2222-333-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/1111-2222-333-444-20220119.zip",
                             hash_zip="NULL",
                             start_at=date(2023,1,19).ctime(),
                             end_at=date(2023,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )

if(FullBackupCatalog.objects(backup_id="111-2222-333-4444").count()==0):
    fullback_1.save()

doc=FullBackupCatalog.objects(backup_id="111-2222-333-4444")
for e in doc:
    print(e.status)

fullback_2=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s2,
                             root="MyExample",
                             backup_id="222-3333-4444-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/222-3333-4444-4444-20220219.zip",
                             hash_zip="NULL",
                             start_at=date(2022,1,19).ctime(),
                             end_at=date(2022,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )

if(FullBackupCatalog.objects(backup_id="222-3333-4444-4444").count()==0):
    fullback_2.save()

doc=FullBackupCatalog.objects(backup_id="222-3333-4444-4444")
for e in doc:
    print(e.status)

fullback_2.status=Status.EXPIRED

FullBackupCatalog.objects(backup_id="222-3333-4444-4444").update_one(push__files=file_2)


fullback_3=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s1,
                             root="MyExample",
                             backup_id="bbb-2222-333-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/1111-2222-333-444-20220119.zip",
                             hash_zip="NULL",
                             start_at=date(2023,1,19).ctime(),
                             end_at=date(2023,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )


fullback_4=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s1,
                             root="MyExample",
                             backup_id="aaa-2222-333-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/1111-2222-333-444-20220119.zip",
                             hash_zip="NULL",
                             start_at=date(2023,1,19).ctime(),
                             end_at=date(2023,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )


fullback_5=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s1,
                             root="MyExample",
                             backup_id="ccc-2222-333-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/1111-2222-333-444-20220119.zip",
                             hash_zip="NULL",
                             start_at=date(2023,1,19).ctime(),
                             end_at=date(2023,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )


fullback_3.save()
fullback_4.save()
fullback_5.save()