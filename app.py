import cherrypy
import random
import string
import os
from bidict import bidict
import sqlite3
import configparser


class MyWebService(object):

    '''
    The constructor creates a two-way dictionary (for memory mode), reads/creates the database (for database mode),
    establishes a connection to the database, and creates the underlying table if necessary.
    '''
    def __init__(self):
        self.link_map = bidict()
        self.db_file = 'database.db'
        config = configparser.ConfigParser()
        config.read('config.properties')
        self.mode = config.get("storage", "type")
        self.conn = sqlite3.connect(self.db_file, check_same_thread = False, isolation_level = None)
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS MAPPINGS (original_link TEXT, random_string TEXT);')
        print('Initialized the program with storage type ' + self.mode + '.')

    '''
    This function generates a random string of alphabets (of length 6 by default), which means our system as of now can support
    up to 26 ^ 6 = 308915776 URLs. To increease that, we can either use a bigger character set (e.g., alphanumeric), or
    increase the length of the random string.
    '''
    def generate_random_string(self, length = 6):
        letters = string.ascii_lowercase
        print("length: " + str(length))
        result_str = ''.join(random.sample(letters, k = length))
        print("Random String is:", result_str)
        return result_str

    '''
    This HTML content is loaded at the start of the application.
    '''
    @cherrypy.expose
    def index(self):
        return """
        <head>
   <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
<h2>Welcome to our URL shortening service!</h2>
   <form method="POST" action="shorten">
      <input type="text" name="original_link" class="textField" placeholder="Original link" size="50"/>
      <button type="submit">Shorten!</button>
   </form>
   <form method="POST" action="retrieve">
   <input type="text" name="shortened_link" class="textField" placeholder="Shortened link" size="50"/>
   <button type="submit">Retrieve!</button>
   </form>
</body>
"""

    '''
    This is a helper method that prints the content of the database
    '''
    def print_database(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM MAPPINGS')
        print(cursor.fetchall())

    '''
    This function stores a mapping from an original link to a random string in the configured storage method
    '''
    def store_mapping(self, original_link, random_string):
        if self.mode == 'memory':
            self.link_map[original_link] = random_string
            print("Insertion into the memory completed.")
        elif self.mode == 'database':
            cursor = self.conn.cursor()
            query_string = 'INSERT INTO MAPPINGS VALUES (?, ?);'
            print(query_string)
            params = (original_link, random_string)
            print("params are: " + str(params))
            cursor.execute(query_string, params)
            self.conn.commit()
            print("Insertion into the database completed.")
            self.print_database()

    '''
    This method is called before a new random string is generated; it checks to see if the URL has already been
    inserted into the system.
    '''
    def attempt_to_retrieve(self, original_link):
        if self.mode == 'memory':
            if original_link in self.link_map:
                return self.link_map[original_link]
        elif self.mode == 'database':
            cursor = self.conn.cursor()
            cursor.execute('SELECT random_string FROM MAPPINGS WHERE original_link = "' + original_link + '";')
            fetched_list = cursor.fetchall()
            if len(fetched_list) == 0:
                random_string = None
            else:
                random_string = fetched_list[0][0]
            return random_string

    '''
    This method checks if a generated random string has already been assigned to a URL. Chances of this happening is
    very slim (also depends on how many random strings have already been used), but to ensure correctness this check
    has to be performed.
    '''
    def is_duplicate(self, random_string):
        if self.mode == 'memory':
            if random_string in self.link_map.values():
                return True
        elif self.mode == 'database':
            cursor = self.conn.cursor()
            cursor.execute('SELECT random_string FROM MAPPINGS;')
            fetched_list = cursor.fetchall()
            for tple in fetched_list:
                if random_string == tple[0]:
                    return True
            return False


    '''
    This method handles a shortening request for a URL. It first checks to see if that URL has already been inserted
    into the system. If not, generates a random string and checks for its uniqueness. It then stores the mapping in the
    specified storage type.
    '''
    @cherrypy.expose
    def shorten(self, original_link):
        new_entry = False
        random_string = self.attempt_to_retrieve(original_link)

        if random_string is None:
            random_string = self.generate_random_string()
            while self.is_duplicate(random_string):
                print('Wow! This random string was a duplicate. Generating another one...')
                random_string = self.generate_random_string()
            new_entry = True

        if new_entry == True:
            self.store_mapping(original_link, random_string)
        shortened_link = "shorten.er/" + random_string
        return """
                            <head>
                       <link href="/static/css/style.css" rel="stylesheet">
                    </head>
                    <body>
                    <h2>The shortened link is: {shortened_link}</h2>
                    </body>
                    """.format(shortened_link = shortened_link)

    '''
    This method handles a retrieval request for a URL. It first extracts the random string from the shortened URL. The
    corresponding URL is then retrieved from the specified storage type. If the URL is not found an error message is shown.
    '''
    @cherrypy.expose
    def retrieve(self, shortened_link):
        random_string = shortened_link.split('/')[1]
        if self.mode == 'memory':
            if random_string not in self.link_map.inverse:
                return "Link not found in the system!"
            original_link = self.link_map.inverse[random_string]
        elif self.mode == 'database':
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM MAPPINGS WHERE random_string = "' + random_string + '";')
            original_link = cursor.fetchall()[0][0]
        return """
                <head>
           <link href="/static/css/style.css" rel="stylesheet">
        </head>
        <body>
        <h2>The original link is: {original_link}</h2>
        </body>
        """.format(original_link = original_link)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    my_web_service = MyWebService()
    # to print the existing database contents before application start-up
    # my_web_service.print_database()
    cherrypy.quickstart(my_web_service, '/', conf)
