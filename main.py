import webapp2
import jinja2
import os
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from models import User, Taskboard
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
		response_data = {}
		request = self.request.POST	
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		taskboard_key = ndb.Key(Taskboard, taskboard_name)
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
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		taskboard_key = ndb.Key(Taskboard, taskboard_name)
		taskboard_exist = taskboard_key.get()
		taskboard.key = ndb.Key(Taskboard, taskboard_name)
		taskboard.taskboard = taskboard_name
		taskboard.created_by = users.get_current_user()
		taskboard.created_date = datetime.now()
		taskboard.put()
		user_email = users.get_current_user().email()
		user_key = ndb.Key(User, user_email)
		user = user_key.get()
		user.taskboards.append(taskboard_name)
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
			welcome_message = 'hi, ' + user.email()
			logout_url = users.create_logout_url(self.request.uri)
			template_values = {
				'welcome_message':welcome_message,
				'logout_url':logout_url,
				'taskboard':taskboard
			}
			template = JINJA_ENVIROMENT.get_template('taskboard-details.html')
			self.response.write(template.render(template_values))
			
	def post(self):
		request = self.request.POST	
		taskboard_name = request['taskboard'].strip().capitalize()
		taskboard = Taskboard()
		taskboard_key = ndb.Key(Taskboard, taskboard_name)
		taskboard_exist = taskboard_key.get()
		taskboard.key = ndb.Key(Taskboard, taskboard_name)
		taskboard.taskboard = taskboard_name
		taskboard.created_by = users.get_current_user()
		taskboard.created_date = datetime.now()
		taskboard.put()
		user_email = users.get_current_user().email()
		user_key = ndb.Key(User, user_email)
		user = user_key.get()
		user.taskboards.append(taskboard_name)
		user.put()
		self.redirect('/taskboard')
		

JINJA_ENVIROMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True
)

app = webapp2.WSGIApplication([
	('/', LoginPage),
	('/get_taskboard', GetTaskboard),
	('/taskboard', TaskboardPage),
	('/taskboard_details/(.*)', TaskboardDetailsPage),
], debug = True)