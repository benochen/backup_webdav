from mongoengine import *
from models.users.users import User
from models.users.group import Group


class Entity(Document):
    name = StringField(required=True)

    read_group = ListField(ReferenceField(Group)
                           )

def _init__(self,name,owner):
    self.name=name
    self.owner=owner