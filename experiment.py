#!/usr/bin/python
import pdb
import bottle
import json
from bottle import run, get, post, redirect, route, request, static_file, template
from bottle.ext import sqlite

cache_size = 200
cache = []

@route('/new/<hi>')
def do_login(db,hi):
	# username = request.POST.get('username')
	# password = request.POST.get('password')
	# query = 'SELECT id FROM users WHERE username=\'%s\' and password=\'%s\';' % (username,password)
	# print query
	# row = db.execute(query).fetchone()
	# print row
	pdb.set_trace()
	print yo
	return 0

app = bottle.app()
app.install(sqlite.Plugin(dbfile='chatData.db'))


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, server='gevent', host='localhost', port=8080)