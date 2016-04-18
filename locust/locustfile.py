from locust import HttpLocust, TaskSet, task

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


class WebUserLocust(HttpLocust):
	# weight = 3 #this attribute "how often this type of user calls"
	task_set = MyTaskSet #set taskset which defines user behavior
	min_wait = 5000
	max_wait = 15000