from urlpath import URL
import re


def isValidVidUrl(url: str) -> bool:
    """Check if the given Url is a valid Vidstream Url"""
    obj = URL(url)
    return obj.drive.find("vidstream") == 8 and bool(re.match(r"^/f/(\w|[0-9])+", obj.path))


def isSeriesOrMovie(url: str) -> bool:
    """Check if the given Url points to a series or a movie"""
    obj = URL(url)
    return obj.path.find('season') == 1 or obj.path.find('movie') == 1


def getDomain(url: str) -> str:
    obj = URL(url)
    return obj.drive


def stripOfQuery(url: str) -> str:
    obj = URL(url)
    return obj.drive+obj.path
