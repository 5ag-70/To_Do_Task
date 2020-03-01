from google.appengine.ext import ndb

class User(ndb.Model):
	user = ndb.UserProperty()
	taskboards = ndb.StringProperty(repeated=True)

class Taskboard(ndb.Model):
	taskboard = ndb.StringProperty()
	created_by = ndb.UserProperty()
	created_date = ndb.DateTimeProperty()
	users = ndb.StringProperty(repeated=True)
	tasks = ndb.StringProperty(repeated=True)
	
class Task(ndb.Model):
	title = ndb.StringProperty()
	assigned_to = ndb.UserProperty()
	created_by = ndb.UserProperty()
	due_date = ndb.StringProperty()
	completed = ndb.BooleanProperty()
	un_assigned = ndb.BooleanProperty()
	completion_date = ndb.DateProperty()