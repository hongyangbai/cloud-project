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

    global page_user

    if page_user == '':

        return redirect(url_for('signin'))

    return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = '')

# Render home page
@application.route('/index')
def index_():

    global page_user
    if page_user == '':
        return redirect(url_for('signin'))
    return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = '')


@application.route('/signin', methods = ['GET', 'POST'])
def signin():
    error = None
    global page_user

    if request.method == 'POST':
        username = request.form.get('user-username')
        password = request.form.get('user-password')
        cur = g.conn.execute('''SELECT * FROM users WHERE username = %s AND password = %s''', (username, password))
        user = cur.fetchone()
        if user is None:
            return render_template('signin.html')

        else:
            session['username'] = username
            page_user = username
        
        return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = '')

    return render_template('signin.html')



@application.route('/signup', methods = ['GET', 'POST'])
def signup():


    error = None
    global page_user

    if request.method == 'POST':
        username = request.form.get('user-username')
        password = request.form.get('user-password')
        page_user = username
        try:
            g.conn.execute('''INSERT INTO users (username, password) VALUES (%s, %s)''', (username, password))
            session['username'] = username
        except Exception as e:
            return render_template('signup.html')



        return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = '')



    return render_template('signup.html')

@application.route('/show_movie')
def show_movie():
    movie_genre = request.args.get('genre')
    genre=[];
    movie_info_list = []
    if movie_genre == 'action':
<<<<<<< HEAD
        genre='%'+'Action'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s ORDER BY movie_id ASC LIMIT 20',genre)
        # cur = engine.connect().execute('SELECT * FROM movies WHERE genre like %s ORDER BY movie_id ASC LIMIT 10',genre)
        # print 'hey'
        movies=get_movie(cur)
        print movies
=======
#        genre='%'+'Adventure'+'%'
#        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s LIMIT 2',genre)
#        movie_dict = get_movie(cur)
#
#        for each_key in movie_dict.keys():
#            this_movie = []
#            for each in movie_dict[each_key]:
#
#                this_movie.append(each)
#            movie_info_list.append(this_movie)

>>>>>>> origin/master

        show = "Action Movies"
    elif movie_genre == 'romance':
        show = "Romance Movies"
    elif movie_genre == 'documentary':
        show = "Documentary Movies"
    elif movie_genre == 'comedy':
        show = "Comedy Movies"
    elif movie_genre == 'drama':
        show = "Drama Movies"
    elif movie_genre == 'thriller':
        show = "Thriller Movies"
    else:
        show = "Movies"

    return render_template('index.html', this_username = page_user, show_what = show, movie_info_list = movie_info_list)



@application.route('/logout')
def logout():
    page_user = ''
    return redirect(url_for('signin'))



@application.route('/profile')
def profile():

    return render_template('profile.html', this_username = page_user)

@application.route('/inbox')
def inbox():

    return render_template('movie_page.html', this_username = page_user)


@application.route('/profile-edit')
def profile_edit():

    return render_template('profile-edit.html', this_username = page_user)

def get_movie(cur):
    movie_info = {row[0]: (row[1], row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20]) for row in cur}
    movies = []
    for key in movie_info:
        movies.append({'movie_id': key,
                       'imdb_id': movie_info[key][0],
                       'tmdb_id': movie_info[key][1],
                       'title': movie_info[key][2],
                       'year': movie_info[key][3],
                       'plot': movie_info[key][4],
                       'rated': movie_info[key][5],
                       'released': movie_info[key][6],
                       'runtime': movie_info[key][7],
                       'genre': movie_info[key][8],
                       'director': movie_info[key][9],
                       'writer': movie_info[key][10],
                       'actors': movie_info[key][11],
                       'language': movie_info[key][12],
                       'country': movie_info[key][13],
                       'awards': movie_info[key][14],
                       'poster': movie_info[key][15],
                       'metascore': movie_info[key][16],
                       'imdbrating': movie_info[key][17],
                       'imdbvotes': movie_info[key][18],
                       'type': movie_info[key][19]})
    return movies
# Main function
if __name__ == '__main__':
    socketio.run(application, debug=True, port = 5001)


