import sqlite3 as sqlite
import requests
import csv
import json
import sys
import codecs
import secrets
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import random
import datetime
import numpy
import pandas
import collections
import re
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

COLORS = ['rgb(230, 25, 75)', 'rgb(60, 180, 75)', 'rgb(255, 225, 25)',
        'rgb(0, 130, 200)', 'rgb(245, 130, 48)', 'rgb(145, 30, 180)',
        'rgb(70, 240, 240)', 'rgb(240, 50, 230)', 'rgb(210, 245, 60)',
        'rgb(250, 190, 190)', 'rgb(0, 128, 128)', 'rgb(230, 190, 255)',
        'rgb(170, 110, 40)', 'rgb(255, 250, 200)', 'rgb(128, 0, 0)'
        'rgb(170, 255, 195)', 'rgb(128, 128, 0)', 'rgb(0, 0, 128)']

DBNAME = 'final.db'

good_reads_auth_url = 'https://www.goodreads.com/api/author_url/{}?key={}'
good_reads_book_url = 'https://www.goodreads.com/author/list/{}?format=xml&key={}'
omdb_url = 'http://www.omdbapi.com/?apikey={}&s={}'
wiki_url = 'https://en.wikipedia.org/wiki/{}'

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

# sets up the database
# params: none
# returns: none
def setup_db():
    # connect to the new database
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    # Drop tables
    statement = '''
        DROP TABLE IF EXISTS 'Authors';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Books';
    '''
    cur.execute(statement)

    statement = '''
        DROP TABLE IF EXISTS 'Movies';
    '''
    cur.execute(statement)

    conn.commit()

    # create authors table
    statement = '''
        CREATE TABLE 'Authors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'BirthDate' TEXT,
            'DeathDate' TEXT
        );
    '''
    cur.execute(statement)

    # create books table
    statement = '''
        CREATE TABLE 'Books' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT,
            'PublishDate' TEXT,
            'PageCount' TEXT,
            'AuthorId' INTEGER
        );
    '''
    cur.execute(statement)

    # create movies table
    statement = '''
        CREATE TABLE 'Movies' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT,
            'ReleaseDate' TEXT,
            'AuthorId' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()


# Makes info request first, by checking the cache, but if not already in the cache
# goes and gets it using proper channels
# params: url string, boolean telling if looking for wikipedia page, boolean telling
#           if looking for author in good reads
# returns: data that is requested
def make_request_using_cache(url, wiki = False, book = False):
    unique_ident = url

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data...")
        # Make the request and cache the new data
        if book == False:
            resp = requests.get(url)
            if wiki == False:
                CACHE_DICTION[unique_ident] = json.loads(resp.text)
            else:
                CACHE_DICTION[unique_ident] = resp.text
            #dumped_cache = json.dumps(CACHE_DICTION)
        else:
            resp = requests.get(url)
            CACHE_DICTION[unique_ident] = resp.text
            #dumped_cache = CACHE_DICTION
        dumped_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

# Searches good reads for author
# params: name of author eg. <First> <Last>
# returns: total number of books written as well as list with book info
def search_books(name):
    authID = ''
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    command = 'SELECT Id FROM Authors WHERE Name=\"' + name + "\""
    cur.execute(command)
    dbID = 0
    for row in cur:
        dbID = row[0]
    nameNew = name.replace(' ', '%20')
    authUrl = good_reads_auth_url.format(nameNew, secrets.good_reads_key)
    authorXml = make_request_using_cache(authUrl, book = True)

    root = ElementTree.fromstring(authorXml)
    for child in root.iter('author'):
        authID = child.attrib['id']

    searchUrl = good_reads_book_url.format(authID, secrets.good_reads_key)
    authorXml = make_request_using_cache(searchUrl, book = True)
    root = ElementTree.fromstring(authorXml)

    for bookItem in root.find('author').find('books').findall('book'):
        title = bookItem.find('title').text
        publishYear = bookItem.find('publication_year').text
        pageCount = bookItem.find('num_pages').text
        insertion = (None, title, publishYear, pageCount, int(dbID))
        statement = 'INSERT INTO "Books" '
        statement += 'VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()

    conn.close()

# Searches omdb for movies with the title of the author in them
# params: name of author eg. <First> <Last>
# returns: list of movies
def search_movies(name):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    command = 'SELECT Id FROM Authors WHERE Name=\"' + name + '\"'
    cur.execute(command)
    dbID = 0
    for row in cur:
        dbID = row[0]
    movies = []
    searchUrl = omdb_url.format(secrets.omdb_api_key, name)
    authorJson = make_request_using_cache(searchUrl)
    try:
        for movie in authorJson['Search']:
            movies.append([name, movie['Title'], movie['Year']])
            insertion = (None, movie['Title'], movie['Year'], int(dbID))
            statement = 'INSERT INTO "Movies" '
            statement += 'VALUES (?, ?, ?, ?)'
            cur.execute(statement, insertion)
            conn.commit()
    except:
        return
    conn.close()

# Scrapes wikipedia page of author
# params: name of author eg. <First> <Last>
# returns: birth and death dates
def search_wiki(name):
    wiki = {}
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    searchUrl = wiki_url.format(name)
    wiki_text = make_request_using_cache(searchUrl, wiki = True)
    page_soup = BeautifulSoup(wiki_text, 'html.parser')
    info_table = page_soup.find('table', class_='infobox vcard')
    if info_table == None:
        info_table = page_soup.find('table', class_='infobox biography vcard')
    if info_table == None:
        return

    for tr in info_table.find_all('tr'):
        ths = tr.find_all('th')
        tds = tr.find_all('td')
        try:
            spans = tr.find('span', style='display:none').text
        except:
            spans = ''

        for i in range(0,len(ths)):
            if ths[i].text == 'Born':
                wiki['Born'] = spans
            if ths[i].text == 'Died':
                wiki['Died'] = spans

    if 'Died' not in wiki.keys():
        wiki['Died'] = 'Alive'

    insertion = (None, name, wiki['Born'], wiki['Died'])
    statement = 'INSERT INTO "Authors" '
    statement += 'VALUES (?, ?, ?, ?)'
    cur.execute(statement, insertion)
    conn.commit()
    conn.close()

def clear_db():
    setup_db()

# Calls all the searches and puts results into dictionary
# params: name of author eg. <First> <Last>
# returns: none
def search_all(name):
    search_wiki(name)
    search_books(name)
    search_movies(name)

# Calls search all specifically when being used by user
# params: name of author
# returns: none
def user_search(name):
    search_all(name)

# Creates Plotly graphs about book publications from info from database
# params: none
# returns: none
def user_timeline():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    earliestPub = 2018
    color = 0
    aNames = []
    avgPages = []
    authors = []
    dataLine = []
    dataBar = []

    # Get all the authors
    sqlStatement = 'SELECT Id, Name FROM Authors'
    cur.execute(sqlStatement)
    for row in cur:
        authors.append(row)

    for a in authors:
        aNames.append(a[1])
        years = []
        numberBooks = []
        annotation = a[1]
        totalPageCount = 0
        sqlStatement = 'SELECT PublishDate, PageCount, AuthorId FROM Books WHERE AuthorId={} ORDER BY PublishDate'.format(str(a[0]))
        cur.execute(sqlStatement)
        bookNumber = 0
        for row in cur:
            if row[0] != None and row[1] != None:
                if int(row[0]) < earliestPub:
                    earliestPub = int(row[0])
                bookNumber += 1
                totalPageCount += int(row[1])
                years.append(row[0])
                numberBooks.append(bookNumber)
        dataLine.append(
            go.Scatter(
                x = years,
                y = numberBooks,
                name = annotation,
                line = dict(color = (COLORS[color]), width = 2)
                )
        )
        avgPages.append(totalPageCount/bookNumber)
        color += 1

    dataBar.append(
        go.Bar(
            x = aNames,
            y = avgPages,
            text = avgPages,
            textposition = 'auto',
            marker=dict(
                color='rgb(230,90,22)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.8
        )
    )
    layoutLine = go.Layout(
        title="Timeline of Publications",
        xaxis = dict(
            range=[earliestPub, 2018]
        ),
        yaxis = dict(
            range=[0, 30]
        ),
        height=500,
        width=1000
    )
    layoutBar = go.Layout(
        title="Average Page Counts",
        yaxis = dict(
            range=[0, max(avgPages)]
        ),
        height=500,
        width=1000
    )

    figLine = go.Figure(data=dataLine, layout=layoutLine)
    py.plot(figLine, filename = 'timeline-of-publications')

    figBar = go.Figure(data=dataBar, layout=layoutBar)
    py.plot(figBar, filename = 'average-page-counts')

# Creates Plotly graphs about author's lifespans from info from database
# params: none
# returns: none
def user_lifespan():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    data = []
    colors = []

    # Get all the authors
    sqlStatement = 'SELECT Name, BirthDate, DeathDate FROM Authors'
    cur.execute(sqlStatement)
    c = 0
    for row in cur:
        colors.append(COLORS[c])
        c += 1
        if row[2] == 'Alive':
            fin = datetime.date.today()
            aName = row[0] + '*'
        else:
            fin = row[2].split('(')[1].split(')')[0]
            aName = row[0]
        data.append(dict(Task='', Start=row[1].split('(')[1].split(')')[0], Finish=fin, Resource=aName))

    fig = ff.create_gantt(data, colors=colors, index_col='Resource', title='Author Lifespans (*Alive)', reverse_colors=True, show_colorbar=True)
    py.plot(fig, filename='author-lifespans')

# Creates Plotly graphs about movies titled after authros from info from database
# params: none
# returns: none
def user_movie():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    aNames = []
    authors = []
    numMovies = []
    ratio = []
    aTimeDiff = []
    timeDiff = []
    earliestMovie = 0
    latestBook = 0

    # Get all the authors
    sqlStatement = 'SELECT Id, Name FROM Authors'
    cur.execute(sqlStatement)
    for row in cur:
        aNames.append(row[1])
        authors.append(row)

    for a in authors:
        earliestMovie = 0
        latestBook = 0
        sqlStatement = 'SELECT Count(*) FROM Movies WHERE AuthorId={}'.format(str(a[0]))
        cur.execute(sqlStatement)
        for row in cur:
            numMovies.append(row[0])
        sqlStatement = 'SELECT ReleaseDate FROM Movies WHERE AuthorId={} ORDER BY ReleaseDate ASC'.format(str(a[0]))
        cur.execute(sqlStatement)
        for row in cur:
            if row != None:
                earliestMovie = row[0]
                break

        sqlStatement = 'SELECT Count(*) FROM Books WHERE AuthorId={}'.format(str(a[0]))
        cur.execute(sqlStatement)
        for row in cur:
            if int(numMovies[-1]) != 0:
                ratio.append(int(row[0])/int(numMovies[-1]))
            else:
                ratio.append(0)
        sqlStatement = 'SELECT PublishDate FROM Books WHERE AuthorId={} ORDER BY PublishDate DESC'.format(str(a[0]))
        cur.execute(sqlStatement)
        for row in cur:
            if row != None:
                latestBook = row[0].split('(')[0].split('-')[0]
                break

        if earliestMovie != 0 and latestBook != 0:
            timeDiff.append(int(earliestMovie) - int(latestBook))
            aTimeDiff.append(a[1])

    trace0 = go.Bar(
        x=aNames,
        y=numMovies,
        name='Number of Movies',
        marker=dict(
            color='rgb(49,130,189)'
        )
    )
    trace1 = go.Bar(
        x=aNames,
        y=ratio,
        name='Ratio of Books to Movies',
        marker=dict(
            color='rgb(204,204,204)',
        )
    )

    data1 = [trace0, trace1]
    layout1 = go.Layout(
        title='Movie Fame',
        barmode='group',
    )

    data2 = [go.Bar(
                x = aTimeDiff,
                y = timeDiff,
                base = 0,
                marker = dict(color = 'purple')
            )
    ]
    layout2 = go.Layout(
        title='Number of Years Between<br>Last Book and First Movie',
        yaxis = dict(
            range=[-1*(abs(max(timeDiff,key=abs))), abs(max(timeDiff,key=abs))]
        )
    )

    fig1 = go.Figure(data=data1, layout=layout1)
    py.plot(fig1, filename='number-of-movies')

    fig2 = go.Figure(data=data2, layout=layout2)
    py.plot(fig2, filename='time-between')

# Creates Plotly graph concerning common words from info from database
# params: none
# returns: none
def user_words():
    data = []
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    words = []

    # Get all the authors
    sqlStatement = 'SELECT Title FROM Books'
    cur.execute(sqlStatement)
    for row in cur:
        title = re.split('[^a-zA-Z]', row[0])
        for t in title:
            if len(t) > 0:
                words.append(t.lower())
    counter = collections.Counter(words)
    sortedWords = []
    sortedValues = []
    top5 = 0
    for c in counter.most_common():
        sortedWords.append(c[0])
        sortedValues.append(c[1])

    data.append(
        go.Pie(
            hole=0.6,
            labels=sortedWords,
            marker=dict(line=dict(color='transparent')),
            values=sortedValues
        )
    )
    layout = go.Layout(
        title='Popularity of Title Words',
        hovermode='closest',
        margin=dict(r=10,t=25,b=40,l=60),
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='title-words')

# Populates the database with a sample search of authors
# params: integer that describes how many authors to include
# returns: none
def sample_search(num):
    clear_db()
    i = 0
    authorList = ['Jack Kerouac', 'Mike Lupica', 'Hunter Thompson',
                'Sylvia Plath', 'George Orwell', 'Kurt Vonnegut',
                'J.K. Rowling', 'Ta-Nehisi Coates', 'Ernest Hemmingway', 'Stephen King']
    for name in authorList:
        search_all(name)
        i += 1
        if i > num:
            break
    return

# prints a help statement
# params: none
# returns: none
def user_help():
    toPrint = '''
            How to Use The Author Comparison Program...

            commands to enter...
            "search <First Name of Author> <Last Name of Author>"
                - this will tell the program to find information about a certain authors
                and will save it into the program's database
                - be sure to include both the first and last name of the author
                - example: "Jack Kerouac"

            "Book Timeline"
                - this will create two graphs comparing books between the authors
                you searched

            "Author Lifespan"
                - this will create a graph comparing the lifespans of the authors
                you searched

            "Movie Fame"
                - this will create figures comparing the movies that are titled after
                the authors you searched

            "Similar Words"
                - this will create a figure showing the most popular words shared in
                titles written by all the authors you searched

            "Clear Searches"
                - this will clear the database of your search results, allowing you
                to do a new search comparing other authors

            "Example Search <# of authors (1-10)>"
                - this will first clear all of your searches from the database
                - then a list of preselected authors will be searched and saved
                - example: "Example Search 7"

            "Help"
                - this will bring up instructions on how to operate the program

            "Exit"
                - this will exit the program

    '''
    print(toPrint)

# checks if a command is valid
# params: user command
# returns: True if valid, False if not
def check_command(comm):
    splitName = comm.split()
    if splitName[0].lower() == 'search':
        return True
    if len(splitName) != 2:
        if len(splitName) == 3:
            if splitName[0].lower() == 'example' and splitName[1].lower() == 'search' and int(splitName[2]) > 1 and int(splitName[2]) < 11:
                return True
            else:
                print('Command not recognized, please try again')
                return False
        if comm.lower() != "help" and comm.lower() != "exit":
            print('Command not recognized, please try again')
            return False
        else:
            return True
    else:
        return True

# Runs while user has not typed 'exit' and prompts them for their commands
# params: none
# returns: none
def interactive_prompt():
    response = ''
    print('Welcome to the Author Comparison Program')
    print('by Rob Dalka\n')
    while response.lower() != 'exit':
        response = input('Enter a command: ')
        if check_command(response) == False:
            continue
        else:
            splitResp = response.split()
            if response.lower() == 'book timeline':
                user_timeline()
            elif response.lower() == 'author lifespan':
                user_lifespan()
            elif response.lower() == 'movie fame':
                user_movie()
            elif response.lower() == 'similar words':
                user_words()
            elif response.lower() == 'clear searches':
                clear_db()
            elif splitResp[0].lower() == 'example' and splitResp[1].lower() == 'search':
                sample_search(int(splitResp[2]))
            elif response.lower() == 'help':
                user_help()
            elif response.lower() == 'exit':
                continue
            elif splitResp[0].lower() == 'search':
                authorName = ''
                for s in range(1,len(splitResp)):
                    authorName += splitResp[s] + ' '
                user_search(authorName)
            else:
                print('Command not recognized, please try again')
    print('Goodbye! :)')


setup_db()
if __name__ == "__main__":
    interactive_prompt()
