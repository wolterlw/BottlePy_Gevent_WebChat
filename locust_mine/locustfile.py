from locust import HttpLocust, TaskSet, task
import random 
import pdb
import time
from gevent import monkey
monkey.patch_all()

#TODO:
# make two user types
# recievers post long poll requests and senders respond to those requests using only dialogue id and generating random id numbers

num_users = 10000
Tails = []

# all users have <number> as username
# and pass<number> as password


def random_word(file_name):
	file = open(file_name,'r')
	for line in file:
		for word in line.split(' '):
			yield word

word_gen = random_word('LoremIpsum')
		
class ReceiverTaskSet(TaskSet):

	@task(5)
	def poll_message(self):
		global Tails
		Tails.append(self.client.current_dialogue)
		with self.client.post('dialogues/{0}/get_messages'.format(self.client.current_dialogue), json={'id': str(self.client.id)} ,catch_response = True, name = "GET /dialogues/get_messages") as resp:
			if resp.status_code == 200:
				Tails.remove(self.client.current_dialogue)
			else: resp.failure("unexpected error in long poll")			

	def on_start(self):
		"""initializing a user and assignng it a password"""
		global num_users
		global Receivers

		#preparing a user data
		self.client.username = str(random.randint( num_users/2, num_users) )			
		password = 'pass'+ self.client.username
 
		data = {"username": self.client.username,
				"password": password }

		# pdb.set_trace()
		with self.client.post('register', json = data, catch_response=True) as resp:
			if resp.status_code == 409:
				"""such user already exists"""
				# pdb.set_trace()
				with self.client.post('login', json = data, catch_response=True) as resp2:
					if resp2.status_code == 404:
						resp2.failure('password issue')
					else: 
						self.client.id = resp2.json()['id']
						Receivers.append(self.client.id)
						# resp2.success()
					resp.success()
			else: 
				self.client.id = resp.json()['id']
				Receivers.append(self.client.id)
				# resp.success()

		global Senders

		from_id = random.randint(0,num_users/2)

		Senders.append(from_id)

		# creating dialogue
		with self.client.put('dialogues/{0}'.format(from_id), json = {'id': str(self.client.id) }, catch_response=True, name="PUT /dialogues/dialogue_id" ) as resp:
			if resp.status_code == 404:
				resp.failure('somehow chose invalid user')
			if resp.status_code == 409:
				#  print "logging into an exsting dialogue"
				self.client.current_dialogue = str(resp.json()['dialogue_id'])
				resp.success()
	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			resp.success()
	 		else: resp.failure("Error initializing Receiver dialogue")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(self.client.current_dialogue), json={'id': str(self.client.id) }, catch_response=True, name="POST /dialogues/<dialogue_id") as resp:
	 		if resp.status_code == 409:
	 			pass
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")
	 	# print "polling a message"
	 	self.poll_message()

class Sender_dialogue(TaskSet):

	@task(1)
	def close_dialogue(self):
		self.interrupt()

	@task(2)
	def send_message(self):
		if Tails:
			with self.client.post('dialogues/{0}/messages_text'.format(Tails[0]) , json = {'datetime': time.strftime('%Y-%m-%d %H:%M:%S'), 'from_id': str(self.client.id), 'body': word_gen.next(), 'id': str(self.client.id) }, catch_response=True, name="dialogues/dialogue_id/messages_text") as resp:
				if resp.status_code == 200:
					resp.success()
					#  print resp.text
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
				#  print "chose invalid user"
				# resp.success()
				self.interrupt()

			if resp.status_code == 409:
				# opened existing dialogue
				self.client.current_dialogue = str(resp.json()['dialogue_id'])
				# resp.success()

	 		if resp.status_code == 200:
	 			self.client.current_dialogue = str(resp.json()['dialogue_id'])
	 			# resp.success()

	 		else: resp.failure("Error creating Sender dialogue")

	 	#opening dialogue
	 	with self.client.post('dialogues/{0}'.format(self.client.current_dialogue), json={'id': str(self.client.id) }, catch_response=True, name="POST /dialogues/dialogue_id") as resp:
	 		if resp.status_code == 409:
	 			# Opened existing dialogue
	 			resp.success()
	 		else: 
	 			if resp.status_code == 200:
	 				resp.success()
	 			else: resp.failure("unexpected error with dialogue initialization")


class SenderTaskSet(TaskSet):
	tasks = {Sender_dialogue: 10}

	@task(2)
	def get_userpage(self):
		self.client.get('users/{0}'.format(self.client.id), name='/users/dialogue_id')
	
	@task(5) 
	def search_user(self):
		# pdb.set_trace()
		with self.client.post('users/search', json={'username': random.randint(0,num_users) }, catch_response=True) as resp:
			if resp.status_code == 404:
				# resp.success()
				pass
			else: 
				if resp.status_code == 200:
					resp.success()
					pass
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

		if Senders:
			self.client.id = Senders.pop()
		else:
			with self.client.post('register', json = data, catch_response=True) as resp:
				if resp.status_code == 409:
					with self.client.post('login', json = data, catch_response=True) as resp2:
						if resp2.status_code == 404:
							resp2.failure('password issue')
						else: 
							self.client.id = resp2.json()['id']
							Senders.append(self.client.id)
							resp2.success()

					resp.success()
				else: 
					self.client.id = resp.json()['id']
					Senders.append(self.client.id)
					resp.success()

class Sender(HttpLocust):
	"""the one who promised to call"""
	weight = 1 #this attribute "how often this type of user calls"
	task_set = SenderTaskSet
	min_wait = 50
	max_wait = 1500

class Receiver(HttpLocust):
	"""the girl who waited"""
	weight = 2
	task_set = ReceiverTaskSet
	min_wait = 500
	max_wait = 15000
