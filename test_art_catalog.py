from unittest import TestCase
import sqlite3
import art_catalog

class TestInputString(TestCase):

    def test_add_artist_empty_strings(self):
        with self.assertRaises(sqlite3.Error):
            name = ''
            email = ''
            art_catalog.add_artist(name,email)
