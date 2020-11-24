import cherrypy
import pandas as pd
import myprocessor
import random
import string
from bidict import bidict

class MyWebService(object):

    def __init__(self):
        self.link_map = bidict()

    def generate_random_string(self, length = 6):
        letters = string.ascii_lowercase
        print("length: " + str(length))
        result_str = ''.join(random.sample(letters, k = length))
        print("Random String is:", result_str)
        return result_str

    @cherrypy.expose
    def index(self):
        return """<form method="POST" action="shorten">
          <input type="text" name="original_link" size="50"/>
          <button type="submit">Shorten!</button>
        </form>
        <form method="POST" action="retrieve">
          <input type="text" name="shortened_link" size="50"/>
          <button type="submit">Retrieve!</button>"""

    @cherrypy.expose
    def shorten(self, original_link):
        random_string = self.generate_random_string()
        while random_string in self.link_map.values():
            random_string = self.generate_random_string()
        self.link_map[original_link] = random_string
        shortened_link = "shorten.er/" + random_string
        return shortened_link

    @cherrypy.expose
    def retrieve(self, shortened_link):
        # shorten.er/hqgjbe
        random_string = shortened_link.split('/')[1]
        if random_string not in self.link_map.inverse:
            return "Link not found in the database!"
        original_link = self.link_map.inverse[random_string]
        return original_link

if __name__ == '__main__':
    config = {'server.socket_host': '0.0.0.0'}
    cherrypy.config.update(config)
    # cherrypy.quickstart(MyWebService(), '/', config)
    cherrypy.quickstart(MyWebService())