import unittest
from final import *

## All tests are done under the assumption that the database is filled with
## the info from the sample search of preselected authors

## it may take an abnormal amount of time to run if there is no cache saved

class TestAuthorTable(unittest.TestCase):

    def test_names(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Name
            FROM Authors
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        self.assertIn(('Mike Lupica',), results_list)
        self.assertEqual(len(results_list), 10)

    def test_birth_dates(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT BirthDate
            FROM Authors
            WHERE Name="Hunter Thompson"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('(1937-07-18)',), result_list)

    def test_alive(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Name
            FROM Authors
            WHERE DeathDate="Alive"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('Stephen King',), result_list)
        self.assertEqual(len(results_list), 4)

class TestBookTable(unittest.TestCase):

    def test_total_books(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Title
            FROM Books
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        self.assertIn(('Cujo',), results_list)
        self.assertEqual(len(results_list), 300)

    def test_book_from_author(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Title
            FROM Books
            WHERE AuthorId='3'
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        self.assertIn(('Fear and Loathing in Las Vegas',), results_list)
        self.assertEqual(len(results_list), 30)

class TestMovieTable(unittest.TestCase):

    def test_total_movies(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Title
            FROM Movies
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        self.assertIn(('Kurt Vonnegut: Unstuck in Time',), results_list)
        self.assertEqual(len(results_list), 31)

    def test_author_movies(self):
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Title
            FROM Movies
            WHERE AuthorId='1'
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        self.assertIn(('Jack Kerouac Slept Here',), results_list)
        self.assertEqual(len(results_list), 6)

sample_search(10)
unittest.main()
