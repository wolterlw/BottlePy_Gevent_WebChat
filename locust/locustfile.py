from locust import HttpLocust, TaskSet, task
import pdb
import random
from gevent import queue as qu
from time import strftime


n_users = 10000
recievers = qu.Queue()
senders = qu.Queue()
waiters = []

def random_word(file_name):
	file = open(file_name,'r')
	for line in file:
		for word in line.split(' '):
			yield word

word_gen = random_word('LoremIpsum')

class ChatUserTaskSet(TaskSet):

	def login(self):
		username = str( random.randint(0,n_users) )
		password = "pass"+username

		with self.client.post('register',
		 json={'username': username, 'password': password}, catch_response=True) as resp:
			if resp.status_code == 409:
				self.client.id = str(self.client.post('login', json={'username': username, 'password': password}, catch_response=True ).json()['id'])
				resp.success()
			if resp.status_code == 200:
				self.client.id = str(resp.json()['id'])
				resp.success()
			else:
				resp.failure()

	def open_dialogue(self,other_id):
		with self.client.put('dialogues/'+other_id, json={'id': self.client.id}, catch_response=True, name='PUT /dialogues/to_id') as resp:
			if resp.status_code == 404:
				resp.failure('No such user')
			if resp.status_code == 200:
				self.client.current_dialogue = str(resp.json()['dialogue_id'])
				self.client.post('dialogues/'+self.client.current_dialogue, 
					json={'id': self.client.id}, name='POST: /dialogue/dialogue_id')
			else:
				resp.failure('could not open a dialogue')

class RecieverTaskSet(ChatUserTaskSet):

	@task
	def get_messages(self):
		global waiters
		d_id = self.client.current_dialogue
		waiters.append(d_id)
		self.client.post('dialogues/{0}/get_messages'.format(d_id), 
			name='dialogues/dialogue_id/get_messages')

	def on_start(self):
		global senders, recievers

		self.login()

		recievers.put(self.client.id)
		self.client.sender = senders.get()

		self.open_dialogue(other_id=self.client.sender)

class SenderTaskSet(ChatUserTaskSet):
	@task
	def send_message(self):
		global waiters, word_gen
		d_id = self.client.current_dialogue
		while d_id in waiters:
			self.client.post('dialogues/{0}/messages_text'.format(d_id), 
				json={'id': self.client.id, 
					'datetime': strftime('%Y-%m-%d %H:%M:%S'),
					'body': word_gen.next()})

	def on_start(self):
		global senders, recievers

		# pdb.set_trace()
		self.login()

		senders.put(self.client.id)
		self.client.reciever = recievers.get()

		self.open_dialogue(other_id=self.client.reciever)

class Sender(HttpLocust):
	"""The one who sends"""
	task_set = SenderTaskSet #ChatUserTaskSet 
	min_wait = 10
	max_wait = 1000

class Reciever(HttpLocust):
	"""And one who receivers"""
	task_set = RecieverTaskSet #ChatUserTaskSet
	min_wait = 10
	max_wait = 10000
