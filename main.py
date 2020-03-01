import webapp2
import jinja2
import os
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from models import User, Taskboard, Task
from datetime import datetime

class LoginPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			url_string = 'login'
			template_values = {
				'url':url,
				'url_string':url_string
			}
			template = JINJA_ENVIROMENT.get_template('login.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect('/taskboard')
	
class GetTaskboard(webapp2.RequestHandler):
	def post(self):
		user_email = users.get_current_user().email()
		response_data = {}
		request = self.request.POST	
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		taskboard_key = ndb.Key(Taskboard, user_email+':'+taskboard_name)
		taskboard_exist = taskboard_key.get()
		if not taskboard_exist:
			response_data["taskboard_exist"] = False
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
			
		else:
			response_data["taskboard_exist"] = True
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
	
class TaskboardPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('login.html')
			self.response.write(template.render(template_values))
		else:
			new_user_key = ndb.Key(User, user.email())
			new_user = new_user_key.get()
			if new_user is None:
				new_user = User()
				new_user.key = new_user_key
				new_user.user = user
				new_user.put()
			welcome_message = 'hi, ' + user.email()
			logout_url = users.create_logout_url(self.request.uri)
			taskboards = new_user_key.get().taskboards
			template_values = {
				'welcome_message':welcome_message,
				'logout_url':logout_url,
				'taskboards':taskboards
			}
			template = JINJA_ENVIROMENT.get_template('taskboard.html')
			self.response.write(template.render(template_values))
			
	def post(self):
		request = self.request.POST	
		user_email = users.get_current_user().email()
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		taskboard_key = ndb.Key(Taskboard, taskboard_name)
		taskboard_exist = taskboard_key.get()
		taskboard.key = ndb.Key(Taskboard, user_email+':'+taskboard_name)
		taskboard.taskboard = taskboard_name
		taskboard.created_by = users.get_current_user()
		taskboard.created_date = datetime.now()
		taskboard.put()
		user_key = ndb.Key(User, user_email)
		user = user_key.get()
		user.taskboards.append(user_email+':'+taskboard_name)
		user.put()
		self.redirect('/taskboard')
		

class TaskboardDetailsPage(webapp2.RequestHandler):
	def get(self, key):
		self.response.headers['Content-Type'] = 'text/html'
		url = ''
		url_string = ''
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('login.html')
			self.response.write(template.render(template_values))
		else:
			taskboard_key = ndb.Key(Taskboard, key)
			taskboard = taskboard_key.get()
			tasks = []
			task_keys = taskboard.tasks
			for task_key in task_keys:
				ndb_task_key = ndb.Key(Task, task_key)
				task = ndb_task_key.get()
				tasks.append(task)
			welcome_message = 'hi, ' + user.email()
			logout_url = users.create_logout_url(self.request.uri)
			all_users = User.query().fetch()
			template_values = {
				'welcome_message':welcome_message,
				'logout_url':logout_url,
				'taskboard':taskboard,
				'key':key,
				'tasks':tasks,
				'all_users':all_users,
			}
			template = JINJA_ENVIROMENT.get_template('taskboard-details.html')
			self.response.write(template.render(template_values))
			
	def post(self):
		request = self.request.POST	
		response_data = {}
		type = request['type']
		taskboard_key = request['taskboard_key']
		try:
			import simplejson as json
		except(ImportError,):
			import json
		if(type == 'invite_user'):
			data = request['data']
			userdata = json.loads(data)
			for key in userdata:
				user_key = key.split(';')[1]
				ndb_taskboard_key = ndb.Key(Taskboard, taskboard_key)
				taskboard = ndb_taskboard_key.get()
				ndb_user_key = ndb.Key(User, user_key)
				userobj = ndb_user_key.get()
				taskboard.users.append(user_key)
				taskboard.put()
				userobj.taskboards.append(taskboard_key)
				userobj.put()
				self.response.headers['Content-Type'] = 'application/json'
				return self.response.out.write(json.dumps(response_data))
		elif(type == 'create'):
			task_name = request['task']
			due_date = request['due_date']
			task_key = taskboard_key+":"+task_name
			ndb_taskboard_key = ndb.Key(Taskboard, taskboard_key)
			taskboard = ndb_taskboard_key.get()
			if task_key in taskboard.tasks:
				response_data["task_exist"] = True
			else:
				response_data["task_exist"] = False
				taskboard.tasks.append(task_key)
				taskboard.put()
				task = Task()
				ndb_task_key = ndb.Key(Task, task_key)
				task.key = ndb_task_key
				task.title = task_name
				user = users.get_current_user()
				task.created_by = user
				task.due_date = due_date
				task.completed = False
				task.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'completed'):
			task_key = request['task_key']
			response_data["task_completed"] = True
			ndb_task_key = ndb.Key(Task, task_key)
			task = ndb_task_key.get()
			task.completed = True
			task.completion_date = datetime.now()
			task.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'edit'):
			task_key = request['task_key']
			response_data["task_completed"] = True
			ndb_task_key = ndb.Key(Task, task_key)
			task = ndb_task_key.get()
			task.completed = True
			task.completion_date = datetime.now()
			task.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'delete'):
			task_key = request['task_key']
			response_data["task_deleted"] = True
			ndb_task_key = ndb.Key(Task, task_key)
			ndb_task_key.delete()
			ndb_taskboard_key = ndb.Key(Taskboard, taskboard_key)
			taskboard = ndb_taskboard_key.get()
			tasks = taskboard.tasks
			tasks.remove(task_key)
			taskboard.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))

JINJA_ENVIROMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True
)

app = webapp2.WSGIApplication([
	('/', LoginPage),
	('/get_taskboard', GetTaskboard),
	('/taskboard', TaskboardPage),
	('/taskboard_details', TaskboardDetailsPage),
	('/taskboard_details/(.*)', TaskboardDetailsPage),
], debug = True)