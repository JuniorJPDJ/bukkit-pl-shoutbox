#!/usr/bin/python

import urllib2, urllib, cookielib, json, sys, thread, getpass, time, datetime, HTMLParser

cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
lista1 = []

if sys.platform == "win32":
  encoding = sys.stdout.encoding
else:
  encoding = "utf-8"

class msgparse(HTMLParser.HTMLParser):
  def handle_starttag(self, tag, attrs):
    for attr in attrs:
      if attr[0] == "data-timestring":
        global czas
        czas = attr[1]
      elif attr[1] == "username":
        global pisz
        pisz = True
      elif attr[0] == "alt":
        if pisz:
          global line
          line = line + attr[1]
  def handle_data(self, data):
    global line
    global pisz
    if pisz:
      line = line + data
  def handle_endtag(self, tag):
    if tag == "li":
      global pisz
      global czas
      pisz = False
      if czas != "":
        global line
        global wiad
        line = "[" + czas + "] " + line
        czas = ""
        wiad = wiad + unicode(line).encode(encoding) + "\n"
      line = ""
      
class listparse(HTMLParser.HTMLParser):
  def handle_starttag(self, tag, attrs):
    global licz
    for attr in attrs:
      if attr[1] == 'listInline':
        licz = licz + 1
      elif attr[1] == 'username':
        if licz == 1:
          global dodaj
          dodaj = True
  def handle_endtag(self, tag):
    global dodaj
    dodaj = False
  def handle_data(self, data):
    if dodaj:
      global lista
      lista.append(data)

def logczas():
  return "[" + str(datetime.datetime.now().time())[0:-10]+ "] "

print "Zaloguj sie danymi z bukkit.pl"
print "Jesli wpiszesz bledne dane poprostu nie bedziesz w stanie pisac na czacie"
print "PS. Hasla nie widac podczas jego wpisywania"
login = raw_input("Login: ")
pw = getpass.getpass("Haslo: ")

token = urllib2.urlopen(urllib2.Request("http://bukkit.pl/login/login", urllib.urlencode({"login":login, "password":pw, "cookie_check":"0", "register":"0", "remember":"1"}))).read()
token = token[token.find('name="_xfToken')+23:]
token = token[:token.find('"')]

def getmsg(*args):
  ref = 0
  err = False
  while 1:
    try:
      output = urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/list.json", urllib.urlencode({"_xfToken":token, "_xfResponseType":"json", "lastrefresh":ref})), timeout=10).read()
      global line
      global pisz
      global wiad
      line = ""
      pisz = False
      wiad = ""
      msgparse().feed(json.loads(output.replace("\\n","")).get("templateHtml"))
      if wiad != "":
        print(wiad),
      ref = json.loads(output).get("lastrefresh")
      if err:
        print(logczas() + "Pomyslnie pobrano zalegle wiadomosci")
        err = False
    except KeyboardInterrupt:
      pass
    except Exception as e:
      if not err:
        print(logczas() + "Blad pobierania wiadomosci: " +  str(e))
      err = True
    time.sleep(2)

def playerlist(*args):
  while 1:
    global lista
    global licz
    global dodaj
    lista = []
    licz = -1
    dodaj = False
    try:
      listparse().feed(json.loads(urllib2.urlopen(urllib2.Request("http://bukkit.pl/shoutbox/", urllib.urlencode({"_xfResponseType":"json", "_xfToken":token,})), timeout=10).read()).get("sidebarHtml"))
    except Exception as e:
      print(logczas() + "Blad podczas pobierania listy uzytkownikow: " +  str(e))
    lista.sort()
    global lista1
    if lista1 != lista and lista1 != []:
      for a in lista:
        try:
          lista1.remove(a)
        except ValueError:
          print(logczas() + a + " dolaczyl do czatu")
      for a in lista1:
         print(logczas() + a + " opuscil czat")
    lista1 = lista
    if args[0] == "komenda":
      print(logczas() + "Aktualnie z czatu korzystaja: ")
      strlista = ""
      for a in lista:
        strlista = strlista + a + " "
      print(logczas() + strlista)
      break
    else:
      time.sleep(4)

thread.start_new_thread(getmsg, ("", ""))
thread.start_new_thread(playerlist, ("diff", ""))

while 1:
  try:
    #msg = raw_input()
    msg = unicode(str(raw_input()).decode(encoding)).encode("utf-8")
  except:
    sys.exit()
  if msg == "/q" or msg == "/quit" or msg == "/exit":
    urllib2.urlopen("http://bukkit.pl/logout/?" + urllib.urlencode({"_xfToken":token}), timeout=10)
    sys.exit()
  elif msg == "/list" or msg == "/lista":
    playerlist("komenda")
  else:
    try:
      urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/post.json", urllib.urlencode({"message":msg, "_xfToken":token, "_xfResponseType":"xml"})), timeout=10)
    except Exception as e:
      print(logczas() + "Blad wysylania wiadomosci: " +  str(e))
      