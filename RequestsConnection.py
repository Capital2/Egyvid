import requests
import UrlOperations

EgybestAd = '/click.php'


def makeSession() -> requests.sessions.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"})
    return s


def getPage(url: str, timeout: float = 5, session: requests.sessions.Session = makeSession()) -> str:
    try:
        return session.get(url, timeout=timeout).text
    except requests.exceptions.ConnectionError:
        return None


def prepSession(url: str, s: requests.sessions.Session) -> None:
    """get the headers of 2 ads"""
    link = UrlOperations.getDomain(url) + EgybestAd
    s.head(link)
    s.head(link)
