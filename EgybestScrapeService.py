import re
import bs4.element
import RequestsConnection
from bs4 import BeautifulSoup as Bs
import UrlOperations
from Exceptions import *


def _bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile(r'(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)  # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)  # convert newlines to spaces
    # this preserves newline delimiters
    html = re.sub(r'[\s]+<', '<', html)  # remove whitespaces before opening tags
    html = re.sub(r'>[\s]+', '>', html)  # remove whitespaces after closing tags
    return html


def _MovieTableToDict(movietable: bs4.element.Tag, isseriesormovie: bool) -> dict:
    """Parse the egybest movie table into a dictionary"""
    keys = ['language', 'rating', 'genre', 'review', 'duration', 'quality', 'translator']
    if not isseriesormovie:
        keys.insert(0, 'Series')
    it = keys.__iter__()
    ret = {'title': movietable.find("tr").td.get_text()}
    for tag in movietable.find("tr").next_siblings:
        ret[it.__next__()] = tag.td.next_sibling.get_text()
    return ret


def getVidstreamLink(apiurl: str, session) -> str:
    retries = 3
    vidurl = session.get(apiurl).url
    # test if the Api gives us access to the url if not, open some ads
    while retries:
        if UrlOperations.isValidVidUrl(vidurl):
            return UrlOperations.stripOfQuery(vidurl)
        else:
            RequestsConnection.prepSession(apiurl, session)
            vidurl = session.get(apiurl).url
            retries = retries - 1
    # if not retries:
    #     raise EgybestApiNotResponding(vidurl)


class Base:
    def __init__(self, url: str):
        self.url = url
        self.session = RequestsConnection.makeSession()
        # egybest does not look at the user agent but maybe they will someday idk lol
        self.session.headers.update({
                             "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"})
        html = RequestsConnection.getPage(self.url, 5, self.session)
        self.soup = Bs(_bs_preprocess(html), features="lxml")
        self.info = _MovieTableToDict(self.soup.find('table', {'class': 'movieTable full'}),
                                      UrlOperations.isSeriesOrMovie(self.url))
        self.info['movie_img'] = self.soup.find('div', {'class': 'movie_img'}).img['src']

    def dlTableToList(self, dltable: bs4.element.Tag) -> list:
        """Parse the egybest download options table into a list"""
        keys = ['method', 'quality', 'size', 'link']
        trgen = dltable.tbody.children
        ret = []
        for tr in trgen:
            tdresultset = tr.find_all('td')
            apipath = tdresultset[3].find('a')['data-url']
            fullpath = UrlOperations.getDomain(self.url) + apipath

            temp = {keys[3]: getVidstreamLink(fullpath, self.session) or fullpath}
            for i in range(3):
                temp[keys[i]] = tdresultset[i].get_text()
            ret.append(temp)
        # recheck links
        for i in ret:
            if not UrlOperations.isValidVidUrl(i['link']):
                i['link'] = getVidstreamLink(i['link'], self.session)
        return ret


class Episode(Base):
    def __init__(self, url: str):
        super(Episode, self).__init__(url)
        self.dl = None

    def getDl(self):
        self.dl = self.dlTableToList(self.soup.find('table', {'class': 'dls_table btns full mgb'}))
        return self.dl


class Season(Base):
    def __init__(self, url: str):
        super(Season, self).__init__(url)
        self.synopsis = self.soup.find('strong', text='القصة').find_parent().next_sibling.get_text()
        self.episodes = {}

    def getAllEpisodes(self) -> dict:
        ls = self.soup.find('div', {'class': 'movies_small'}).findChildren('a')
        key = len(ls) + 1
        for tag in ls:
            key = key - 1
            if key not in self.episodes.keys():
                self.episodes[key] = Episode(tag['href'])
        return self.episodes

    def getEpisodeByNum(self, num: int) -> Episode:
        if num not in self.episodes.keys():
            ls = self.soup.find('div', {'class': 'movies_small'}).findChildren('a')
            antinum = num - 2*num
            self.episodes[num] = Episode(ls[antinum]['href'])
        return self.episodes[num]


class Series(Base):
    def __init__(self, url: str):
        super(Series, self).__init__(url)
        self.synopsis = self.soup.find('strong', text='القصة').find_parent().next_sibling.get_text()
        self.seasons = {}

    def getAllSeasons(self) -> dict:
        ls = self.soup.find('div', {'class': 'contents movies_small'}).findChildren('a')
        key = len(ls) + 1
        for tag in ls:
            key = key - 1
            if key not in self.seasons.keys():
                self.seasons[key] = Season(tag['href'])
        return self.seasons

    def getSeasonByNum(self, num: int) -> Season:
        if num not in self.seasons.keys():
            ls = self.soup.find('div', {'class': 'movies_small'}).findChildren('a')
            antinum = num - 2*num
            self.seasons[num] = Season(ls[antinum]['href'])
        return self.seasons[num]


class Movie(Base):
    def __init__(self, url: str):
        super(Movie, self).__init__(url)
        self.synopsis = self.soup.find('strong', text='القصة').find_parent().next_sibling.get_text()
        self.dl = self.dlTableToList(self.soup.find('table', {'class': 'dls_table btns full mgb'}))
