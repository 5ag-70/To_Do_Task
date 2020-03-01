from google.appengine.ext import ndb

class User(ndb.Model):
	user = ndb.UserProperty()
	taskboards = ndb.StringProperty(repeated=True)

class Taskboard(ndb.Model):
	taskboard = ndb.StringProperty()
	created_by = ndb.UserProperty()
	created_date = ndb.DateTimeProperty()
	
class Task(ndb.Model):
	task = ndb.StringProperty()
	assigned_user = ndb.UserProperty()
	completed = ndb.BooleanProperty()