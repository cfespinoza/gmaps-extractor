FROM python

RUN mkdir -p /usr/gmaps

COPY extractor /usr/gmaps/

COPY resources /usr/gmaps/

