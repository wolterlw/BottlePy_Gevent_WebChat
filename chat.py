#!/usr/bin/python

# TODO LIST
# 
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
port_num = 8080
d_id_pos = len('http://{}:{}/dialogues/'.format(host_name,port_num))
num_messages = 20 #number of messages sent when a dialogue is initialized
d_dialogues = {}
message_cache = {} #messages sent to another part of a dialogue

#Used to get all the HTML CSS and JavaScript data needed
#Everything else mostly returns JSONs

@route('/static/<filepath:path>', name='static', method='GET')
def static_files(filepath):
	# pdb.set_trace()
	return static_file(filepath, root='./static/')

@route('')
@route('/')
def index():
	# pdb.set_trace()
	# u_id = request.json['id']
	# if u_id: 
		# redirect('/users/{}'.format(u_id) )
	# else:
	redirect('/static/index.html')

@route('/login', method='POST')
def do_login(db):
	# pdb.set_trace()
	username = request.json['username']
	password = request.json['password']

	u_id = db.execute('SELECT id FROM users WHERE username=? and password=?;', (username,password)).fetchone()
	
	if not (u_id is None):
		return  {'id': str(u_id['id']) }
		# get id from cookie on frontend and create custo cookies
		# do redirection to /users/userid in frontend
	else: 
		return HTTPError(404,'User not found')     

#seems to work just fine on regular cases
@route('/register', method='POST')
def do_register(db):
	username = request.json['username']
	password = request.json['password']

	present = db.execute('SELECT id FROM users WHERE username=\'%s\';' % username).fetchone()

	if present is None:
		new_id = int(db.execute('SELECT MAX(id)+1 FROM users;').fetchone()[0])
		db.execute('INSERT INTO users VALUES(\'%d\',\'%s\',\'%s\');' % (new_id,username,password))
		return {'id': str(new_id)}

	else: return HTTPError(409,'Username already exists')

#==================================USER SECTION=======================================================
 
@route('/users/<user_id:int>', method='GET')
def user_homepage(user_id,db):
	"""returns a Json {'username': 'dialogue_id'} """
	username = db.execute('SELECT username FROM users WHERE id={}'.format(user_id)).fetchone()[0]

	#TODO: check for appropriate cookies

	dialogues = db.execute(
	'SELECT dialogues.dialogue_id, users.username FROM users INNER JOIN dialogues ON users.id = dialogues.to_id WHERE from_id = ?;',
	(user_id,) ).fetchall()
	return dict( (dialogue[0],dialogue[1]) for dialogue in dialogues )

@route('/users/<user_id:int>', method='DELETE')
def logout(user_id):
	response.delete_cookie('id')
	#TODO: check whether all dialogues are closed


@route('/users/search', method='POST')
def search_user(db):
	# pdb.set_trace()
	username = request.json['username']
	userid = db.execute('SELECT id FROM users WHERE username=?;', (username,) ).fetchone()
	if userid:
		return { 'id': int(userid[0]) }
	else:
		return HTTPError(404,'no such user')


#==================================DIALOGUE SECTION=======================================================

@route('/dialogues/<to_id:int>', method='PUT')
def create_dialogue(to_id,db):
	pdb.set_trace()
	from_id = int( request.json['id'] )
	#checking whether this dialogue already exists
	dialogue_id = db.execute('SELECT dialogue_id FROM dialogues WHERE from_id=? and to_id=?',(from_id,to_id)).fetchone()
	to_username = db.execute('SELECT username FROM users WHERE id=?',(to_id,) ).fetchone()
	if to_username:
		if dialogue_id:
			return HTTPError(409, 'dialogue already exists')
		else:
			dialogue_id = int(db.execute('SELECT MAX(dialogue_id)+1 FROM dialogues').fetchone()[0]) 
			db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(from_id, to_id, dialogue_id) )
			db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(to_id, from_id, dialogue_id) )
			return {'dialogue_id': dialogue_id}
	else: return HTTPError(404,'No such user')		

#TODO: add a method to delete a dialogue


@route('/dialogues/<dialogue_id:int>', method='GET')
def dialogue(dialogue_id,db):
	"""Intended to use already created dialogues"""	
	# pdb.set_trace()
	global num_messages
	
	from_id = int( request.json['id'] )
	names = db.execute('SELECT users.username, users.id FROM users, dialogues WHERE users.id = dialogues.from_id and dialogues.dialogue_id = ?;',(dialogue_id,)).fetchall()
	
	if not dialogue_id in d_dialogues:
		d_dialogues[dialogue_id] = Event() #new message event for current dialogue

	messages = db.execute('SELECT t_sent, from_id, body FROM messages WHERE dialogue_id = ? ORDER BY t_sent ASC LIMIT ?;', (dialogue_id,num_messages) ).fetchall()
	if messages:
		messages_json = [ {"datetime" : message[0], "from_id": message[1], "body": message[2]} for message in messages ]
		#and sending it to the app
		return { dialogue_id: messages_json }
	else: return None #empty dialogue


@route('/dialogues/<dialogue_id:int>/messages_text', method='POST') 
def message_new(db,dialogue_id):
	pdb.set_trace()
	#could possibly be problems with large messages 
	#make limitations to single message size according to max response size

	from_id = int( json['id'] )
	global d_dialogues
	global message_cache

	try:
		new_message_event = d_dialogues[dialogue_id]
	except Exception:
		return HTTPError(404,"dialogue not opened")
	else:
		
		#TODO: change for something more cryptic 
		from_name = db.execute('SELECT username FROM users WHERE id=?', str(from_id) ).fetchone()[0]

		msg = {
			'dialogue_id': dialogue_id,
			'message_id': db.execute('SELECT MAX(message_id)+1 FROM messages').fetchone()[0],
			'datetime' : request.json['datetime'],  #use request header date-time later 
			'from': from_name, 
			'body': request.json['body']
			}
		
		db.execute('INSERT INTO messages (message_id,dialogue_id,body,t_sent) VALUES({m_id},{d_id},"{body}","{time}");'.format(m_id=msg['message_id'], d_id=msg['dialogue_id'], body=msg['body'],time=msg['datetime']))

		db.execute('UPDATE dialogues SET num_messages = num_messages + 1 WHERE dialogue_id=? and from_id=?', (msg['dialogue_id'], from_id) )
		#ASYNCHRONOUS HANDLING
		message_cache[dialogue_id] = msg
		new_message_event.set()
		new_message_event.clear()
		#this one is a Json encoded string
		return msg


@route('/dialogues/<dialogue_id:int>/messages', method='GET')
def message_updates(dialogue_id,db):
	# pdb.set_trace()
	from_id = int(request.json['id'])
	global d_dialogues
	global message_cache
	new_message_event = d_dialogues[dialogue_id]

	# DEAL WITH CODE HERE
	if new_message_event:
		new_message_event.wait()
		msg = message_cache.pop(dialogue_id)
		return msg
	else: 
		return HTTPError(404,"dialogue not opened")
	
	# var 1) if new_message.is_set take last message entry for current dialogue and return it  
	# 
	# var 2) try using queues for this
	#
	# var 3) leave messages in memory in some sort of dictionary with stuff from all dialogues 
	
	#TODO: USE SESSIONS

	
@route('/dialogues/<dialogue_id :int>',method='DELETE')
def dialugue_close(db,d_id):
	d_dialogues.pop(d_id)


#================================== BASIC SERVER SETUP =======================================================


app = bottle.app()
app.install(sqlite.Plugin(dbfile='./data/chatData.db'))

if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app=app, server='gevent', host=host_name, port=port_num)