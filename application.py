#from gevent import monkey
import time
from flask import Flask, render_template, request, g, session, redirect, flash, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json 
import requests
from elasticsearch import Elasticsearch
import sqlalchemy
import predictionio

#monkey.patch_all()
application = Flask(__name__)
application.config['SECRET_KEY'] = 'secret!'
eventserver_url = 'http://52.87.217.221:7070'
access_key = 'fWPlsqEj5AOv4EQSzkCvz-yoOpjeuPnMyWimv_nZS1pT5ndWzEme8S0hspWVzfo-'

pio_client = predictionio.EventClient(
    access_key=access_key,
    url=eventserver_url,
    threads=5,
    qsize=500
)

disp_process_pref = "===[Process]===: "

page_user = ''


#####################################
#
# For hanlding PostGreSQL
#
#####################################
conn_str = 'postgresql://movie:nerds@52.87.217.221:5432/movie'
engine_url = 'https://52.87.217.221:8000/queries.json'

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


    response = requests.post(engine_url, json.dumps({'user': page_user, 'num': 20}), verify=False)
    response = json.loads(response.text)['itemScores']
    print len(response)
    if len(response) == 0:

        cur = g.conn.execute('''
        SELECT *
        FROM movies
        WHERE random() < 0.01
        LIMIT %s''', 20)  

        movie_dict = get_movie(cur)

        
        return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = movie_dict)


    return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = '')

# Render home page
@application.route('/index')
def index_():

    global page_user

    if page_user == '':


        return redirect(url_for('signin'))


    response = requests.post(engine_url, json.dumps({'user': page_user, 'num': 20}), verify=False)
    response = json.loads(response.text)['itemScores']
    print len(response)

    if len(response) == 0:

        cur = g.conn.execute('''
        SELECT *
        FROM movies
        WHERE random() < 0.01
        LIMIT %s''', 20)  

        movie_dict = get_movie(cur)

        
        return render_template('index.html', this_username = page_user, show_what = "Top Picks", movie_info_list = movie_dict)


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
            
            page_user = username
        
        return redirect(url_for('index'))

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

        genre='%'+'Action'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01 LIMIT 20',genre)
        
        movie_dict = get_movie(cur)

        show = "Action Movies"
    elif movie_genre == 'romance':
        genre='%'+'Romance'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01 LIMIT 20',genre)
        
        movie_dict = get_movie(cur)

        show = "Romance Movies"

    elif movie_genre == 'documentary':
        genre='%'+'Documentary'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01 LIMIT 20',genre)
        
        movie_dict = get_movie(cur)
        show = "Documentary Movies"

    elif movie_genre == 'comedy':
        genre='%'+'Comedy'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01 LIMIT 20',genre)
        
        movie_dict = get_movie(cur)
        show = "Comedy Movies"

    elif movie_genre == 'drama':
        genre='%'+'Drama'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01  LIMIT 20',genre)
        
        movie_dict = get_movie(cur)
        show = "Drama Movies"
    elif movie_genre == 'thriller':
        genre='%'+'Thriller'+'%'
        cur = g.conn.execute('SELECT * FROM movies WHERE genre like %s AND random() < 0.01 LIMIT 20',genre)
        
        movie_dict = get_movie(cur)
        show = "Thriller Movies"

    else:
        genre='%'+'Thriller'+'%'
        cur = g.conn.execute('SELECT * FROM movies AND random() < 0.01 LIMIT 20')
        
        movie_dict = get_movie(cur)
        show = "Others"

    return render_template('index.html', this_username = page_user, show_what = show, movie_info_list = movie_dict)



@application.route('/logout')
def logout():
    page_user = ''
    return redirect(url_for('signin'))



@application.route('/profile')
def profile():

    return render_template('profile.html', this_username = page_user)

@application.route('/movie', methods = ["GET", "POST"])
def inbox():

    movie_id = request.args.get('movie_id')

    if request.method == 'POST':
        if request.form["btn_cl"] == "comment":
            user_comment = request.form.get('user-comment')
        elif request.form["btn_cl"] == "1":
            user_rate = 1
        elif request.form["btn_cl"] == "2":
            user_rate = 2
        elif request.form["btn_cl"] == "3":
            user_rate = 3
        elif request.form["btn_cl"] == "4":
            user_rate = 4
        elif request.form["btn_cl"] == "5":
            user_rate = 5
        else:
            pass

        with g.conn.begin() as _:
            print user_rate, movie_id, page_user
            g.conn.execute('DELETE FROM ratings WHERE username = %s AND movie_id = %s', (page_user, movie_id))
            g.conn.execute('INSERT INTO ratings VALUES (%s, %s, %s)', (page_user, movie_id, user_rate))
        pio_client.create_event(
                event="rate",
                entity_type="user",
                entity_id=page_user,
                target_entity_type="item",
                target_entity_id=str(movie_id),
                properties={"rating": user_rate}
            )

    
    cur = g.conn.execute('SELECT * FROM movies WHERE movie_id=%s',movie_id)
        
    movie_dict = get_movie(cur)[0]


    return render_template('movie_page.html', this_username = page_user, this_movie = movie_dict)


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
    application.run(debug=True, port = 5001)


