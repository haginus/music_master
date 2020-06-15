import unittest

from IndexService import IndexService


class TestIndexService(unittest.TestCase):
    def test_not_indexed(self):
        """
            We check if the (not_indexed) syntax is working
        """
        index_service = IndexService.get_instance()
        index_service.reset_db()
        index_service.add_song("Vino la mine", ["N&D"],
                               "[nu pot să cred că m-ai uita(aa)t\nnu înțeleg oare de ce ai plec(aaa)t?!]")

        res = index_service.complete_lyrics("nu pot sa cred ca m-ai uitat", False)  # we run this query
        self.assertTrue(res['found'])  # expect to find a match
        self.assertEqual(res['response']['text'], "nu înțeleg oare de ce ai plecaaat?!")  # which should be exactly

    def test_double_encounter(self):
        """
            Check whether the algorithm 'jumps' after the first partial encounter.
        """
        index_service = IndexService.get_instance()
        index_service.reset_db()
        index_service.add_song("Dincolo de noapte e zi", ["Nicola"],
                               "[dincolo de noapte e zi\ndincolo de nori nimeni nu ne va găsi]\n"
                               "[și cerul ne va zâmbi, cum mi-ai promis...]")

        # we have 'dincolo de' repeating
        # we want to get 'dincolo de nori'
        res = index_service.complete_lyrics("dincolo de nori", False)  # we run this query
        self.assertTrue(res['found'])  # expect to find a match
        self.assertEqual(res['response']['text'], "nimeni nu ne va găsi")  # which should be exactly

    def test_same_segment_in_multiple_songs(self):
        """
            We will identify 2 songs with the same words which we are going to query
        """
        index_service = IndexService.get_instance()
        index_service.reset_db()
        song1 = index_service.add_song("Undeva-n Balkani", ["Puya"],
                                       "[Sud-Est, România, undeva-n balkani\n"
                                       "când aterizezi pe aeroporțile pline de bani!]\n"
                                       "[Is this, is this the life? I wanna live, I wanna carry on...]")

        song2 = index_service.add_song("Americandrim", ["Puya"],
                                       "[Undeva-n balkani sună a manele...\npăi mai demult, aici era Turcia, mă vere!]")

        res = index_service.index_handler.find_lyrics(['undeva', 'n', 'balkani'])

        song_ids = [res['songs'][i][0] for i in range(len(res))]  # we get the song IDs in the result
        self.assertTrue(res['found'])  # expect to find a match
        # expect to find our two different songs in the result
        self.assertTrue(song1["song_id"] in song_ids and song2["song_id"] in song_ids and len(song_ids) == 2)

    def test_remove_from_index_by_editing(self):
        """
            We will create a song, query by its words, then edit it and try again.
        """
        index_service = IndexService.get_instance()
        index_service.reset_db()
        song = index_service.add_song("O secundă", ["Simplu"],
                                      "[O secundă și mi-a fost de-ajuns\n"
                                      "am zărit-o, în inimă mi-a pătruns!]\n"
                                      "[Și mă simt fericit\nFiindcă ea e tot ce mi-am dorit!]")

        res = index_service.index_handler.find_lyrics("o secunda".split())  # we run this query
        self.assertTrue(res['found'])  # expect to find a match

        # we change the lyrics from 'o secunda' to 'un minut'
        index_service.edit_song(song_id=str(song["song_id"]), lyrics="[UN MINUT și mi-a fost de-ajuns\n"
                                                                     "am zărit-o, în inimă mi-a pătruns!]\n"
                                                                     "[Și mă simt fericit\nFiindcă ea e tot ce mi-am "
                                                                     "dorit!]")

        res = index_service.index_handler.find_lyrics("o secunda".split())  # we run this again
        self.assertFalse(res['found'])  # expect to not find a match

    def test_delete_song(self):
        """
            We will create and then delete a song.
        """
        index_service = IndexService.get_instance()
        index_service.reset_db()
        song = index_service.add_song("Dă-mi nopțile înapoi", ["A.S.I.A"],
                                      "[Dă-mi nopțile înapoi\n"
                                      "și zilele cu soare\n"
                                      "[Dă-mi visele înapoi\n"
                                      "chiar dacă știu că doare...\n")

        song_id = str(song["song_id"])

        song_obj = index_service.get_song(song_id)  # get the song by its ID
        self.assertTrue(song_obj is not None)  # expect it exists after we added it
        index_service.delete_song(song_id)
        song_obj = index_service.get_song(song_id)  # get the song by its ID
        self.assertFalse(song_obj is not None)  # we expect it not to exist after its removal


if __name__ == '__main__':
    unittest.main()
