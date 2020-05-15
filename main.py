from flask import Flask, jsonify, abort, render_template, url_for, request
from Songs import *

driver()
app = Flask(__name__)


@app.route('/')
def main():
    return render_template("base.html")


@app.route('/songs/')
def list_songs_render():
    songs_dict = get_songs()
    return render_template("songs/list.html", songs=songs_dict)


@app.route('/songs/add')
def add_song_render():
    return render_template("songs/add_song.html")


@app.route('/songs/add', methods=['POST'])
def add_song_request():
    res = add_song(json.dumps(request.get_json()))
    return jsonify(res)


@app.route('/songs/edit/<song_id>')
def edit_songs_render(song_id):
    print(song_id)
    song = get_song(song_id)
    if song == -1:
        abort(404)
    artists = ''
    for index in range(len(song.artists)):
        artists += song.artists[index]
        if index < len(song.artists) - 1:
            artists += ', '
    return render_template("songs/edit_song.html", song=song, artists=artists)


@app.route('/songs/edit', methods=['POST'])
def edit_song_request():
    data = request.get_json()
    res = edit_song(data['id'], data['title'], data['artists'], data['lyrics'])
    return jsonify(res)


@app.route('/songs/delete', methods=['POST'])
def delete_song_request():
    data = request.get_json()
    res = delete_song(data['id'])
    return jsonify(res)


'''
This method expects a json content.
Use header: 'Content-Type: application/json'
'''


@app.route('/lyrics', methods=['POST'])
def post_method():
    res = complete_lyrics(request.get_json()['query'])
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True, host='localhost')
