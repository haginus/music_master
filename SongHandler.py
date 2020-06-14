import pickle
import uuid


class Song:
    def __init__(self, title, artists, lyrics):
        self.title = title
        self.lyrics = lyrics.replace('\u2026', '...')  # replace unicode char '...' with 3 dots
        self.artists = artists
        self.id = uuid.uuid4()  # generates unique ID for the new song


class SongHandler:
    songs = {}
    __instance = None

    @staticmethod
    def get_instance():
        if SongHandler.__instance is None:
            SongHandler()
        return SongHandler.__instance

    def __init__(self):
        if SongHandler.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SongHandler.__instance = self
            self._load_files()

    def _load_files(self):
        """
            Function to load pickle files and populate songs dictionary.
        """
        try:
            f = open('songs.pkl', 'rb')
            self.songs = pickle.load(f, encoding='bytes')
            f.close()
        except FileNotFoundError:
            self.reset_db()

    def _save_files(self):
        """
            Function to save dicts to pickle files.
        """
        f = open("songs.pkl", "wb")
        pickle.dump(self.songs, f)
        f.close()

    def reset_db(self):
        """
            Function to reinitialize song and lyrics dictionaries.
        """
        self.songs = {}
        self._save_files()

    def get_song(self, song_id):
        """
            Function to get a song by its ID.
        """
        try:
            song_id = uuid.UUID(song_id)
            if song_id in self.songs:
                return self.songs[song_id]
            else:
                return None
        except TypeError:  # if we could not make a UUID out of the song_id string
            return None

    def get_songs(self):
        return self.songs

    def add_song(self, title, artists, lyrics):
        """
            Adds song to the song dictionary.
        """
        song = Song(title, artists, lyrics)  # create a song object (constructor generates unique ID)
        self.songs[song.id] = song  # add song to the song dictionary
        try:
            self._save_files()
            return song
        except IOError:
            return None

    def edit_song(self, song_id, title, artists, lyrics):
        """
            Function to edit a song.
        """
        song = self.get_song(song_id)  # get the song
        song.title = title
        song.artists = artists
        song.lyrics = lyrics
        self.songs[song.id] = song  # save the song to dict
        try:
            self._save_files()
            return song
        except IOError:
            return None

    def delete_song(self, song_id):
        """
            Function to delete a song.
        """
        song = self.get_song(song_id)
        if song is None:
            return {'success': False}
        del self.songs[song.id]
        try:
            self._save_files()
            return {'success': True, 'song_id': song.id}  # return a success message with the song ID
        except IOError:
            return {'success': False}
