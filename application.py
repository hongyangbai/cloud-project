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

page_user = ''


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
    return render_template('index.html', this_username = page_user)

# Render home page
@application.route('/index')
def index_():
    return render_template('index.html', this_username = page_user)


@application.route('/signin', methods = ['GET', 'POST'])
def signin():
    error = None
    global page_user

    if request.method == 'POST':
        print request.form.get('user-username')
        print request.form.get('user-password')
        username = request.form.get('user-username')
        password = request.form.get('user-password')
        cur = g.conn.execute('''SELECT * FROM users WHERE username = %s AND password = %s''', (username, password))
        user = cur.fetchone()
        if user is None:
            return render_template('signin.html')

        else:
            session['username'] = username
            page_user = username
        
        return render_template('index.html', this_username = page_user)

    return render_template('signin.html')



@application.route('/signup', methods = ['GET', 'POST'])
def signup():


    error = None
    global page_user

    if request.method == 'POST':
        print request.form.get('user-username')
        print request.form.get('user-password')
        username = request.form.get('user-username')
        password = request.form.get('user-password')
        page_user = username
        try:
            g.conn.execute('''INSERT INTO users (username, password) VALUES (%s, %s)''', (username, password))
            session['username'] = username
        except Exception as e:
            return render_template('signup.html')



        return render_template('index.html', this_username = page_user)



    return render_template('signup.html')


@application.route('/profile')
def profile():

    return render_template('profile.html')


@application.route('/profile-edit')
def profile_edit():

    return render_template('profile-edit.html')


# Main function
if __name__ == '__main__':
    socketio.run(application, debug=True)