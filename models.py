from google.appengine.ext import ndb

class User(ndb.Model):
	user = ndb.UserProperty()
	taskboards = ndb.KeyProperty(kind='Taskboard', repeated=True)

class Taskboard(ndb.Model):
	title = ndb.StringProperty()
	created_by = ndb.UserProperty()
	created_date = ndb.DateTimeProperty()
	users = ndb.UserProperty(repeated=True)
	tasks = ndb.KeyProperty(kind='Task', repeated=True)
	
class Task(ndb.Model):
	title = ndb.StringProperty()
	assigned_to = ndb.UserProperty()
	created_by = ndb.UserProperty()
	due_date = ndb.StringProperty()
	completed = ndb.BooleanProperty()
	un_assigned = ndb.BooleanProperty()
	completion_date = ndb.DateProperty()