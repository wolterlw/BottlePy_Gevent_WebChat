from locust import HttpLocust, TaskSet, task
import random 

# all users have <number> for username
# and pass<number> for password

class MyTaskSet(TaskSet):
	@task(5)
	def room(self):
		self.client.get('/room')
		payload = {'body':'This is some random text'}
		self.client.post(url='http://localhost:8080/a/message/new',data=payload)

	@task(3)
	def login(self):
		self.client.get('/')
		payload = {'username':'someUser','password':'pass_rand'}
		self.client.post(url='http://localhost:8080/login')

	@task(10)
	def room2(self):
		payload = {'body':'Other Random text'}
		self.client.post(url='http://localhost:8080/a/message/new',data=payload)

	def on_statr(self):
		self.Session['username'] = random.randint(0,100000)
		self.Session['password'] = pass+str(self.Session['username'])

		data = {"username": self.Session['username'],
				"password": self.Session['password']}
		resp = self.client.post('/login/', json = data)
		if resp.status_code == 404:
			resp = self.client.post('/login/', json = data)
			if resp.status_code == 409: print "Wrong password"

		self.Session['id'] = resp.json()['id']


class WebUserLocust(HttpLocust):
	# weight = 3 #this attribute "how often this type of user calls"
	task_set = MyTaskSet #set taskset which defines user behavior
	min_wait = 5000
	max_wait = 15000