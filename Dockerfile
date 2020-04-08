FROM python:3.7

# Install Chromium.
RUN \
  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
  echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
  apt-get update && \
  apt-get install -y google-chrome-stable && \
  rm -rf /var/lib/apt/lists/* \
  && wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip


#RUN curl https://intoli.com/install-google-chrome.sh | bash \
#	&& sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome \
#	&& wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip \
#	&& unzin chromedriver_linux64.zip


RUN mkdir -p /opt/gmaps
COPY target/* /opt/gmaps/

RUN pip install --no-cache-dir -r /opt/gmaps/requirements.txt && \
    pip install --no-cache-dir /opt/gmaps/gmaps-extractor.tar.gz

ENTRYPOINT ["/opt/cr/bin/scrapper.sh"]