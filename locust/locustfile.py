from locust import HttpLocust, TaskSet, task
import random 
import pdb
import time


#TODO: make self.client.id a string and skip converting it every time 

num_users = 100
Receivers = []
Senders = []

# all users have <number> as username
# and pass<number> as password


def random_word(file_name):
	file = open(file_name,'r')
	for line in file:
		for word in line.split(' '):
			yield word

word_gen = random_word('LoremIpsum')

class Receiver_dialogue(TaskSet):

	@task(1)
	def close_dialogue(self):
		# pdb.set_trace()
		self.interrupt()

	@task(20)
	def poll_message(self):
		with self.client.post('dialogues/{0}/get_messages'.format(self.client.current_dialogue), json={'id': str(self.client.id)} ,catch_response = True, name = "GET /dialogues/<int>/get_messages") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.text
			else: resp.failure("unexpected error in long poll")			

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
				break

		# creating dialogue
		with self.client.put('dialogues/{0}'.format(from_id), json = {'id': str(self.client.id) }, catch_response=True, name="PUT /dialogues/<id>" ) as resp:
			if resp.status_code == 404:
				resp.failure('somehow chose invalid user')
				self.interrupt()
			if resp.status_code == 409:
				print "logging into an exsting dialogue"
				self.client.current_dialogue = str(resp.json()['dialogue_id'])
				self.success()
	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			resp.success()
	 		else: resp.failure("Error initializing Receiver dialogue")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(self.client.current_dialogue), json={'id': str(self.client.id) }, catch_response=True, name="POST /dialogues/<id>") as resp:
	 		if resp.status_code == 409:
	 			print "Opened exsting dialogue"
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				if resp.text:
	 					print resp.text
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")
	 	
	 	self.poll_message()

class ReceiverTaskSet(TaskSet):

	tasks = {Receiver_dialogue: 10}


	def on_start(self):
		"""initializing a user and assignng it a password"""
		global num_users
		global Receivers

		#preparing a user data
		self.client.username = str(random.randint( 0,num_users/2 )+num_users/2 )			
		password = 'pass'+ self.client.username
 
		data = {"username": self.client.username,
				"password": password }

		with self.client.post('register', json = data, catch_response=True) as resp:
			if resp.status_code == 409:
				"""such user already exists"""
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
		self.interrupt()

	@task(20)
	def send_message(self):
		# pdb.set_trace()
		with self.client.post('dialogues/{0}/messages_text'.format(self.client.current_dialogue) , json = {'datetime': time.strftime('%Y-%m-%d %H:%M:%S'), 'from_id': str(self.client.id), 'body': word_gen.next(), 'id': str(self.client.id) }, catch_response=True, name="dialogues/<id>/messages_text") as resp:
			if resp.status_code == 200:
				resp.success()
				print resp.text
			else: resp.failure("Error sending a message")			

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
				break

		# creating dialogue
		with self.client.put('dialogues/{0}'.format(to_id), json = {'id': str(self.client.id) }, catch_response=True, name="PUT /dialogues/<id>" ) as resp:
			if resp.status_code == 404:
				print "chose invalid user"
				resp.success()
				self.interrupt()

			if resp.status_code == 409:
				# opened existing dialogue
				self.client.current_dialogue = str(resp.json()['dialogue_id'])
				resp.success()

	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			resp.success()

	 		else: resp.failure("Error creating Sender dialogue")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(self.client.current_dialogue), json={'id': str(self.client.id) }, catch_response=True, name="POST /dialogues/<id>") as resp:
	 		if resp.status_code == 409:
	 			# Opened existing dialogue
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				print resp.text
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")


class SenderTaskSet(TaskSet):
	tasks = {Sender_dialogue: 10}

	@task(2)
	def get_userpage(self):
		self.client.get('users/{0}'.format(self.client.id), name='/users/<user_id>')
	
	@task(5) 
	def search_user(self):
		# pdb.set_trace()
		with self.client.post('users/search', json={'username': random.randint(0,num_users) }, catch_response=True) as resp:
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
	weight = 1 #this attribute "how often this type of user calls"
	task_set = SenderTaskSet
	min_wait = 50
	max_wait = 1500

class Receiver(HttpLocust):
	"""the girl who waited"""
	weight = 1
	task_set = ReceiverTaskSet
	min_wait = 5000
	max_wait = 150000000