
from models.users.group import Group
from models.users.users import User
from models.entities.Entity import Entity
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

s2 = Entity(name="MDC")
s2.save()


g1.delete()