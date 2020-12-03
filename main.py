import requests
from Anime import getnamesandlinks, getimageslinks, getjson
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


app.run()
