import requests
from bs4 import BeautifulSoup as Bs
import UrlOperations
import js2py


def findnth(haystack, needle, n):
    parts = haystack.split(needle, n+1)
    if len(parts) <= n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)


def extractDownloadLink(url: str) -> str:
    """extracts the download link """
    adurl = UrlOperations.getDomain(url) + "/cv.php"
    # --------------part1: the verfy url------------------
    r = requests.get(url)
    soup = Bs(r.content, features="lxml")

    # func is :
    func = soup.find("script").get_text()

    # to scrape the operations:
    op = func[func.find("a0c();") + 6:]
    op = op[:op.find("$(")]

    # (delete that navigator check var)
    nav = op[op.find("var ismob"):]
    nav = nav[:nav.find(";") + 1]
    op = op.replace(nav, '')

    # now to change the main variables' names using findnth()
    it = [2, 4, 5]
    nama = ["mainverif", "btab", "stab"]
    outt = []
    for i in range(3):
        outt.append(op[findnth(op, "var", it[i]) + 4:])
        outt[i] = outt[i][: outt[i].find("=")]
        op = op.replace(outt[i], nama[i])

    # a0b is normally this :
    a0b = "var a0b = function(a, b) {a = a - 0x0;var c = a0a[a];return c;};"

    # find the a0a array:
    a0a = func[func.find("var a0a"): func.find("(function(a,b)")]

    # finding the rotation constant
    rot = func[func.find("d();") + 10:]
    rot = rot[:rot.find(")")]

    # javascript for rotating a0a
    rota0a = "for (i=0; i<" + rot + "; i++){a0a.push(a0a.shift());}"

    payload = """function payload(){ for(var c = 0x0; c <= stab["length"]; c++){mainverif += btab[stab[c]] || '';} return mainverif;}"""

    # scraping the unique id from the ajax method
    uniqid = func[func.find("$["):]
    uniqid = uniqid[uniqid.find("data") + 8:uniqid.find("}") - 6]
    # js2py.translate_file("f.js", "preparePayload.py")
    verif = js2py.eval_js(a0a + rota0a + a0b + op + payload + "payload()")
    godallmighty = adurl + "?verify=" + verif

    # ---------------part2: the verify post request--------------
    s = requests.Session()
    s.headers.update({
                         "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"})
    pos = {uniqid: 'ok'}

    s.head(adurl)  # get the cookies for them ads
    # we verify that we have watched the ad
    s.post(godallmighty, data=pos, headers={"X-Requested-With": "XMLHttpRequest"})
    r = s.get(url)

    # ---------------part3: the juicy download url-------------
    soup = Bs(r.content, features="lxml")
    return soup.find("a", {'class': 'bigbutton'})["href"]


