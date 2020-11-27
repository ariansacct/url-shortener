from python:3.6.4-slim-jessie
RUN pip install bidict
RUN pip install CherryPy
RUN pip install configparser
COPY app.py .
COPY config.properties .
EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
