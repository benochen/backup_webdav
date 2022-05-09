from mongoengine import *

class User(Document):
   username = StringField(required=True)
   last_name = StringField(max_length=50)
   given_name = StringField()
   def _init__(self,username, last_name,given_name):
      self.username=username,
      self.last_name=last_name
      self.given_name=given_name


