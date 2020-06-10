from flask import Flask, jsonify, abort, render_template, session, url_for, request, redirect
from Songs import *

driver()
app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def main():
    """
    Render main page.
    """
    return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Login for admin
    """
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['username'] = request.form['username']
            return redirect(url_for('list_songs_render'))
        else:
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main'))


@app.route('/admin/songs/')
def list_songs_render():
    if 'username' not in session: # protect against not logged in users
        return redirect(url_for('login'))
    songs_dict = get_songs()
    return render_template("songs/list.html", songs=songs_dict)


@app.route('/admin/songs/add')
def add_song_render():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("songs/add_song.html")


@app.route('/admin/songs/add', methods=['POST'])
def add_song_request():
    if 'username' not in session:
        return redirect(url_for('login'))
    res = add_song(json.dumps(request.get_json()))
    return jsonify(res)


@app.route('/admin/songs/edit/<song_id>')
def edit_songs_render(song_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    song = get_song(song_id)  # try get the song
    if song == -1:  # if there is not a song with this ID throw 404 error
        abort(404)
    artists = ''
    for index in range(len(song.artists)):  # artists separated by comma for input
        artists += song.artists[index]
        if index < len(song.artists) - 1:
            artists += ', '
    return render_template("songs/edit_song.html", song=song, artists=artists)


@app.route('/admin/songs/edit', methods=['POST'])
def edit_song_request():  # edit song POST method
    if 'username' not in session:
        return redirect(url_for('login'))
    data = request.get_json()
    res = edit_song(data['id'], data['title'], data['artists'], data['lyrics'])  # get song info and run edit_song
    return jsonify(res)


@app.route('/admin/songs/delete', methods=['POST'])
def delete_song_request():
    if 'username' not in session:
        return redirect(url_for('login'))
    data = request.get_json()
    res = delete_song(data['id'])
    return jsonify(res)


@app.route('/lyrics', methods=['POST'])
def lyrics():  # get query and take to complete_lyrics function
    res = complete_lyrics(request.get_json()['query'])
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True, host='localhost')
