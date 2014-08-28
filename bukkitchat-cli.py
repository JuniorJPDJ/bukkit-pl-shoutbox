#!/usr/bin/python
import urllib2, urllib, cookielib, json, sys, thread, getpass, time, datetime, HTMLParser

cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

line = ""
pisz = False
class msgp(HTMLParser.HTMLParser):
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
      global line
      global czas
      global pisz
      pisz = False
      if czas != "":
        line = "[" + czas + "] " + line
        czas = ""
        print unicode(line).encode("utf-8")
      line = ""

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
      output = urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/list.json", urllib.urlencode({"_xfToken":token, "_xfResponseType":"json", "lastrefresh":ref}))).read()
      msgp().feed(json.loads(output).get("templateHtml").replace("\n",""))
      ref = json.loads(output).get("lastrefresh")
      if err:
        print("[" + str(datetime.datetime.now().time())[0:-10]+ "] Pomyslnie pobrano zalegle wiadomosci")
        err = False
    except Exception as e:
      if not err:
        print("[" + str(datetime.datetime.now().time())[0:-10]+ "] Blad pobierania wiadomosci: " +  str(e))
      err = True
    time.sleep(1)

thread.start_new_thread(getmsg, ("", ""))

while 1:
  try:
    msg = raw_input()
  except:
    exit()
  if msg == "/q" or msg == "/quit" or msg == "/exit":
    exit()
  urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/post.json", urllib.urlencode({"message":msg, "_xfToken":token, "_xfResponseType":"xml"})))