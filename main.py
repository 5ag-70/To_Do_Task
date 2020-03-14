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
		taskboard_key = ndb.Key(Taskboard, taskboard_name+user_email)
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
			taskboard_keys = new_user_key.get().taskboards
			taskboards = ndb.get_multi(taskboard_keys)
			template_values = {
				'welcome_message':welcome_message,
				'logout_url':logout_url,
				'taskboards':taskboards,
			}
			template = JINJA_ENVIROMENT.get_template('taskboard.html')
			self.response.write(template.render(template_values))
			
	def post(self):
		request = self.request.POST	
		user_email = users.get_current_user().email()
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		ndb_taskboard_key = ndb.Key(Taskboard, taskboard_name+user_email)
		taskboard_exist = ndb_taskboard_key.get()
		taskboard.key = ndb_taskboard_key
		taskboard.title = taskboard_name
		taskboard.created_by = users.get_current_user()
		taskboard.users.append(users.get_current_user())
		taskboard.created_date = datetime.now()
		taskboard.put()
		user_key = ndb.Key(User, user_email)
		user = user_key.get()
		user.taskboards.append(ndb_taskboard_key)
		user.put()
		self.redirect('/taskboard')
		

class TaskboardDetailsPage(webapp2.RequestHandler):
	def get(self, taskboard_key):
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
			ndb_taskboard_key = ndb.Key(urlsafe=taskboard_key)
			taskboard = ndb_taskboard_key.get()
			task_keys = taskboard.tasks
			tasks = ndb.get_multi(task_keys)
			total_tasks = 0
			completed_tasks = 0
			active_tasks = 0
			completed_today_tasks = 0
			for task in tasks:
				total_tasks+=1
				if task.completed:
					completed_tasks+=1
				if not task.completed:
					active_tasks+=1
				if task.completion_date == datetime.date(datetime.now()):
					completed_today_tasks+=1
			total_tasksboard_users = len(taskboard.users)
			welcome_message = 'hi, ' + user.email()
			logout_url = users.create_logout_url(self.request.uri)
			all_users = User.query().fetch()
			template_values = {
				'welcome_message':welcome_message,
				'logout_url':logout_url,
				'taskboard':taskboard,
				'tasks':tasks,
				'total_tasks':total_tasks,
				'completed_tasks':completed_tasks,
				'active_tasks':active_tasks,
				'completed_today_tasks':completed_today_tasks,
				'current_user':user,
				'all_users':all_users,
				'total_tasksboard_users':total_tasksboard_users,
			}
			template = JINJA_ENVIROMENT.get_template('taskboard-details.html')
			self.response.write(template.render(template_values))
			
	def post(self):
		request = self.request.POST	
		response_data = {}
		type = request['type']
		taskboard_key = request['taskboard_key']
		ndb_taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = ndb_taskboard_key.get()
		try:
			import simplejson as json
		except(ImportError,):
			import json
			
		if(type == 'invite_user'):
			data = request['data']
			userdata = json.loads(data)
			for user_key in userdata:
				ndb_user_key = ndb.Key(User, user_key)
				userobj = ndb_user_key.get()
				taskboard.users.append(userobj.user)
				taskboard.put()
				userobj.taskboards.append(ndb_taskboard_key)
				userobj.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'create'):
			task_name = request['task']
			due_date = request['due_date']
			assigned_to_email = request['assigned_to']
			taskboard_name = taskboard.title
			task_key = taskboard_name+task_name
			ndb_task_key = ndb.Key(Task, task_key)
			if ndb_task_key in taskboard.tasks:
				response_data["task_exist"] = True
			else:
				response_data["task_exist"] = False
				taskboard.tasks.append(ndb_task_key)
				taskboard.put()
				task = Task()
				task.key = ndb_task_key
				task.title = task_name
				ndb_user_key = ndb.Key(User, assigned_to_email)
				assigned_to = ndb_user_key.get()
				task.assigned_to = assigned_to.user
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
			ndb_task_key = ndb.Key(urlsafe=task_key)
			task = ndb_task_key.get()
			task.completed = True
			task.completion_date = datetime.now()
			task.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'edit'):
			task_key = request['task_key']
			task_name = request['task']
			due_date = request['due_date']
			assigned_to_key = request['assigned_to']
			ndb_task_key = ndb.Key(urlsafe=task_key)
			task = ndb_task_key.get()
			task.title = task_name
			ndb_assigned_to_key = ndb.Key(User, assigned_to_key)
			assigned_to = ndb_assigned_to_key.get()
			task.assigned_to = assigned_to.user
			task.due_date = due_date
			task.un_assigned = False
			task_key = taskboard.title+task_name
			new_ndb_task_key = ndb.Key(Task, task_key)
			task.key = new_ndb_task_key
			index = taskboard.tasks.index(ndb_task_key)
			ndb_task_key.delete()
			task.put()
			taskboard.tasks[index] = new_ndb_task_key
			taskboard.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'delete'):
			task_key = request['task_key']
			response_data["task_deleted"] = True
			ndb_task_key = ndb.Key(urlsafe=task_key)
			ndb_task_key.delete()
			tasks = taskboard.tasks
			tasks.remove(ndb_task_key)
			taskboard.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'change_title'):
			title = request['title']
			taskboard.title = title
			taskboard.put()
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'remove_user'):
			user_key = request['user_key']
			current_user_email = request['current_user_email']
			ndb_user_key = ndb.Key(User, user_key)
			user = ndb_user_key.get()
			user.taskboards.remove(ndb_taskboard_key)
			user.put()
			users_of_taskboard = taskboard.users
			users_of_taskboard.remove(user.user)
			taskboard.put()
			ndb_task_keys = taskboard.tasks
			tasks = ndb.get_multi(ndb_task_keys)
			for task in tasks:
				if task.assigned_to == user.user:
					task.assigned_to = None
					task.un_assigned = True
					task.put()
			if(current_user_email == user_key):
				response_data["goback"] = True
			else:
				response_data["goback"] = False
			self.response.headers['Content-Type'] = 'application/json'
			return self.response.out.write(json.dumps(response_data))
		elif(type == 'delete_taskboard'):
			all_users = User.query().fetch()
			for user in all_users:
				taskboards = user.taskboards
				if ndb_taskboard_key in taskboards:
					taskboards.remove(ndb_taskboard_key)
				user.put()
			ndb_taskboard_key.delete()
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