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
port_num = 8080
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
	u_id = int(request.get_cookie('id'))
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
	"""returns a Json {'username': 'dialogue_id'} """
	username = db.execute('SELECT username FROM users WHERE id={}'.format(user_id)).fetchone()[0]

	#TODO: check for appropriate cookies

	dialogues = db.execute(
	'SELECT dialogues.dialogue_id, users.username FROM users INNER JOIN dialogues ON users.id = dialogues.to_id WHERE from_id = ?;',
	(user_id,) ).fetchall()
	return dict( (dialogue[0],dialogue[1]) for dialogue in dialogues )

@route('/users/logout/<user_id:int>/', method='POST')
def logout(user_id):
	response.delete_cookie('id')
 	#TODO: check whether all dialogues are closed


@route('/users/search/', method='POST')
def search_user(db):
	# pdb.set_trace()
	username = request.json['username']
	userid = db.execute('SELECT id FROM users WHERE username=?;', (username,) ).fetchone()
	if userid:
		return { 'id': int(userid[0]) }
	else:
		return HTTPError(404,'no such user')


#==================================DIALOGUE SECTION=======================================================

@route('/dialogues/create_dialogue/<to_id:int>/', method='POST')
def create_dialogue(to_id,db):
	pdb.set_trace()
	from_id = int( request.get_cookie('id') )
	#checking whether this dialogue already exists
	dialogue_id = get_dialogue(from_id,to_id,db)
	if dialogue_id:
		return HTTPError(409, 'dialogue already exists')
	else:
		dialogue_id = int(db.execute('SELECT MAX(dialogue_id)+1 FROM dialogues').fetchone()[0]) 
		db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(from_id, to_id, dialogue_id) )
		db.execute('INSERT INTO dialogues (from_id,to_id,dialogue_id,num_messages,last_updated) VALUES(?,?,?,0,CURRENT_TIMESTAMP);',(to_id, from_id, dialogue_id) )
		return {'dialogue_id': dialogue_id}

#TODO: add a method to delete a dialogue


#NO TEMPLATE
@route('/dialogues/<dialogue_id:int>/init/', method='POST')
def dialogue(dialogue_id,db):
	"""Intended to use already created dialogues"""	
	# pdb.set_trace()
	global num_messages

	from_id = int( request.get_cookie('id') )
	names = db.execute('SELECT users.username, users.id FROM users, dialogues WHERE users.id = dialogues.from_id and dialogues.dialogue_id = ?;',(dialogue_id,)).fetchall()
	
	if not dialogue_id in d_dialogues:
		d_dialogues[dialogue_id] = Event() #new message event for current dialogue

	messages = db.execute('SELECT t_sent, from_id, body FROM messages WHERE dialogue_id = ? ORDER BY t_sent ASC LIMIT ?;', (dialogue_id,num_messages) ).fetchall()
	if messages:
		messages_json = [ {"datetime" : message[0], "from_id": message[1], "body": message[2]} for message in messages ]
		#and sending it to the app
		return { dialogue_id: messages_json }
	else: return None #empty dialogue

# -----------------------------------CHECKED UNTIL HERE---------------------------------------------------

@route('/dialogues/<dialogue_id:int>/messages/new/', method='POST') 
def message_new(db,dialogue_id):
	# pdb.set_trace()
	#could possibly be problems with large messages 
	#make limitations to single message size according to max response size

	from_id = int(request.cookies.get('id'))
	global d_dialogues
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
		#NOT YET CHECKED THIS ONE
		#ASYNCHRONOUS HANDLING
		new_message_event.set()
		new_message_event.clear()
		#this one is a Json encoded string
		return msg

# RECREATE THIS ONE FOR THE NEW SCHEME

@route('/dialogues/<dialogue_id :int>/messages/update/', method='POST')
def message_updates(session,db):
	from_id = int(request.cookies.get('id'))
	global d_dialogues

	new_message_event = d_dialogues[get_dialogue(from_id,to_id)]

	# DEAL WITH CODE HERE
	if new_message_event:
		new_message_event.wait()
	else: return HTTPError(404,"dialogue not opened")

	# USE SESSIONS LATER
	# try:
	# 	for index, m in enumerate(cache):
	# 	   if m['id'] == cursor:
	# 		   return {'messages': cache[index + 1:]}
	# 	return {'messages': cache}
	# finally:
	# 	if cache:
	# 		session['cursor'] = cache[-1]['id']
	# 	else:
	# 		session.pop('cursor', None)
	
@route('/dialogues/<dialogue_id :int>/close/',method='POST')
def dialugue_close(db,d_id):
	d_dialogues.pop(d_id)



def get_dialogue(from_id,to_id,db):
	return db.execute('SELECT dialogue_id FROM dialogues WHERE from_id={0} and to_id={1}'.format(from_id,to_id)).fetchone()

app = bottle.app()
app.install(sqlite.Plugin(dbfile='./data/chatData.db'))

if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app=app, server='gevent', host=host_name, port=port_num)