import json
import re

import requests
from Anime import getnamesandlinks, getimageslinks, getjson, Anime
from bs4 import BeautifulSoup
import flask

from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/search', methods=['GET'])
def search():
    animes = []
    tag = request.args['tag'].strip().replace(' ', '+')
    page = requests.get("https://w.animesanka.com/search?q={}".format(tag))
    soup = BeautifulSoup(page.content, 'html.parser')
    names_links = soup.find_all('a', class_="RecentThumb")
    getnamesandlinks(names_links, animes)
    images = soup.find_all('div', itemprop="image", itemscope="itemscope")
    getimageslinks(images, animes)
    if len(animes) > 0:
        return jsonify(getjson(animes))
    else:
        return jsonify([{"message": f"there is no such anime called '{tag.replace('+', ' ')}'"}])


@app.route('/details', methods=['GET'])
def details():
    anime = Anime('title', 'link', 'imagecover')
    screens = []
    detail = {}
    links = {}

    url = request.args['url'].strip()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    """Anime name"""
    title = soup.find('i', class_="sh-msg short-success").text
    title = re.sub(
        '[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', u'', title)
    anime.title = re.sub(' +', ' ', title)

    """link"""
    anime.link = url

    """Anime Cover"""
    cover = soup.find('link', rel="image_src").get('href')
    anime.imageUrl = cover

    """Details"""
    table = soup.find(id="content1-sanka").find('table')
    cols = table.findAll("tr")
    for col in cols:
        detail[col.find('th').text.strip()] = col.find('td').text.strip()

    """Screens"""
    for screen in soup.find(id="content4-sanka").findAll('a'):
        screens.append(screen.get('href'))

    """Links"""
    url_links = soup.find('a', class_="ibtn iPrev ibtn-4").get('href')

    if url_links.find('tube.animesanka.com') != -1:
        url_links = url_links.replace(
            'tube.animesanka.com', 'www.animesanka.club')
    elif url_links.find('tv.animesanka.net') != -1:
        url_links = url_links.replace(
            'tv.animesanka.net', 'www.animesanka.club')

    page = requests.get(url_links)
    soup = BeautifulSoup(page.content, 'html.parser')

    all_links = soup.findAll('option', attrs={"data-links": True})

    for link in all_links:
        direct_links = {}
        stream_links = {}

        list = link.get('data-links').split()
        for x in list:
            if x.find('@http') != -1:
                host = x.split("@")[0].split("-")[0]
                links.setdefault(host, {})
                direct_links = links[host]
                direct_links[x.split("@")[0].split("-")[2]] = x.split("@")[1]
                links[host] = direct_links

    anime.details = detail
    anime.screens = screens
    anime.links = links

    return json.dumps(anime.tojson())


app.run()
