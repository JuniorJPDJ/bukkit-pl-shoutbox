import Tkinter as tk
import urllib2, urllib, cookielib, json, sys, thread, time, datetime, HTMLParser, tkMessageBox

cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)
lista1 = []

listref = 4
msgref = 2
timeout = 10

def logczas():
  return "[" + str(datetime.datetime.now().time())[0:-10]+ "] "

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
        wiad = wiad + unicode(line).encode("utf-8") + "\n"
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

class TextRedirector(object):
  def __init__(self, widget):
    self.widget = widget
  def write(self, str):
    self.widget.configure(state="normal")
    self.widget.insert("end", str)
    self.widget.see('end')
    self.widget.configure(state="disabled")


login = ''
pw = ''

class loginwindow(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)
    self.title('Logowanie do shoutboxa')
    self.resizable(0, 0)
    self.geometry('300x135')
    tk.Label(self, text="Zaloguj sie danymi z bukkit.pl\nJesli wpiszesz bledne dane lub zamkniesz to okno,\npoprostu nie bedziesz w stanie pisac na czacie").pack(side='top')
    loginframe = tk.Frame(self)
    tk.Label(loginframe, text="Login:", width=8).pack(side='left')
    loginbox = tk.Entry(loginframe, width=25)
    loginbox.pack(side="left")
    loginbox.focus()
    loginframe.pack(side='top', pady=2)
    pwframe = tk.Frame(self)
    tk.Label(pwframe, text="Haslo:", width=8).pack(side='left')
    pwbox = tk.Entry(pwframe, show='*', width=25)
    pwbox.pack(side='left')
    pwframe.pack(side='top')
    
    self.protocol("WM_DELETE_WINDOW", sys.exit)
    
    def log(*args):
      global login
      global pw
      login = loginbox.get()
      pw = pwbox.get()
      self.destroy()
      self.quit()
    loginbutton = tk.Button(self, text="Zaloguj", command=log, width=8).pack(side='top', pady=6)
    self.bind('<Return>', log)
    
loginwindow().mainloop()

try:
  token = urllib2.urlopen(urllib2.Request("http://bukkit.pl/login/login", urllib.urlencode({"login":login, "password":pw, "cookie_check":"0", "register":"0", "remember":"1"})), timeout=timeout).read()
  token = token[token.find('name="_xfToken')+23:]
  token = token[:token.find('"')]
except Exception as e:
  print(logczas() + "Blad logowania do czatu: " +  str(e))
  tkMessageBox.showerror("Blad logowania do czatu", "Blad logowania do czatu: " + str(e))
  sys.exit()

class chatwindow(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)
    text = tk.Text(self, wrap="word", bg='white', state="disabled")
    text.pack(side="top", fill="both", expand=True)
    self.title('Bukkit.pl shoutbox client by JuniorJPDJ v1.4')
    
    def send(*args):
      msg = unicode(msgbox.get()).encode("utf-8")
      msgbox.delete(0,'end')
      if msg == "/q" or msg == "/quit" or msg == "/exit":
        self.destroy()
        self.quit()
      elif msg == "/list" or msg == "/lista":
        playerlist("komenda")
      elif msg == "/ver" or msg == "/version":
        print(logczas() + "Posiadasz shoutbox bukkit.pl by JuniorJPDJ w wersji 1.4")
      else:
        try:
          urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/post.json", urllib.urlencode({"message":msg, "_xfToken":token, "_xfResponseType":"xml"})), timeout=timeout)
        except Exception as e:
          print(logczas() + "Blad wysylania wiadomosci: " +  str(e))
    
    przycisk = tk.Button(self, text="Wyslij", command=send, width=8)
    przycisk.pack(side="right")
    
    msgbox = tk.Entry(self)
    msgbox.pack(side="top", fill="both")
    msgbox.focus()
        
    sys.stdout = TextRedirector(text)
    
    self.bind('<Return>', send)
    
    self.update()
    self.minsize(self.winfo_width(), self.winfo_height())
    
    def getmsg(*args):
      ref = 0
      err = False
      while 1:
        try:
          output = urllib2.urlopen(urllib2.Request("http://bukkit.pl/taigachat/list.json", urllib.urlencode({"_xfToken":token, "_xfResponseType":"json", "lastrefresh":ref})), timeout=timeout).read()
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
        time.sleep(msgref)

    def playerlist(*args):
      while 1:
        global lista
        global licz
        global dodaj
        lista = []
        licz = -1
        dodaj = False
        try:
          listparse().feed(json.loads(urllib2.urlopen(urllib2.Request("http://bukkit.pl/shoutbox/", urllib.urlencode({"_xfResponseType":"json", "_xfToken":token,})), timeout=timeout).read()).get("sidebarHtml"))
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
          time.sleep(listref)

    thread.start_new_thread(getmsg, ("", ""))
    thread.start_new_thread(playerlist, ("diff", ""))
    
    self.wm_attributes("-topmost", 1)
    msgbox.focus_force()

chatwindow().mainloop()
urllib2.urlopen("http://bukkit.pl/logout/?" + urllib.urlencode({"_xfToken":token}), timeout=timeout)
sys.exit()