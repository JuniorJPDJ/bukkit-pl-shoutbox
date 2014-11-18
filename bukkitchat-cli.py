#!/usr/bin/python
# coding: utf-8 
import datetime, sys, shoutApi, time
from threading import Thread

chathost = "http://bukkit.pl"
logged = False
quit = False

if sys.platform == "win32":
  encoding = sys.stdout.encoding
else:
  encoding = "utf-8"

class asyncRun(Thread):
  def __init__(self, what, *args):
    Thread.__init__(self)
    self.what = what
    self.args = args
    self.start()
  def run(self):
    self.what(*self.args)

def printP(msg):
  print(unicode(msg).encode(encoding))

def send(msg):
  if logged:
    User.send(unicode(msg).encode('utf-8'))
  else:
    printP(u'[INFO] Przed wysłaniem wiadomości zaloguj się do czatu za pomocą komendy "/login"!')

def onJoin(nick):
  printP(datetime.datetime.now().strftime('[%H:%M:%S] ') + nick + u' dołączył do czatu')

def onLeave(nick):
  printP(datetime.datetime.now().strftime('[%H:%M:%S] ') + nick + u' opuścił czat')

def onMsg(time, sender, msg, new):
  printP(datetime.datetime.fromtimestamp(int(time)).strftime('[%H:%M:%S] ')+sender+': '+msg)

def Quit():
  global quit
  quit = True
  printP(u'[INFO] Trwa wyłączanie klienta')
  List.stop()
  Reciever.stop()
  User.logout()

def onCommand(command, args):
  if command.lower() == 'help' or command.lower() == 'h':
    printP(u"[INFO] Lista dostępnych komend:\n"
           u"[INFO] /l lub /login - pozwala się zalogować\n"
           u"[INFO] /lo lub /logout - pozwala się wylogować\n"
           u"[INFO] /ls lub /list - wyswietla liste graczy\n"
           u"[INFO] /h lub /help - wyświetla ten komunikat\n"
           u"[INFO] /q lub /quit - wyłącza czat\n"
           u"[INFO] /ver lub /version - wyświetla wersję programu")
  elif command.lower() == 'l' or command.lower() == 'login':
    if len(args) == 2:
      global logged
      if not logged:
        User.login(args[0], args[1])
        if User.isLoggedIn:
          logged = True
          printP(u'[INFO] Zalogowano pomyślnie!')
        else:
          printP(u'[INFO] Błąd logowania, spróbuj ponownie')
      else:
        printP(u'[INFO] Jesteś już zalogowany, najpierw się wyloguj!')
    else:
      printP(u'[INFO] Błędne użycie komendy /login\n'
             u'[INFO] Prawidłowe użycie: "/login NICK HASŁO"')
  elif command.lower() == 'lo' or command.lower() == 'logout':
    if not logged:
      User.logout()
      printP(u'[INFO] Wylogowano!')
    else:
      printP(u'[INFO] Przed wylogowaniem, wypadałoby się zalogować ;)')
  elif command.lower() == 'quit' or command.lower() == 'q':
    Quit()
  elif command.lower() == 'list' or command.lower() == 'ls':
    usrlist = u''
    for usr in List.list():
      usrlist += u' ' + usr
    printP(u'[INFO] Lista osób uczestniczących w czacie:'+usrlist)
  elif command.lower() == 'version' or command.lower() == 'ver':
    printP(u'[INFO] Posiadasz shoutbox bukkit.pl by JuniorJPDJ w wersji 2.0')
  else:
    printP(u'[INFO] Nie ma takiej komendy ;c')

User = shoutApi.ChatUser(chathost)
Reciever = shoutApi.ChatReciever(chathost, onMsg)
List = shoutApi.ChatUserList(chathost, onJoin, onLeave)

while 1:
  try:
    if quit: break
    msg = raw_input().decode(encoding)
    if msg.find('/') == 0:
      args = msg.split(' ')
      onCommand(args[0][1:], args[1:])
    else:
      asyncRun(send, msg)
  except:
    Quit()
sys.exit()