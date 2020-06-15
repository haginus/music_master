import string
from unidecode import unidecode
import os
import random
from flask import url_for

import IndexHandler
import SongHandler
from EmojiHandler import add_emoji


class IndexService:
    __instance = None

    @staticmethod
    def get_instance():
        if IndexService.__instance is None:
            IndexService()
        return IndexService.__instance

    def __init__(self):
        if IndexService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            IndexService.__instance = self
            self.song_handler = SongHandler.SongHandler.get_instance()
            self.index_handler = IndexHandler.IndexHandler.get_instance()

    def add_song(self, title, artists, lyrics):
        song = self.song_handler.add_song(title, artists, lyrics)
        if song is not None:  # if the song was saved successfully
            res = self.index_handler.index_lyrics(song)
            if res['success']:  # if indexing was successful
                return {'success': True, 'song_id': song.id}

        return {'success': False}

    def edit_song(self, song_id, title=None, artist=None, lyrics=None):
        prev_song = self.song_handler.get_song(song_id)  # get song in current state
        if prev_song is None:  # if song does not exist
            return {'success': False}
        res = self.index_handler.remove_from_index(prev_song)  # remove it from index
        if res['success']:
            song = self.song_handler.edit_song(song_id, title, artist, lyrics)
            if song is not None:  # if the song was saved successfully
                res = self.index_handler.index_lyrics(song)
                if res['success']:  # if indexing was successful
                    return {'success': True, 'song_id': song.id}

        return {'success': False}

    def delete_song(self, song_id):
        prev_song = self.song_handler.get_song(song_id)  # get song in current state
        if prev_song is None:  # if song does not exist
            return {'success': False}
        res = self.song_handler.delete_song(song_id)
        if res['success']:  # if delete was successful
            res = self.index_handler.remove_from_index(prev_song)  # remove from index as well
            if res['success']:
                return {'success': True}
        return {'success': True}

    def get_song(self, song_id):
        return self.song_handler.get_song(song_id)

    def get_songs(self):
        return self.song_handler.get_songs()

    def re_index(self):
        """
            Function to reindex all songs
        """
        self.index_handler.reset_db()
        songs = self.get_songs()
        for song_id in songs:
            self.index_handler.index_lyrics(songs[song_id])

    def reset_db(self):
        """
            Function to remove all songs and indexes
        """
        self.song_handler.reset_db()
        self.index_handler.reset_db()

    def complete_lyrics(self, part, with_emoji=True):
        """
        Function to be called by main.py in order to get the continuation
        """
        to_index = sanitize_text(part).split()  # sanitize text
        res = self.index_handler.find_lyrics(to_index)  # call to get song
        if res['found']:
            choice = random.choice(res["songs"])  # choose a random song / choice is (songId, nextWordPos)
            song = self.song_handler.get_song(str(choice[0]))  # get that random song
            lines = get_next_lines(song.lyrics, choice[1])  # get the lines and add emoji to them
            if with_emoji:
                lines = add_emoji(lines)
            final = ''  # compose response string
            for index in range(len(lines)):
                final += lines[index].replace('(', '').replace(')', '')  # remove ( and ) and append to string
                if index < len(lines) - 1:
                    final += '\n'
            # return the response string and details about the song
            return {'found': True, 'response': {'text': final},
                    'song': {'title': song.title, 'artists': song.artists}}
        else:
            # if there was no match for the query show and image in response
            path = os.getcwd() + "/static/images/not-found"
            image_path = url_for('static', filename="images/not-found/" + random.choice(os.listdir(path)))
            return {'found': False, 'response': {'image': image_path}}


def get_next_lines(lyrics, next_word):
    """
    Function that gets song id and the next word and returns the next part of the song
    """
    while next_word < len(lyrics) and not lyrics[next_word].isalnum():
        # we search for the next letter in the song lyrics
        next_word += 1
    if next_word == len(lyrics):  # if end of track we start over
        next_word = 0
    index = lyrics.find(']', next_word)  # we find the next ] which ends the current part
    if index == -1:
        return []
    part = lyrics[next_word:index].replace('[', '')  # we get the continuation from the next word to the part end
    # part = part.translate(str.maketrans('', '', string.punctuation.replace('(', '').replace(')', '')))
    lines = part.split('\n')  # we split lines
    if len(lines) == 1:  # if there is only one line
        if len(lines[0].split()) <= 3:  # and there are less than 3 words in it
            index2 = lyrics.find('[', index + 1)  # we get the next part of the song
            if index2 != -1:  # (if it exists)
                index3 = lyrics.find(']', index2 + 1)  # find its end
                part = lyrics[index2 + 1:index3]  # and append it as a whole to the first part
                # part = part.translate(str.maketrans('', '', string.punctuation.replace('(', '').replace(')', '')))
                lines += part.split('\n')  # split in lines
    return lines  # return the lines


def sanitize_text(s):
    return unidecode(s.lower()).replace('-', ' ')


