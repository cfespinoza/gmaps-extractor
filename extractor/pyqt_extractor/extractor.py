import sys
# from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from lxml import html as htmlRenderer
import requests
import json
from datetime import date


def render(source_url):
    """Fully render HTML, JavaScript and all."""

    import sys
    from PySide2.QtWidgets import QApplication
    #     from PyQt5.QtWidgets import QApplication
    from PySide2.QtCore import QUrl
    #     from PyQt5.QtCore import QUrl
    from PySide2.QtWebEngineWidgets import QWebEngineView
    #     from PyQt5.QtWebEngineWidgets import QWebEngineView

    class Render(QWebEngineView):
        def __init__(self, url):
            self.html = None
            self.app = QApplication(sys.argv)
            QWebEngineView.__init__(self)
            self.loadFinished.connect(self._loadFinished)
            #self.setHtml(html)
            self.load(QUrl(url))
            self.app.exec_()

        def _loadFinished(self, result):
            # This is an async call, you need to wait for this
            # to be called before closing the app
            path = "/tmp/downloadedHtml.html"
            self.page().save(path)
            with open(path, "r") as myfile:
                data = myfile.read()
                self._callable(data)

        def _callable(self, data):
            self.html = data
            # Data has been stored, it's safe to quit the app
            self.app.quit()

    return Render(source_url).html


path = "/tmp/downloadedHtml.html"
url="https://www.google.com/maps/search/Restaurants/28047"
# renderUrl = render(url)
with open(path, "r") as myfile:
    renderUrl = myfile.read()
    renderedPage = htmlRenderer.fromstring(renderUrl)
dsfelems = renderedPage.xpath("//jsl/div[@role='listitem']")

print(elems)