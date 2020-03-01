from google.appengine.ext import ndb

class Taskboard(ndb.Model):
	name = ndb.StringProperty()
	created_by = ndb.UserProperty()
	users = ndb.UserProperty(repeated=true)
	tasks = ndb.StructuredProperty(Task, repeated=true)
	
class Task(ndb.Model):
	taskboard = ndb.KeyProperty(kind=Taskboard)
	task = ndb.StringProperty()
	assigned_user = ndb.UserProperty()
	completed = ndb.BooleanProperty()