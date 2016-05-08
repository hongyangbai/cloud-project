#from gevent import monkey
import time
from flask import Flask, render_template, request, g, session, redirect, flash, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json 
import requests
from elasticsearch import Elasticsearch
import sqlalchemy

#monkey.patch_all()
application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application, async_mode='gevent')

disp_process_pref = "===[Process]===: "

#####################################
#
# For hanlding PostGreSQL
#
#####################################
conn_str = 'postgresql://movie:nerds@52.87.217.221:5432/movie'

engine = sqlalchemy.create_engine(conn_str)

@application.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        g.conn = None


@application.teardown_request
def teardown_request(_):
    if g.conn is not None:
        g.conn.close()


# Render home page
@application.route('/')
def index():
    return render_template('index.html')

# Render home page
@application.route('/index')
def index_():
    return render_template('index.html')


@application.route('/signin', methods = ['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        print request.form.get('user-mail')
        print request.form.get('user-password')
        username = request.form.get('user-mail')
        password = request.form.get('user-password')
        #cur = g.conn.execute('''SELECT * FROM users WHERE username = %s AND password = %s''', (username, password))
        '''user = cur.fetchone()
        if user is None:
            error = 'Invalid username or password.'
        else:
            session['username'] = username
            flash('You are now logged in as <b>{}</b>.'.format(username))'''
        return redirect(url_for('index'))

    return render_template('signin.html')

@application.route('/profile')
def profile():

    return render_template('profile.html')



@application.route('/signup')
def signup():
    return render_template('signup.html')

# Main function
if __name__ == '__main__':
    socketio.run(application, debug=True)