from locust import HttpLocust, TaskSet, task
import random 
import pdb
import time

num_users = 100
users = {}


# all users have <number> for username
# and pass<number> for password

class dialogue(TaskSet):

	@task(1)
	def close_dialogue(self):
		# pdb.set_trace()
		self.client.delete('dialogues/{0}/'.format(self.client.cookies['current_dialogue']), name="DELETE /dialogues/<id>/" ) 
		self.interrupt()

	@task(10)
	def send_message(self):
		# pdb.set_trace()
		with self.client.post('dialogues/{0}/messages_text/'.format(self.client.cookies['current_dialogue']) , json = {'datetime': time.strftime('%Y-%m-%d %H:%M:%S'), 'from_id': self.client.cookies['id'], 'body': 'aha'}, catch_response=True, name="dialogues/<id>/messages_text/") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.json()
			else: resp.failure("unexpected error 0")

	@task(10)
	def poll_message(self):
		# pdb.set_trace()
		with self.client.get('dialogues/{0}/messages/'.format(self.client.cookies['current_dialogue']), catch_response = True, name = "GET /dialogues/<int>/messages") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.json()
			else: resp.failure("unexpected error 2")			

	def on_start(self):
		global users
		# pdb.set_trace()
		to_id = random.choice(users.keys())
		# creating dialogue
		with self.client.put('dialogues/{0}/'.format(to_id), cookies = {'id': str(self.client.cookies['id']) }, catch_response=True, name="PUT /dialogues/<id>/" ) as resp:
			if resp.status_code == 404:
				print "chose invalid user"
				resp.success()
			if resp.status_code == 409:
				print "logging into an exsting dialogue"
				resp.success()
	 		if resp.status_code == 200:
	 			self.client.cookies['current_dialogue'] = str(resp.json()['dialogue_id'])
	 			resp.success()
	 			resp.success
	 		else: resp.failure("unexpected error 3")

	 	#opening dialogue
	 	with self.client.get('dialogues/{0}/'.format(to_id) , catch_response=True, name="GET /dialogues/<id>/") as resp:
	 		if resp.status_code == 409:
	 			print "Opened exsting dialogue"
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				if resp.text:
	 					print resp.json()
	 				resp.success()
	 			else: resp.failure("unexpected error 1")




class MyTaskSet(TaskSet):
	tasks = {dialogue: 10}

	@task(1)
	def get_userpage(self):
		# pdb.set_trace()
		self.client.get('users/{0}/'.format(self.client.cookies['id']), name='/users/<user_id>/')
	
	@task(5) 
	def search_user(self):
		# pdb.set_trace()
		with self.client.post('users/search/', json={'username': random.randint(0,num_users) }, catch_response=True) as resp:
			if resp.status_code == 404:
				print "searched for inexisting user"
				resp.success()
			else: 
				if resp.status_code == 200:
					resp.success()
				else: resp.failure('Search didn`t work') 

	def on_start(self):
		# initializing a user and assignng it a password
		# pdb.set_trace()
		global num_users
		global users
		self.client.cookies['username'] = str(random.randint(0,num_users))
		self.client.cookies['password'] = "pass" + self.client.cookies['username']
 
		#preparing a login requset
		data = {"username": self.client.cookies['username'],
				"password": self.client.cookies['password']}
		with self.client.post('register/', json = data, catch_response=True) as resp:
			if resp.status_code == 409:
				resp.success()
				resp2 = self.client.post('login/', json = data)
				if resp2.status_code == 404: print "Wrong password"
				else: self.client.cookies['id'] = resp2.json()['id']

			else: self.client.cookies['id'] = resp.json()['id']

		global users
		users[self.client.cookies['id']] = self.client.cookies['password']

		print "user \"{0}\" logged in correctly with password \"{1}\"".format(self.client.cookies['username'], self.client.cookies['password'])

class WebUserLocust(HttpLocust):
	# weight = 3 #this attribute "how often this type of user calls"
	task_set = MyTaskSet #set taskset which defines user behavior
	min_wait = 5000
	max_wait = 15000