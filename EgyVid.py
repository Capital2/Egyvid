from urlpath import URL
import requests
from bs4 import BeautifulSoup as bs
import js2py
import json

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def tols(html, ls):
    soup = bs(html, features="lxml")
    for l in soup.find_all("a", {"class" : "movie"}):
        ls.append([l.find('span', {"class" : "title"}).get_text(), l["href"]])
    return ls    
        
def dirurl(s, url):
    r=s.get(url)
    soup = bs(r.content, features="lxml")
    url=egy+soup.find("a", {"class": "nop btn g dl _open_window"})["data-url"]
    r=s.get(url)
    return r.url[:r.url.find("/?")]

def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

egy = "https://room.egybest.biz"
search = "/explore/?q="
auto = "/autoComplete.php?q="
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"}) #egybest does not look at the user agent but maybe they will someday idk lol

# n7assnou sira bechwaya ads
try :
    s.head(egy+"/click.php")
    s.head(egy+"/click.php")
except ConnectionError :
    print("please verify your internet connection before continuing")
    exit(1)

term = input("movie: ")

#autoComplete.php
r=s.get(egy+auto+term)
ls = json.loads(r.content)
cpt=0
url=""
th = False
if len(ls[term]) :
    for i in ls[term]:
        cpt = cpt + 1
        print(str(cpt)+':'+ i['t'])
    while True:
        ch = input("choose a movie or try a thorough search (1,2,.../s)?: ")
        if is_number(ch):
            try:
                url=egy+"/"+ls[term][int(ch)-1]['u']
                url = dirurl(s, url)
                break
            except:
                print("try again")      
        elif ch == 's':
            th = True
            break
        else:
            print("try again")
else:
    th = True
    
#thorough search 
if th:
    ls = []
    pg=0
    url = ""
    while 1:
        pg=pg+1
        r=s.get(egy+search+term+"&page="+str(pg))
        tols(r.content, ls)
        if not len(ls):
            print("no matches")
            break
        else:
            for i in range(len(ls)):
                print(str(i+1) +": "+ ls[i][0])
            ch = input("choose a movie or continue ?: ")
            try:
                if int(ch) in range(len(ls)+1):
                    url = dirurl(s, ls[int(ch)-1][1])
                    break
            except ValueError:
                print("continuing")
#---------second act---------
if not url :
    exit(0)

urlobj = URL(url)
adurl= urlobj.drive + "/cv.php"

#--------------part1: the verfy url------------------
r = requests.get(url)
soup = bs(r.content, features="lxml")

#func is :
func = soup.find("script").get_text()
    
#to scrape the operations:
op = func[func.find("a0c();") + 6 :]
op = op[:op.find("$(")]

#(delete that navigator check var)
nav = op[op.find("var ismob") :]
nav = nav[:nav.find(";")+1]
op = op.replace(nav, '')

#now to change the main variables' names using findnth()
it=[2,4,5]
nama=["mainverif", "btab", "stab"]
outt=[]
for i in range(3):
    outt.append(op[findnth(op, "var", it[i])+4 :])
    outt[i] = outt[i][: outt[i].find("=")]
    op = op.replace(outt[i], nama[i])


#a0b is normally this :
a0b = "var a0b = function(a, b) {a = a - 0x0;var c = a0a[a];return c;};"
    
#find the a0a array:
a0a = func[func.find("var a0a") : func.find("(function(a,b)")]

#finding the rotation constant
rot = func[func.find("d();")+10:]
rot = rot[:rot.find(")")]

#javascript for rotating a0a
rota0a = "for (i=0; i<"+ rot +"; i++){a0a.push(a0a.shift());}"

payload = """function payload(){ for(var c = 0x0; c <= stab["length"]; c++){mainverif += btab[stab[c]] || '';} return mainverif;}"""

#scraping the unique id from the ajax method
uniqid = func[func.find("$["):]
uniqid = uniqid[uniqid.find("data")+8:uniqid.find("}")-6]
#js2py.translate_file("f.js", "preparePayload.py")
verif = js2py.eval_js(a0a + rota0a + a0b + op + payload + "payload()")
godallmighty = adurl+"?verify="+verif

#---------------part2: the verify post request--------------
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"} ) 
pos= {uniqid : 'ok'}

s.head(adurl)#get the cookies for them ads
#we verify that we have watched the ad
s.post(godallmighty, data=pos, headers = {"X-Requested-With": "XMLHttpRequest"})
r=s.get(url)

#---------------part3: the juicy download url-------------
soup = bs(r.content, features="lxml")
DLlink = soup.find("a", {'class':'bigbutton'})["href"]
print(DLlink)