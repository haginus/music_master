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
    """
    Takes a song and removes it from index
    Index for is index[word] = List of (songId, wordCount, (wordStart, wordEnd))
    """
    lyrics = song.lyrics
    lyrics = unidecode.unidecode(lyrics.lower())  # remove diacritics and lower the chars
    lyrics = re.sub(r"\([^\(\)]*\)", '', lyrics)  # regex to remove parts that won't be indexed
    to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]  # break into words
    global lyrics_dict
    for index in range(len(to_index)):  # for every (word, wordStart, wordEnd) tuple
        tp = to_index[index]  # get tuple
        word = tp[0]  # get word
        res = (index, tp[1])  # construct tuple of wordCount and wordStart
        prev = lyrics_dict[word]  # get the word in index
        prev.remove((song.id, res[0], res[1]))  # remove occurrence marking this song
        if len(prev) == 0:
            del lyrics_dict[word]  # if there are no other occurrences of this word in other songs remove it from index
        else:
            lyrics_dict.update({word: prev})  # else just update with the new tuple list
    f = open("lyrics.pkl", "wb")  # save in file
    pickle.dump(lyrics_dict, f)
    f.close()


def index_lyrics(song):
    """
    Takes a song and adds it to index
    Index for is index[word] = List of (songId, wordCount, (wordStart, wordEnd))
    """
    lyrics = song.lyrics
    lyrics = unidecode.unidecode(lyrics.lower())  # remove diacritics and lower the chars
    lyrics = re.sub(r"\([^\(\)]*\)", '', lyrics)  # regex to remove parts that won't be indexed
    to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]  # break into words
    global lyrics_dict
    for index in range(len(to_index)): # for every (word, wordStart, wordEnd) tuple
        tp = to_index[index]  # get tuple
        word = tp[0]
        res = (index, tp[1])  # construct tuple of wordCount and wordStart
        prev = []
        if word in lyrics_dict:  # if this word is in index get the previous list, otherwise we have a blank list
            prev = lyrics_dict[word]
        prev.append((song.id, res[0], res[1]))  # append to previous list
        lyrics_dict.update({word: prev})  # update word with its new list of tuples
    f = open("lyrics.pkl", "wb")  # save to file
    pickle.dump(lyrics_dict, f)
    f.close()


def add_song(data):
    """
    Gets song data from GUI and parses it. Adds song to the song dictionary and calls the index function.
    """
    parsed = json.loads(data)  # parse data from call
    title = parsed['title']
    artist = parsed['artists']
    lyrics = parsed['lyrics'].replace('\u2026', '...')  # and get all the info
    song = Song(title, artist, lyrics)  # create a song obj with it (constructor generates unique ID)
    songs[song.id] = song  # add song to the song dictionary
    f = open("songs.pkl", "wb")  # and save the dictionary to file
    pickle.dump(songs, f)
    f.close()
    index_lyrics(song)  # proceed to index the lyrics of song
    return {'success': True, 'song_id': song.id}  # return a success message with the song ID


class Song:
    def __init__(self, title, artists, lyrics):
        self.title = title
        self.lyrics = lyrics
        self.artists = artists
        self.id = uuid.uuid4()  # generates unique ID for the new song


def check_hyphen(to_index):
    """
    Utility function to check whether we match a combination of words
    that could have hyphen as splitter instead of space.
    Eg.: 'ne a' should actually be written as 'ne-a'
    """
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
    """
    Gets a song part and returns continuation (if any).
    """
    to_index = sanitize_text(part).split()  # sanitize text and check hyphen
    to_index = check_hyphen(to_index)
    for index in range(len(to_index)):  # for every word in this song part
        to_index[index] = unidecode.unidecode(to_index[index].lower())
        if to_index[index] not in lyrics_dict:  # if any of the words is not in the index then we don't have a match
            return {'found': False}
    trace = {}
    # following things are deeply discussed in the documentation
    for (song_id, word_index, char_index) in lyrics_dict[to_index[0]]:
        # we create a trace starting with the first word of the song part
        if song_id in trace:
            trace[song_id].append([(word_index, char_index)])
        else:
            trace[song_id] = [[(word_index, char_index)]]
    # trace is a dict with song IDs as keys and lists of successor words
    # for every occurrence of the first word as values
    for index in range(1, len(to_index)):  # for every second to last word in the song part
        word = to_index[index]
        has_cont = False
        for_songs = {}
        for (song_id, word_index, char_index) in lyrics_dict[word]:  # we get all occurrences of that word in all songs
            if song_id in for_songs:
                for_songs[song_id].append((word_index, char_index))
            else:
                for_songs[song_id] = [(word_index, char_index)]
        for key in trace:  # for every song candidate in trace
            if key in for_songs:  # we check whether that song has our word
                for occ in for_songs[key]:  # for every occurrence of the word in this song
                    for trace_list_index in range(len(trace[key])):  # for every list of successor words in song trace
                        if index - 1 < len(trace[key][trace_list_index]):  # check if count of word matches continuation
                            if trace[key][trace_list_index][index - 1][0] + 1 == occ[0]:  # and words match
                                trace[key][trace_list_index].append(occ)  # then append to the trace
                                has_cont = True  # and mark that this sequence exists in one of these songs (for now)
        if not has_cont:  # if none of the songs did match these conditions we stop (this query will return nothing)
            break
    found_songs = []

    for key in trace:  # we construct the found songs list
        for occ in trace[key]:
            if len(occ) == len(to_index):  # we check if the length of the query
                # is equal to the length of the successive words, and if so we add to the list the song id
                # and the next word position in the lyrics string
                found_songs.append((key, occ[len(occ) - 1][1][1]))
    if len(found_songs) > 0:  # if there are found songs
        song = songs[found_songs[0][0]]  # we choose the first one and return it with all possible next words
        return {'found': True, 'song_id': song.id, 'next_word': [found_songs[0][1]]}

    return {'found': False}


def get_next_lines(params):
    """
    Function that gets song id and the next word and returns the next part of the song
    """
    lyrics = songs[params['song_id']].lyrics
    next_word_choice = random.choice(params['next_word'])  # we choose a random next word from the possibilities
    while not lyrics[next_word_choice].isalnum():  # we search for the next letter in the song lyrics
        next_word_choice += 1
    index = lyrics.find(']', next_word_choice)  # we find the next ] which ends the current part
    if index == -1:
        return []
    part = lyrics[next_word_choice:index].replace('[', '')  # we get the continuation from the next word to the part end
    lines = part.split('\n')  # we split lines
    if len(lines) == 1:  # if there is only one line
        if len(lines[0].split()) <= 3:  # and there are less than 3 words in it
            index2 = lyrics.find('[', index + 1)  # we get the next part of the song
            if index2 != -1:  # (if it exists)
                index3 = lyrics.find(']', index2 + 1)  # find its end
                part = lyrics[index2 + 1:index3]  # and append it as a whole to the first part
                lines += part.split('\n')  # split in lines
    return lines  # return the lines


def add_emoji(lines):
    """
    Function to add emoji to the lines.
    """
    for indx in range(len(lines)):  # for every line
        # remove ( and )
        to_index = lines[indx].translate(str.maketrans('', '', string.punctuation.replace('(', '').replace(')', ''))).split()
        for index in range(len(to_index)):  # and diacritics and lower chars
            to_index[index] = unidecode.unidecode(to_index[index].lower())
        for word in to_index:
            word = re.sub(r"\([^\(\)]*\)", '', word)  # for every word
            if word in emoji_dict:  # if it is in our emoji dictionary
                lines[indx] = lines[indx] + ' ' + emoji_dict[word]  # we add that emoji to the end of the line
    return lines  # return lines with emoji


def complete_lyrics(part):
    """
    Function to be called by main.py in order to get the continuation
    """
    res = find_lyrics(part)  # call to get song
    if res['found']:
        lines = add_emoji(get_next_lines(res))  # get the lines and emoji to them
        final = ''  # compose response string
        for index in range(len(lines)):
            final += lines[index].replace('(', '').replace(')', '')  # remove ( and ) and append to string
            if index < len(lines) - 1:
                final += '\n'
        # return the response string and details about the song
        return {'found': True, 'response': {'text': final},
                'song': {'title': songs[res['song_id']].title, 'artists': songs[res['song_id']].artists}}
    else:
        # if there was no match for the query show and image in response
        path = os.getcwd() + "/static/images/not-found"
        image_path = url_for('static', filename="images/not-found/" + random.choice(os.listdir(path)))
        return {'found': False, 'response': {'image': image_path}}


def get_songs():
    """
    Function to get all songs.
    """
    global songs
    return songs


def get_song(song_id):
    """
        Function to get a song by its ID.
    """
    global songs
    try:
        song_id = uuid.UUID(song_id)
        if song_id in songs:
            return songs[song_id]
        else:
            return -1
    except:  # if we could not make a UUID out of the song_id string
        return -1


def edit_song(song_id, title, artists, lyrics):
    """
        Function to edit a song.
    """
    song = get_song(song_id)  # get the song
    song.title = title
    song.artists = artists
    if lyrics != song.lyrics:  # if lyrics didn't change there is no need for reindexing, otherwise:
        remove_from_index(song)
        song.lyrics = lyrics
        index_lyrics(song)
    songs[song.id] = song  # save the song to dict
    f = open("songs.pkl", "wb")  # and save to file
    pickle.dump(songs, f)
    f.close()
    return {'success': True, 'song_id': song.id}


def delete_song(song_id):
    """
        Function to delete a song.
    """
    song = get_song(song_id)
    if song == -1:
        return
    remove_from_index(song)
    del songs[song.id]
    f = open("songs.pkl", "wb")
    pickle.dump(songs, f)
    f.close()


def reset_db():
    """
        Function to reinitialize song and lyrics dictionaries.
    """
    f = open('songs.pkl', 'wb')
    g = open('lyrics.pkl', 'wb')
    dic = {}
    pickle.dump(dic, f)
    pickle.dump(dic, g)
    f.close()
    g.close()


def re_index():
    """
        Function to reindex every song.
    """
    global songs
    global lyrics_dict
    lyrics_dict = {}  # we empty the index
    for song in songs:  # take every song and index it
        song_obj = songs[song]
        index_lyrics(song_obj)


def sanitize_text(s):
    return unidecode.unidecode(s.translate(str.maketrans('', '', string.punctuation.replace('-', ''))).lower()).replace('-', ' ')


def driver():
    """
    Function to load dictionaries from files.
    """
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
