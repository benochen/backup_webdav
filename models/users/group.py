from mongoengine import Document,StringField,ListField,EmbeddedDocumentField,ReferenceField
from models.users.users import User

class Group(Document):
    name = StringField(required=True)
    members= ListField(ReferenceField(User))