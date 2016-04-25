#!/usr/bin/python

# TODO LIST
# 
#
# use dialogue_id to save one batabase search every time
# use sessions
# TODO: change string formatting in SQL queries to SQL api "?" and stuff 
# TODO: work on ulr arguments
#
# FINISHED TODOS
# try using separate Events for each dialogue and store these events in a dictionary {"dialogue_id": Event}
# add dialogues and database support for new messages 

import uuid
import pdb

from gevent import monkey; monkey.patch_all()
from gevent.event import Event
import bottle
from bottle import run, route, get, post, static_file, template, request, response, redirect, HTTPError
from bottle.ext import sqlite

host_name = 'localhost'
port_num = 8089
d_id_pos = len('http://{}:{}/dialogues/'.format(host_name,port_num))
num_messages = 20
d_dialogues = {}

#USED TO GET STATIC FILES LIKE JAVASCRIPT AND CSS
@route('/static/<filename>/', name='static')
def static_files(filename):
	return static_file(filename, root='./static/')

#works just fine like that
@route('/')
def index():
	pdb.set_trace()
	u_id = int(request.cookies.get('id','0'))
	if u_id: 
		redirect('/users/{}'.format(u_id))
	else:
		redirect('/static/login/')

# @route('/login')
# def do_login():    
# 	return template('login')
# deprecated use /static/login instead


#seems to be working as well
@route('/login/new/', method='POST')
def do_login(db):
	pdb.set_trace()
	username = request.json['username']
	password = request.json['password']

	u_id = db.execute('SELECT id FROM users WHERE username=\'%s\' and password=\'%s\';' % (username,password)).fetchone()
	
	if not (u_id is None):
		response.set_cookie('id',str(u_id['id']))
		# do redirection to /users/userid in frontend
	else: 
		return HTTPError(404,'User not found')     

# @route('/register')
# def reg_page():
# 	return template('register',login_text='Enter unique login')
# deprecated use /static/register instead

#seems to work just fine on regular cases
@route('/register/new/', method='POST')
def do_register(db):
	username = request.json['username']
	password = request.json['password']

	present = db.execute('SELECT id FROM users WHERE username=\'%s\';' % username).fetchone()

	if present is None:
		new_id = int(db.execute('SELECT MAX(id) FROM users;').fetchone()[0])+1
		db.execute('INSERT INTO users VALUES(\'%d\',\'%s\',\'%s\');' % (new_id,username,password))
		response.set_cookie('id',str(new_id))

	else: return HTTPError(409,'Username already exists')

#==================================USER SECTION=======================================================

#NO TEMPLATE 
@route('/users/<user_id:int>/', method='GET')
def user_homepage(user_id,db):
	username = db.execute('SELECT username FROM users WHERE id={}'.format(user_id)).fetchone()[0]
	#later add user-specific content to the template
	#with custom dialogues and stuff
	#TODO: check for appropriate cookies
	return template('homepage',name=username) #create a template that displays users username


@route('/users/logout/<user_id:int>/', method='POST')
def logout(user_id):
	response.delete_cookie('id')
 	#TODO: check whether all dialogues are closed

# -----------------------------------CHECKED UNTIL HERE---------------------------------------------------
#adding separate methods for user search and for creating new dialogue

@route('/users/search/', method='POST')
def search_user(db):
	username = request.json['username']
	userid = db.execute('SELECT id FROM users WHERE username=?;', str(username)).fetchone()
	if userid:
		return { 'id': int(userid[0]) }
	else:
		return HTTPError(404,'no such user')


#==================================DIALOGUE SECTION=======================================================

@route('/dialogues/create_dialogue/<to_id:int>/')
def create_dialogue(to_id,db):
	from_id = int( request.cookies.get('id','0') )
	#checking whether this dialogue already exists
	dialogue_id = get_dialogue(from_id,to_id)
	if dialogue_id:
		return HTTPError(409, 'dialogue already exists')
	else:
		dialogue_id = int(db.execute('SELECT MAX(dialogue_id)+1 FROM dialogues').fetchone()[0]) 
		db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(from_id, to_id, dialogue_id) )
		db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(to_id, from_id, dialogue_id) )
		return {'dialogue_id': dialogue_id}

#TODO: add a method to delete a dialogue


#NO TEMPLATE
@route('/dialogues/<dialogue_id:int>/')
def dialogue(dialogue_id,db):
	from_id = int( request.cookies.get('id','0') )

	if not dialogue_id in d_dialogues:
		d_dialogues[dialogue_id] = Event() #new message event for current dialogue
	#TODO: implement message polling from database 
	# ('SELECT message_id,message_body FROM messages WHERE from_id={0} and to_id={1} LIMIT {3}')
	#and sending it to the app
	#TODO: create this template
	return template('dialogue',dialogue_id=dialogue_id)


@route('/dialogues/<dialogue_id:int>/messages/new/', method='POST') #TODO: this one might actually not work for some reason, maybe because of the url wildcards
def message_new(db,dialogue_id):
	#FIND OUT DIALOGUE INFORMATION SOMEHOW AND BASED ON THAT DO FURTHER 
	pdb.set_trace()
	from_id = int(request.cookies.get('id','0'))
	global d_dialogues
	try:
		new_message_event = d_dialogues[dialogue_id]
	except :
		return HTTPError(404,"dialogue not opened")
	else:
		pass
	#TODO: change for something more cryptic 
	#find username
	from_name = db.execute('SELECT username FROM users WHERE id=?', str(from_id) ).fetchone()[0]

	msg = create_message(
		dialogue_id,
		request.json['datetime'],  #use request header date-time later 
		from_name, 
		request.json['body']
		)
	
	db.execute('INSERT INTO messages (message_id,dialogue_id,message_body,time) VALUES({m_id}{d_id}{body}{time});'.format(m_id=msg['message_id'], d_id=msg['dialogue_id'], body=msg['dody'],time=msg['datetime']))
	db.execute('UPDATE dialogues SET num_messages = num_messages + 1 WHERE dialogue_id=?',msg['dialogue_id'])
	#NOT YET CHECKED THIS ONE

	#ASYNCHRONOUS HANDLING
	new_message_event.set()
	new_message_event.clear()
	#this one is a Json encoded string
	return msg

# RECREATE THIS ONE FOR THE NEW SCHEME
@route('/dialogues/<dialogue_id :int>/messages/update/', method='POST')
def message_updates(session):
	from_id = int(request.cookies.get('id','0'))
	global d_dialogues
	new_message_event = d_dialogues[get_dialogue(from_id,to_id)]

	# DEAL WITH CODE HERE 
	# HAVE NO SESSION IN HERE YET 
	cursor = session.get('cursor')
	if not cache or cursor == cache[-1]['id']:
		 new_message_event.wait()
	assert cursor != cache[-1]['id'], cursor
	# USE SESSIONS LATER
	try:
		for index, m in enumerate(cache):
		   if m['id'] == cursor:
			   return {'messages': cache[index + 1:]}
		return {'messages': cache}
	finally:
		if cache:
			session['cursor'] = cache[-1]['id']
		else:
			session.pop('cursor', None)
	
@route('/dialogues/<dialogue_id :int>/close/',method='POST')
def dialugue_close(db,d_id):
	d_dialogues.pop(d_id)



def create_message(dialogue_id, datetime ,from_name, body):
	#every message gets a unique id with uuid
	data = {'message_id': str(uuid.uuid4()), 'dialogue_id': dialogue_id,'datetime': datetime, 'body': body}
	data['html'] = template('message',message_from=(data,from_name))
	return data

def get_dialogue(from_id,to_id):
	return db.execute('SELECT dialogue_id FROM dialogues WHERE from_id={0} and to_id={1}'.format(from_id,to_id)).fetchone()

app = bottle.app()
app.install(sqlite.Plugin(dbfile='./data/chatData.db'))

if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app=app, server='gevent', host=host_name, port=port_num)