import pickle
import re
from SongHandler import Song
import unidecode


class IndexHandler:
    lyrics_dict = {}
    __instance = None

    @staticmethod
    def get_instance():
        if IndexHandler.__instance is None:
            IndexHandler()
        return IndexHandler.__instance

    def __init__(self):
        if IndexHandler.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            IndexHandler.__instance = self
            self._load_files()

    def _load_files(self):
        """
            Function to load pickle files and populate songs dictionary.
        """
        try:
            f = open('lyrics.pkl', 'rb')
            self.lyrics_dict = pickle.load(f, encoding='bytes')
            f.close()
        except FileNotFoundError:
            self.reset_db()

    def _save_files(self):
        """
            Function to save dicts to pickle files.
        """
        f = open("lyrics.pkl", "wb")
        pickle.dump(self.lyrics_dict, f)
        f.close()

    def reset_db(self):
        """
            Function to reinitialize song and lyrics dictionaries.
        """
        self.lyrics_dict = {}
        self._save_files()

    def index_lyrics(self, song):
        """
        Takes a song and adds it to index
        Index for word is index[word] = List of (songId, wordCount, (wordStart, wordEnd)) tuples
        """
        lyrics = song.lyrics
        lyrics = unidecode.unidecode(lyrics.lower())  # remove diacritics and lower the chars
        to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]  # break into words
        for index in range(len(to_index)):  # for every (word, wordStart, wordEnd) tuple
            tp = to_index[index]  # get tuple
            word = tp[0]
            word = re.sub(r"\([^\(\)]*\)", '', word)  # regex to remove parts that won't be indexed
            if len(word) == 0:  # if nothing is left, ie: word is of form '(abc)' we don't index it
                continue
            res = (index, tp[1])  # construct tuple of wordCount and wordStart
            prev = []
            if word in self.lyrics_dict:
                # if this word is in index get the previous list, otherwise we have a blank list
                prev = self.lyrics_dict[word]
            prev.append((song.id, res[0], res[1]))  # append to previous list
            self.lyrics_dict.update({word: prev})  # update word with its new list of tuples
        try:
            self._save_files()
            return {'success': True}
        except IOError:
            return {'success': False}

    def remove_from_index(self, song):
        """
        Takes a song and removes it from index
        Index for is index[word] = List of (songId, wordCount, (wordStart, wordEnd))
        """
        lyrics = song.lyrics
        lyrics = unidecode.unidecode(lyrics.lower())  # remove diacritics and lower the chars
        to_index = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r"[\(\)\d\w]+", lyrics)]  # break into words
        for index in range(len(to_index)):  # for every (word, wordStart, wordEnd) tuple
            tp = to_index[index]  # get tuple
            word = tp[0]  # get word
            word = re.sub(r"\([^\(\)]*\)", '', word)  # regex to remove parts that were not indexed
            if len(word) == 0:  # if nothing is left, ie: word is of form '(abc)' we don't have anything to remove
                continue
            res = (index, tp[1])  # construct tuple of wordCount and wordStart
            prev = self.lyrics_dict[word]  # get the word in index
            prev.remove((song.id, res[0], res[1]))  # remove occurrence marking this song
            if len(prev) == 0:
                # if there are no other occurrences of this word in other songs remove it from index
                del self.lyrics_dict[word]
            else:
                self.lyrics_dict.update({word: prev})  # else just update with the new tuple list
        try:
            self._save_files()
            return {'success': True}
        except IOError:
            return {'success': False}

    def find_lyrics(self, to_index):
        """
        Gets a song part and returns continuation (if any).
        """
        for index in range(len(to_index)):  # for every word in this song part
            to_index[index] = unidecode.unidecode(to_index[index].lower())
            if to_index[index] not in self.lyrics_dict:
                # if any of the words is not in the index then we don't have a match
                return {'found': False}
        trace = {}
        # following things are deeply discussed in the documentation
        for (song_id, word_index, char_index) in self.lyrics_dict[to_index[0]]:
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
            for (song_id, word_index, char_index) in self.lyrics_dict[word]:
                # we get all occurrences of that word in all songs
                if song_id in for_songs:
                    for_songs[song_id].append((word_index, char_index))
                else:
                    for_songs[song_id] = [(word_index, char_index)]
            for key in trace:  # for every song candidate in trace
                if key in for_songs:  # we check whether that song has our word
                    for occ in for_songs[key]:  # for every occurrence of the word in this song
                        for trace_list_index in range(len(trace[key])):
                            # for every list of successor words in song trace
                            if index - 1 < len(trace[key][trace_list_index]):
                                # check if count of word matches continuation
                                if trace[key][trace_list_index][index - 1][0] + 1 == occ[0]:  # and words match
                                    trace[key][trace_list_index].append(occ)  # then append to the trace
                                    has_cont = True
                                    # and mark that this sequence exists in one of these songs (for now)
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
            return {'found': True, 'songs': found_songs}  # return the list

        return {'found': False}
