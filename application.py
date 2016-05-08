from gevent import monkey
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json 
import requests
from elasticsearch import Elasticsearch

monkey.patch_all()
application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(application, async_mode='gevent')

disp_process_pref = "===[Process]===: "


# Render home page
@application.route('/')
def index():
    return render_template('index.html')

# Render home page
@application.route('/index')
def index_():
    return render_template('index.html')


@application.route('/signin')
def signin():

    return render_template('signin.html')


@application.route('/signin', methods = ['POST'])
def getSignin():
    print request.form.get('user-mail')
    print request.form.get('user-password')



    return render_template('index.html')


@application.route('/signup')
def signup():
    return render_template('signup.html')

# Main function
if __name__ == '__main__':
    socketio.run(application, debug=True)