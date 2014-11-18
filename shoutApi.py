from threading import Thread, Event
from HTMLParser import HTMLParser
from time import sleep
import urllib, urllib2, json, re, cookielib, traceback

class SendMessageException(Exception):
  def __init__(self, msg):
    self.msg = msg
  def __str__(self):
    return self.msg

class ChatReciever(Thread):
  def __init__(self, host, onMsg):
    Thread.__init__(self)
    self.onMsg = onMsg
    self.host = host
    self._stop = Event()
    self.start()
    
  def run(self):
    lastmsg = 0
    while 1:
      if self._stop.isSet(): break
      try:
        output = urllib2.urlopen(urllib2.Request(self.host+"/taigachat/list.json", urllib.urlencode({"lastrefresh":lastmsg})), timeout=10).read()
        new = bool(lastmsg)
        lastmsg = json.loads(output).get("lastrefresh")
        msglist = re.findall('<li.*?data-time="(.*?)".*?class="username" itemprop="name">(.*?)<\/a>.*?messagetext ugc\'>(.*?)</div> <\/li>', json.loads(output.replace("\\n","")).get("templateHtml"))
        for msg in msglist:
          self.onMsg(msg[0], HTMLParser().unescape(re.sub('<[^>]*>', '', msg[1])), HTMLParser().unescape(re.sub('<[^>]*>', '', re.sub('<img.*?alt="(.*?)".*?>',r'\1', msg[2]))), new)
      except:
        print traceback.format_exc()
      if self._stop.isSet(): break
      sleep(2)
      
  def stop(self):
    self._stop.set()
      
class ChatUserList(Thread):
  def __init__(self, host, onJoin, onLeave):
    Thread.__init__(self)
    self.users = []
    self.host = host
    self.onJoin = onJoin
    self.onLeave = onLeave
    self.lock = False
    self._stop = Event()
    self.start()
    
  def run(self):
    while 1:
      if self._stop.isSet(): break
      try:
        usersload = json.loads(urllib2.urlopen(urllib2.Request(self.host+"/shoutbox/", urllib.urlencode({"_xfResponseType":"json"})), timeout=10).read()).get("sidebarHtml")
        usersload = usersload[usersload.rfind('<!-- end block: sidebar_online_users -->'):]
        users = re.findall('class="username">(.*?)</a>', usersload)
        users = map(lambda x: HTMLParser().unescape(re.sub('<[^>]*>', '', x)), users)
        if users != self.users and users != [] and self.users != []:
          self.lock = True
          for a in users:
            try:
              self.users.remove(a)
            except ValueError:
              self.onJoin(a)
          for a in self.users:
            self.onLeave(a)
        if users != []: 
          self.users = users
          self.lock = False
      except:
        print traceback.format_exc()
      if self._stop.isSet(): break
      sleep(5)
      
  def list(self):
    while self.lock or self.users == []:
      sleep(0.1)
    return self.users
    
  def stop(self):
    self._stop.set()
    
class ChatUser(object):
  def __init__(self, host):
    object.__init__(self)
    self.host = host
    self.token = False
    self.cj = cookielib.LWPCookieJar()
    self.urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
    
  def login(self, login, password):
    if not self.isLoggedIn():
      token = self.urlopener.open(urllib2.Request(self.host+"/login/login", urllib.urlencode({"login":login, "password":password, "cookie_check":"0", "register":"0", "remember":"1"}))).read()
      token = token[token.find('name="_xfToken')+23:]
      self.token = token[:token.find('"')]
    else:
      pass
      
  def isLoggedIn(self):
    if self.token:
      page = self.urlopener.open(urllib2.Request(self.host+'/login/', urllib.urlencode({"_xfResponseType":"json", "_xfToken":self.token}))).read()
      if page.find('_redirect') > -1:
        return True
      else:
        self.token = False
        return False
    else:
      return False
      
  def logout(self):
    if self.token:
      self.urlopener.open("http://bukkit.pl/logout/?" + urllib.urlencode({"_xfResponseType":"json", "_xfToken":self.token}))
      self.token = False
      
  def send(self, msg):
    if self.token:
      page = self.urlopener.open(urllib2.Request("http://bukkit.pl/taigachat/post.json", urllib.urlencode({"message":msg, "_xfToken":self.token, "_xfResponseType":"xml"}))).read()
      if page.find('unrepresentable') == -1:
        err = 'Unable to send message: "'+msg+'"'
        raise SendMessageException(err)
    else:
      err = 'Not logged in'
      raise SendMessageException(err)