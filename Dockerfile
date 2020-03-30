FROM python:3.6-alpine

RUN apk add --no-cache --virtual .build-deps gcc libc-dev libxslt-dev && \
    apk add --no-cache libxslt

RUN mkdir -p /opt/gmaps
COPY target/* /opt/gmaps/

RUN pip install --no-cache-dir -r /opt/gmaps/requirements.txt && \
    pip install --no-cache-dir /opt/gmaps/gmaps-extractor.tar.gz

ENTRYPOINT ["/opt/cr/bin/scrapper.sh"]