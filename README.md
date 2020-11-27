# url-shortener
A Python Web service to shorten URLs. It supports two storage modes: memory and SQLite database. You can switch
between the two modes by changing the `config.properties` file.

This application uses CherryPy to deploy the service on port `8080`. It also utilizes a very simple CSS style file.
By default, it uses a 6-character random string for each new URL. Multiple insertions of the same URL return the same
shortened link. In memory mode, all entries are lost once the application is stopped. In database mode, the entries are
retained as long as the `database.db` file is provided to the application. If the file is deleted or does not exist in
the running folder, a new database is created.

## To run the application

Clone this repository and navigate to its folder. Specify your storage mode
in the `config.properties` file.

### Using Docker

To build the Docker container:
```
docker build -t url-shortener .
```

To run:

```
docker run -p 8080:8080 url-shortener
```

### Without Docker

Make sure the following packages are installed on your
system. This application only runs with Python 3.

```
cherrypy
bidict
configparser
```
You can use the following command to install them:

```
pip install bidict CherryPy configparser
```

Run the application:

```
python app.py
```

## To interact with the application

In your browser, navigate to `localhost:8080` and insert a link
to shorten or retrieve the original.

## Time spent
I spent about 4 hours on this application (including development, testing, and documentation), in multiple sittings.