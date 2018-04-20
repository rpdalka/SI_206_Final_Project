# SI_206_Final_Project
The following are the datasources and tools that I used in this program
>GoodReads API

The GoodReads API gave me access to lists of books that authors wrote and inforamation concerning those book. An API key is required. Instructions on how to obtain an GoodReads API Key can be found here: https://www.goodreads.com/api/keys. You may need to create a Good Reads Account if you do not already have one. Once you have your Good Reads API key, save it in a file named 'secrets.py' and store it into the string variable 'good_reads_key'.

>OMDB API

The OMDB API gave me access to movies that were titled after the specific authors that would be searched. An API key is required. Instruction on how ot obtain an OMDB API key can be found here: http://www.omdbapi.com/apikey.aspx. Please select the free option when requesting the key. Once you have your OMDB key, save it in the same file as the Good Reads key, named 'secrets.py' and store it into the string variable 'omdb_api_key'
    
>Wikipedia

I used webscraping to grab data about authors off of their Wikipedia pages. There is no api key required for this, so do not worry.
  
>Plotly
  
To represent my data, I created visuals using the platform Plotly. To fully utilize my program, make sure you create a Plotly FREE account. Be sure to then follow the directions to connect Plotly to python on your machine laid out here: https://plot.ly/python/getting-started/
    
    
How the Program Runs

>Database Setup
  
    >When the program launches, the function 'setup_db' runs. This creates the database and all the tables in the database.
    >Next a function 'interactive_prompt' runs. This function takes in user commands and processes them with the correct functions.
    >When a user searches a new author, a function 'user_search' is called and calls the three sub-searches, 'search_books', 'search_movies', and 'search_wiki'. These sub-searches place the data they find into the database as they run.

>There are seven other main functions that are called when a user prompts them.
    >'user_timeline' searches the database and creates graphs showing information about book releases from all the authors currently in the database.
    >'user_lifespan' searches the database and creates a graph showing the lifespans of all the authors in the database.
    >'user_movie' searches the database and displays information about the movies that have been titled after authors in the database
    >'user_words' records the commonality among words appearing within the titles of all the books in the database and displays them on a pie chart.
    >'clear_db' will clear the database of any and all searches the user has thus far performed
    >'sample_search' will populate the database with a list of preselected authors and their related information
    >'user_help' will print a helpful message regarding how to use the program.
    >When the user enters 'exit' the program will end its processes and print a goodbye message

User Guide:
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
