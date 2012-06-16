#!/usr/bin/env python

from web import form
from web.contrib.template import render_mako
import hashlib
import ldap
import os
import subprocess
import sys
import web
import inspect

urls = (
        '/accountant/?', 'main',
        '/accountant/login', 'login',
        '/accountant/logout', 'logout',
        '/accountant/exists/(.*)', 'finger',
        '/favicon.ico', 'favicon',
        '/(js|css|images)/(.*)', 'media'
)

app = web.application(urls, globals())
render = render_mako(
            directories=['templates'],
            input_encoding='utf-8',
            output_encoding='utf-8',
         )

if web.config.get('_session') is None:
  session = web.session.Session(app, web.session.DiskStore('sessions'))
  web.config._session = session
else:
  session = web.config._session

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

  def disable(self):
    self.HEADER = ''
    self.OKBLUE = ''
    self.OKGREEN = ''
    self.WARNING = ''
    self.FAIL =   ''
    self.ENDC = ''

  def color(text, c):
    return c + text + ENDC

def csrf_token():
  if not session.has_key('csrf_token'):
    from uuid import uuid4
    session.csrf_token=uuid4().hex
  return session.csrf_token

def log(message):
  parent = inspect.stack()[1]
  print '[%s%s:%d%s]: %s' % (bcolors.OKGREEN, parent[3], parent[2],
                             bcolors.ENDC, str(message))

def warning(message, fromException = True):
  parent = inspect.stack()[1]
  print '[%s%s:%d%s]: %s' % (bcolors.WARNING, parent[3], parent[2],
                             bcolors.ENDC, str(message))

def error(message, fromException = True):
  parent = inspect.stack()[1]
  print '[%s%s:%d%s]: %s' % (bcolors.FAIL, parent[3], parent[2], 
                             bcolors.ENDC, str(message))

ldapURI = 'ldaps://ldap.CSUA.berkeley.EDU:636/'
ldapBindUser = 'cn=root,dc=CSUA,dc=Berkeley,dc=EDU'
salt = 'LDAP'
ldapTrace = 0

def getLDAPCredentials():
  ldapBindPw = os.popen('ssh root@soda cat /etc/libnss-ldap.secret').read().strip()
  # FIXME Why can't we ssh to root@soda from soda?
  warning('Fix this function')
  #ldapBindPw = os.popen('ssh mail ssh root@soda cat /etc/libnss-ldap.secret').read().strip()
  return (ldapBindUser, ldapBindPw)

def initLDAP():
  log('Loading Credentials')
  (bindUser, bindPw) = getLDAPCredentials()
  if bindUser == '' or bindPw == '':
    error('Could not get credentials')
    sys.exit(1)
  try:
    log('Connecting to server')
    ldapC = ldap.initialize(ldapURI, ldapTrace, sys.stderr)
    log('Signing in to the server')
    ldapC.simple_bind_s(bindUser, bindPw)
  except ldap.LDAPError, e:
    error(e.desc)
    sys.exit(1)
  return ldapC

ldapConnection = initLDAP()

def getLDAPUser(username):
  try:
    log('Retrieving user ' + username)
    result = ldapConnection.search_s("ou=People,dc=CSUA,dc=Berkeley,dc=EDU", ldap.SCOPE_SUBTREE, '(uid=' + username + ')')
    retval = None
    if len(result) > 0:
      retval = result[0][1]
    else:
      warning('User ' + username + ' not found')
    return retval
  except ldap.LDAPError, e:
    error(e.desc)
    sys.exit(1)
  except Exception, e:
    warning(e)
  return None
  
def checkLDAPUser(username):
  return getLDAPUser(username) != None

def checkLDAPLogin(data):
  user = getLDAPUser(data.username)
  log('Checking if password is correct')
  return user != None and user['userPassword'][0] == data.password

def checkNewUser(username):
  return not checkLDAPUser(username)

create_account_form = form.Form(
                   form.Textbox('username',
                        form.Validator('Username Taken.', checkNewUser),
                        description='Username:'),
                   form.Password('password1',
                        description='Password:'),
                   form.Password('password2',
                        description='Retype Password:'),
                   form.Textbox('email1',
                        description='Email:'),
                   form.Textbox('email2',
                        description='Retype Email:'),
                   validators = [
                      form.Validator("Passwords did not match", lambda x:
                                     x.password1 == x.password2)
    ])

c_login = 'Borborygmous'
c_uname = 'Woebegone'
c_password = 'Sphygmomanometer'
c_hash = 'Perspicacity'

def isLoggedIn():
  c = web.cookies()
  if c.get(c_login) != 'true': return False
  h = hashlib.new('ripemd160')
  h.update(c.get(c_uname))
  h.update(salt)
  h.update(c.get(c_password))
  return h.hexdigest() == c.get(c_hash)

def logIn(username, password):
  log('User: ' + username)
  p = hashlib.md5()
  p.update(password)
  password = p.hexdigest()

  h = hashlib.new('ripemd160')
  h.update(username)
  h.update(salt)
  h.update(password)
  web.setcookie(c_password, password)
  web.setcookie(c_uname, username)
  web.setcookie(c_hash, h.hexdigest())
  web.setcookie(c_login, 'true')

def logOut():
  log('User: ' + web.cookies().get(c_uname))
  web.setcookie(c_password, '')
  web.setcookie(c_uname, '')
  web.setcookie(c_hash, '')
  web.setcookie(c_login, '')

class main:
  def __init__(this):
    this.title = "CSUA Account Form"
    this.token = csrf_token()
    this.loggedIn = isLoggedIn()

  def GET(this):
    if not isLoggedIn():
      raise web.seeother('/accountant/login')
    else:
      errors = []
      return render.main(**locals())

  def POST(this):
    if not isLoggedIn():
      raise web.seeother('/accountant/login')
    else:
      errors = []
      form = create_account_form()
      return render.main(**locals())

class login:
  def __init__(this):
    this.loggedIn = isLoggedIn()
    this.token = csrf_token()
    this.title = "Login Form - CSUA Acount Form"

  def GET(this):
    if isLoggedIn(): return web.seeother('/accountant')
    errors = []
    data = web.input(password='', username='')
    return render.login(**locals())

  def POST(this):
    if isLoggedIn(): return web.seeother('/accountant')
    data = web.input(password='', username='')
    errors = []

    log('Checking login form')
    if not checkLDAPUser(data.username):
      errors.append('User not found')
    elif not checkLDAPLogin(data):
      errors.append('Password did not match')
    elif not this.token == data.authenticity:
      errors.append('Session expired')

    if len(errors) > 0:
      warning('Login form error occurred, re-render')
      return render.login(**locals())
    else:
      log('Login correct')
      logIn(data.username, data.password)
      return web.seeother('/accountant')

class logout:
  def GET(this):
    if isLoggedIn():
      logOut()
    return web.seeother('/accountant')

class finger:
  def GET(this, name):
    return str(subprocess.call(['id', name]))

class favicon:
  def GET(this):
    f = open('static/favicon.ico', 'r')
    return f.read()

class media:
  def GET(this, folder, fname):
    try:
      f = open('static/' + folder + '/' + fname, 'r')
      return f.read()
    except:
      return app.notfound()

if __name__ == "__main__":
  app.run()
