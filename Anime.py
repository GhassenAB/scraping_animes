from regex import regex
from bs4 import BeautifulSoup


class Anime:
    def __init__(self, title, link, imageUrl):
        self.title = title
        self.link = link
        self.imageUrl = imageUrl

    def tojson(self):
        return {
            'title': regex.sub(' +', ' ', self.title.strip()),
            'link': self.link,
            'cover': self.imageUrl,
            'details': self.details,
            'screens': self.screens,
            'links': self.links
        }


def getnamesandlinks(names_links, animes):
    for result in names_links:
        animes.append(Anime(result.get('title'), result.get('href'), ''))
    return animes


def getimageslinks(images, animes):
    x = 0
    for result in images:
        animes[x].imageUrl = result.find('meta').get('content')
        x += 1
    return animes


def getjson(animes):
    alist = []
    for anime in animes:
        alist.append(anime.tojson())
    return alist
