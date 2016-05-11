from locust import HttpLocust, TaskSet, task
import random 
import pdb
import time

num_users = 100
Receivers = []
Senders = []

# all users have <number> as username
# and pass<number> as password

class Receiver_dialogue(TaskSet):

	@task(1)
	def close_dialogue(self):
		# pdb.set_trace()
		self.client.delete('dialogues/{0}'.format(self.current_dialogue), name="DELETE /dialogues/<id>/" ) 
		self.interrupt()

	@task(10)
	def poll_message(self):
		# pdb.set_trace()
		with self.client.get('dialogues/{0}/messages'.format(self.client.current_dialogue), catch_response = True, name = "GET /dialogues/<int>/messages") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.json()
			else: resp.failure("unexpected error 2")			

	def on_start(self):
		global Senders
		global num_users

		from_id = 0

		for i in range(100):
			try:
				from_id = Senders.pop()
			except Exception:
				time.sleep(5)
			else:
				break()
		self.client.current_from_id = str(from_id)
		# creating dialogue
		with self.client.put('dialogues/{0}'.format(from_id), cookies = {'id': str(self.id) }, catch_response=True, name="PUT /dialogues/<id>/" ) as resp:
			if resp.status_code == 404:
				print "chose invalid user"
				resp.success()
				self.interrupt()
			if resp.status_code == 409:
				print "logging into an exsting dialogue"
				resp.success()
	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			resp.success()
	 		else: resp.failure("unexpected error 3")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(from_id), json={'id': str(self.client.id) } catch_response=True, name="POST /dialogues/<id>/") as resp:
	 		if resp.status_code == 409:
	 			print "Opened exsting dialogue"
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				if resp.text:
	 					print resp.json()
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")


class ReceiverTaskSet(TaskSet):

	tasks = {Receiver_dialogue: 10}


	def on_start(self):
	"""initializing a user and assignng it a password"""
		global num_users
		global Receivers

		#preparing a user data
		self.client.username = str(random.randint(0,num_users/2)+num_users/2)			
		password = 'pass'+ str(self.client.username)
 
		data = {"username": self.client.username,
				"password": password }

		with self.client.post('register', json = data, catch_response=True) as resp:
			if resp.status_code == 409:
				resp.success()
				with self.client.post('login', json = data, catch_response=True) as resp2:
				if resp2.status_code == 404:
					resp2.failure('password issue')
					self.interrupt()
				else: 
					resp2.success()
					self.client.id = resp2.json()['id']
					Receivers.append(self.client.id)

			else: 
				resp.success()
				self.client.id = resp.json()['id']
				Receivers.append(self.client.id)

class Sender_dialogue(TaskSet):

	@task(1)
	def close_dialogue(self):
		# pdb.set_trace()
		self.client.delete('dialogues/{0}'.format(self.client.current_dialogue), name="DELETE /dialogues/<id>/" ) 
		self.interrupt()

	@task(10)
	def send_message(self):
		# pdb.set_trace()
		with self.client.post('dialogues/{0}/messages_text'.format(self.current_dialogue) , json = {'datetime': time.strftime('%Y-%m-%d %H:%M:%S'), 'from_id': str(self.clientid), 'body': 'aha'}, catch_response=True, name="dialogues/<id>/messages_text/") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.json()
			else: resp.failure("unexpected error 0")			

	def on_start(self):
		global Receivers
		global num_users

		to_id = 0

		for i in range(100):
			try:
				to_id = Receivers.pop()
			except Exception:
				time.sleep(5)
			else:
				break()
		self.client.current_to_id = str(to_id)
		# creating dialogue
		with self.client.put('dialogues/{0}'.format(to_id), cookies = {'id': str(self.id) }, catch_response=True, name="PUT /dialogues/<id>/" ) as resp:
			if resp.status_code == 404:
				print "chose invalid user"
				resp.success()
				self.interrupt()
			if resp.status_code == 409:
				print "logging into an exsting dialogue"
				resp.success()
	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			resp.success()
	 		else: resp.failure("unexpected error 3")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(to_id), json={'id': str(self.client.id) } catch_response=True, name="POST /dialogues/<id>/") as resp:
	 		if resp.status_code == 409:
	 			print "Opened exsting dialogue"
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				if resp.text:
	 					print resp.json()
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")


class SenderTaskSet(TaskSet):
	tasks = {Sender_dialogue: 10}

	@task(2)
	def get_userpage(self):
		# pdb.set_trace()
		self.client.get('users/{0}'.format(self.client.id]), name='/users/<user_id>')
	
	@task(5) 
	def search_user(self):
		# pdb.set_trace()
		with self.client.post('users/search', json={'username': random.randint(0,num_users/2) }, catch_response=True) as resp:
			if resp.status_code == 404:
				resp.success()
			else: 
				if resp.status_code == 200:
					resp.success()
				else: resp.failure('Search didn`t work') 

	def on_start(self):
		"""initializing a user and assignng it a password"""

		global num_users
		global Senders

		#preparing a user data
		self.client.username = str(random.randint(0,num_users))
		password = 'pass'+ str(self.client.username)
 
		data = {"username": self.client.username,
				"password": password }

		with self.client.post('register', json = data, catch_response=True) as resp:
			if resp.status_code == 409:
				resp.success()
				with self.client.post('login', json = data, catch_response=True) as resp2:
				if resp2.status_code == 404:
					resp2.failure('password issue')
					self.interrupt()
				else: 
					resp2.success()
					self.client.id = resp2.json()['id']
					Senders.append(self.client.id)

			else: 
				resp.success()
				self.client.id = resp.json()['id']
				Senders.append(self.client.id)

class Sender(HttpLocust):
	"""the one who promised to call"""
	# weight = 3 #this attribute "how often this type of user calls"
	task_set = SenderTaskSet
	min_wait = 50
	max_wait = 1500

class Receiver(HttpLocust):
	"""the girl who waited"""
	task_set = WaiterTaskSet
	min_wait = 5000
	max_wait = 150000000