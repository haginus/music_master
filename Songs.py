import string
import sys
import uuid
import json
import unidecode
import pickle
import os
import random
import re
from flask import url_for

lyrics_dict = {}
songs = {}

emoji_dict = {
    "dimineata": '🌅',
    "ajutorul": '🆘'
}


def remove_from_index(song):
    lyrics = song.lyrics
    lyrics = unidecode.unidecode(lyrics.lower())
    lyrics = re.sub(r"\([^\(\)]*\)", '', lyrics)
    to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]
    global lyrics_dict
    for index in range(len(to_index)):
        tp = to_index[index]
        word = tp[0]
        res = (index, tp[1])
        prev = lyrics_dict[word]
        prev.remove((song.id, res[0], res[1]))
        if len(prev) == 0:
            del lyrics_dict[word]
        else:
            lyrics_dict.update({word: prev})
    f = open("lyrics.pkl", "wb")
    pickle.dump(lyrics_dict, f)
    f.close()


def index_lyrics(song):
    lyrics = song.lyrics
    lyrics = unidecode.unidecode(lyrics.lower())
    lyrics = re.sub(r"\([^\(\)]*\)", '', lyrics)
    to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]
    global lyrics_dict
    print(to_index, "aaa")
    for index in range(len(to_index)):
        tp = to_index[index]
        word = tp[0]
        res = (index, tp[1])
        prev = []
        if word in lyrics_dict:
            prev = lyrics_dict[word]
        prev.append((song.id, res[0], res[1]))
        lyrics_dict.update({word: prev})
    f = open("lyrics.pkl", "wb")
    pickle.dump(lyrics_dict, f)
    f.close()


def add_song(data):
    parsed = json.loads(data)
    title = parsed['title']
    artist = parsed['artists']
    lyrics = parsed['lyrics'].replace('\u2026', '...')
    song = Song(title, artist, lyrics)
    songs[song.id] = song
    f = open("songs.pkl", "wb")
    pickle.dump(songs, f)
    f.close()
    index_lyrics(song)


class Song:
    def __init__(self, title, artists, lyrics):
        self.title = title
        self.lyrics = lyrics
        self.artists = artists
        self.id = uuid.uuid4()


def check_hyphen(to_index):
    for i in range(len(to_index) - 1):
        if to_index[i] in ['te', 'ne']:
            if to_index[i + 1] in ['am', 'ai', 'a', 'ați', 'au']:
                p = to_index[i]
                to_index = to_index[:i] + to_index[i + 1:]
                to_index[i] = p + '-' + to_index[i]
                continue
        if to_index[i] in ['n', 'm', 'i', 's', 'v']:
            p = to_index[i]
            to_index = to_index[:i] + to_index[i + 1:]
            to_index[i] = p + '-' + to_index[i]
    return to_index


def find_lyrics(part):
    to_index = sanitize_text(part).split()
    to_index = check_hyphen(to_index)
    song_parts = {}
    for index in range(len(to_index)):
        to_index[index] = unidecode.unidecode(to_index[index].lower())
        if to_index[index] not in lyrics_dict:
            return {'found': False}
    trace = {}
    for (song_id, word_index, char_index) in lyrics_dict[to_index[0]]:
        if song_id in trace:
            trace[song_id].append([(word_index, char_index)])
        else:
            trace[song_id] = [[(word_index, char_index)]]

    for index in range(1, len(to_index)):
        word = to_index[index]
        has_cont = 0
        for_songs = {}
        for (song_id, word_index, char_index) in lyrics_dict[word]:
            if song_id in for_songs:
                for_songs[song_id].append((word_index, char_index))
            else:
                for_songs[song_id] = [(word_index, char_index)]
        for key in trace:
            if key in for_songs:
                for occ in for_songs[key]:
                    for trace_list_index in range(len(trace[key])):
                        if index - 1 < len(trace[key][trace_list_index]):
                            if trace[key][trace_list_index][index - 1][0] + 1 == occ[0]:
                                trace[key][trace_list_index].append(occ)
                                has_cont = 1
        if has_cont == 0:
            break
    found_songs = []

    for key in trace:
        for occ in trace[key]:
            if len(occ) == len(to_index):
                found_songs.append((key, occ[len(occ) - 1][1][1]))
    if len(found_songs) > 0:
        song = songs[found_songs[0][0]]
        return {'found': True, 'song_id': song.id, 'next_word': [found_songs[0][1]]}

    return {'found': False}


def get_next_lines(params):
    lyrics = songs[params['song_id']].lyrics
    next_word_choice = random.choice(params['next_word'])
    while not lyrics[next_word_choice].isalnum():
        next_word_choice += 1
    index = lyrics.find(']', next_word_choice)
    if index == -1:
        return []
    part = lyrics[next_word_choice:index].replace('[', '')
    lines = part.split('\n')
    if len(lines) == 1:
        if len(lines[0].split()) <= 3:
            index2 = lyrics.find('[', index + 1)
            if index2 != -1:
                index3 = lyrics.find(']', index2 + 1)
                part = lyrics[index2 + 1:index3]
                lines += part.split('\n')
    return lines


def add_emoji(lines):
    for indx in range(len(lines)):
        to_index = lines[indx].translate(str.maketrans('', '', string.punctuation.replace('(', '').replace(')', ''))).split()
        for index in range(len(to_index)):
            to_index[index] = unidecode.unidecode(to_index[index].lower())
        for word in to_index:
            word = re.sub(r"\([^\(\)]*\)", '', word)
            if word in emoji_dict:
                lines[indx] = lines[indx] + ' ' + emoji_dict[word]
    return lines


def complete_lyrics(part):
    res = find_lyrics(part)
    if res['found']:
        lines = add_emoji(get_next_lines(res))
        final = ''
        for index in range(len(lines)):
            final += lines[index].replace('(', '').replace(')', '')
            if index < len(lines) - 1:
                final += '\n'
        return {'found': True, 'response': {'text': final},
                'song': {'title': songs[res['song_id']].title, 'artists': songs[res['song_id']].artists}}
    else:
        path = os.getcwd() + "/static/images/not-found"
        image_path = url_for('static', filename="images/not-found/" + random.choice(os.listdir(path)))
        return {'found': False, 'response': {'image': image_path}}


def get_songs():
    global songs
    return songs


def get_song(song_id):
    global songs
    try:
        song_id = uuid.UUID(song_id)
        if song_id in songs:
            return songs[song_id]
        else:
            return -1
    except:
        return -1


def edit_song(song_id, title, artists, lyrics):
    song = get_song(song_id)
    song.title = title
    song.artists = artists
    if lyrics != song.lyrics:
        remove_from_index(song)
        song.lyrics = lyrics
        index_lyrics(song)
    songs[song.id] = song
    f = open("songs.pkl", "wb")
    pickle.dump(songs, f)
    f.close()


def delete_song(song_id):
    song = get_song(song_id)
    if song == -1:
        return
    remove_from_index(song)
    del songs[song.id]
    f = open("songs.pkl", "wb")
    pickle.dump(songs, f)
    f.close()


def reset_db():
    f = open('songs.pkl', 'wb')
    g = open('lyrics.pkl', 'wb')
    dic = {}
    pickle.dump(dic, f)
    pickle.dump(dic, g)
    f.close()
    g.close()


def re_index():
    global songs
    global lyrics_dict
    lyrics_dict = {}
    for song in songs:
        song_obj = songs[song]
        index_lyrics(song_obj)


def sanitize_text(s):
    return unidecode.unidecode(s.translate(str.maketrans('', '', string.punctuation.replace('-', ''))).lower()).replace('-', ' ')


def driver():
    try:
        f = open('songs.pkl', 'rb')
        global songs
        songs = pickle.load(f, encoding='bytes')
        f.close()
        g = open('lyrics.pkl', 'rb')
        global lyrics_dict
        lyrics_dict = pickle.load(g, encoding='bytes')
        g.close()
    except FileNotFoundError:
        reset_db()
