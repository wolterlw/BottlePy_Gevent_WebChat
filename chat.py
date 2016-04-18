#!/usr/bin/python

# TODO LIST
# 
# create templates for:
# user_profile_template (with availible dialogues there), dialogue template
# 
# create new_message events for users
# 
# add dialogues and database support for new messages 
#  
# use sessions
# try using separate Events for each dialogue and store these events in a dictionary {"dialogue_id": Event}

import uuid
import pdb

from gevent import monkey; monkey.patch_all()
from gevent.event import Event
import bottle
from bottle import run, get, post, redirect, route, request, static_file, template, response
from bottle.ext import sqlite

host_name = 'localhost'
port_num = 8080
d_id_pos = len('http://{}:{}/dialogues/'.format(host_name,port_num))


#USED TO GET STATIC FILES LIKE JAVASCRIPT AND CSS
@route('/static/:filename', name='static')
def static_files(filename):
	return static_file(filename, root='./static/')


@route('/',method='GET')
def index():
	try:
		u_id = int(request.cookies.get('id','0'))
		redirect('/users/{}'.format(u_id))
	except:    
		redirect('/login')

#NO TEMPLATE 
@route('/users/<user_id :int>')
def homepage(user_id,db):
	username = db.execute('SELECT username FROM users WHERE id={}'.format(user_id)).fetchone()[0]
	#later add user-specific content to the template
	#with custom dialogues and stuff
	return template('homepage',name=username) #create a template that displays users username

#NO TEMPLATE
@route('dialogues/<to_id :int>')
def dialogue(to_id,db,request):
	messages = []
	#somehow get some number of last messages from the database and return them in a template
	#create this template
	return template('dialogue',dialogue_id=dialogue_id)

@route('/register',method='GET')
def reg_page():
	return template('register',login_text='Enter unique login')


@route('/a/register/new', method='POST')
def do_register(db):
	username = request.POST.get('username')
	password = request.POST.get('password')

	present = db.execute('SELECT id FROM users WHERE username=\'%s\';' % username).fetchone()

	if present is None:
		new_id = int(db.execute('SELECT MAX(id) FROM users').fetchone()[0])+1
		db.execute('INSERT INTO users VALUES(\'%d\',\'%s\',\'%s\');' % (new_id,username,password))
		response.set_cookie('id',str(new_id))

	else: return HTTPError(409,'Username already exists')


@route('/login')
def do_login():    
	return template('login')


@route('/a/login/new', method='POST')
def do_login(db):
	username = request.POST.get('username')
	password = request.POST.get('password')

	u_id = db.execute('SELECT id FROM users WHERE username=\'%s\' and password=\'%s\';' % (username,password)).fetchone()
	
	if not (u_id is None):
		response.set_cookie('id',str(u_id[0]))
		# do redirection to /users/userid in frontend
	else: return HTTPError(404,'User not found')     


@route('/a/message/new', method='POST')
def message_new(db):
	#FIND OUT DIALOGUE INFORMATION SOMEHOW AND BASED ON THAT DO FURTHER 
	global new_message_event 
	#find out the dialogue id
	#later change for something more cryptic 
	dialogue_id = int(request.url[d_id_pos:])
	#find username
	from_id = int(request.cookies.get('id','0'))
	from_name = db.execute('SELECT userfrom_name FROM users WHERE id=%d' % from_id).fetchone()[0]

	msg = create_message(
		dialogue_id,
		request.POST.get('datetime'),
		from_name, request.POST.get('body'))
	
	db.execute('INSERT INTO messages (message_id,dialogue_id,message_body,time) VALUES({m_id}{d_id}{body}{time});'.format(m_id=msg['message_id'], d_id=msg['dialogue_id'], body=msg['dody'],time=msg['datetime']))
	#NOT YET CHECKED THIS ONE

	#ASYNCHRONOUS HANDLING
	#LOOK UP FOR POSSIBILITY TO UNBLOCK ONLY NEEDED CLIENT NOT ALL OF THEM
	new_message_event.set()
	new_message_event.clear()
	return msg

# RECREATE THIS ONE FOR THE NEW SCHEME
@route('/a/message/updates', method='POST')
def message_updates(session):
	global new_message_event

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
	
#NOT CHECKED
def create_message(dialogue_id, datetime ,from_name, body):
	#every message gets a unique id with uuid
	data = {'message_id': str(uuid.uuid4()), 'dialogue_id': dialogue_id,'datetime': datetime, 'body': body}
	data['html'] = template('message',message_from=(data,from_name))
	return data


app = bottle.app()
app.install(sqlite.Plugin(dbfile='./data/chatData.db'))

if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app=app, server='gevent', host=host_name, port=port_num)