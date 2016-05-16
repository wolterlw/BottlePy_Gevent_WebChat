from locust import HttpLocust, TaskSet, task
import pdb
from gevent import queue as qu

Senders = []
Recievers = []





class Sender(HttpLocust):
	tasks = SenderTaskSet
	min_wait = 10
	max_wait = 1000

class Reciever(HttpLocust):
	tasks = ReceiverTaskSet
	min_wait = 10
	max_wait = 10000
