import cherrypy
import pandas as pd
import random
import string
import os
from bidict import bidict
import sqlite3
import configparser


class MyWebService(object):

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

    def generate_random_string(self, length = 6):
        letters = string.ascii_lowercase
        print("length: " + str(length))
        result_str = ''.join(random.sample(letters, k = length))
        print("Random String is:", result_str)
        return result_str

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

    def print_database(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM MAPPINGS')
        print(cursor.fetchall())

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
    config = {'server.socket_host': '0.0.0.0'}
    cherrypy.config.update(config)

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
    my_web_service.print_database()
    cherrypy.quickstart(my_web_service, '/', conf)

    # cherrypy.quickstart(MyWebService(), '/', config)
    # cherrypy.quickstart(MyWebService())
