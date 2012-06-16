from web.contrib.template import render_mako
import web
import logging
import csua_ldap
import user

urls = (
        '/?',             'main',
        '/login',         'login',
        '/logout',        'logout',
        '/exists/(.*)',   'finger',
       )

render = render_mako(
            directories=['templates'],
            input_encoding='utf-8',
            output_encoding='utf-8',
         )

class main:
  def __init__(this):
    this.title = "CSUA Account Form"
    this.token = csrf_token()
    this.loggedIn = user.isLoggedIn()

  def GET(this):
    if not user.isLoggedIn():
      raise web.seeother('/login')
    else:
      errors = []
      return render.main(**locals())

  def POST(this):
    if not user.isLoggedIn():
      raise web.seeother('/login')
    else:
      errors = []
      form = create_account_form()
      return render.main(**locals())

class login:
  def __init__(this):
    this.loggedIn = user.isLoggedIn()
    this.token = csrf_token()
    this.title = "Login Form - CSUA Acount Form"

  def GET(this):
    if user.isLoggedIn(): return web.seeother('/')
    errors = []
    data = web.input(password='', username='')
    return render.login(**locals())

  def POST(this):
    if user.isLoggedIn(): return web.seeother('/')
    data = web.input(password='', username='')
    errors = []

    logging.log('Checking login form')
    if not csua_ldap.checkUser(data.username):
      errors.append('User not found')
    elif not csua_ldap.checkLogin(data):
      errors.append('Password did not match')
    elif not this.token == data.authenticity:
      errors.append('Session expired')

    if len(errors) > 0:
      logging.warning('Login form error occurred, re-render')
      return render.login(**locals())
    else:
      logging.log('Login correct')
      user.logIn(data.username, data.password)
      return web.seeother('/')

class logout:
  def GET(this):
    if user.isLoggedIn():
      user.logOut()
    return web.seeother('/')

class finger:
  def GET(this, name):
    return str(subprocess.call(['id', name]))

app = web.application(urls, locals())

if web.config.get('_session') is None:
  session = web.session.Session(app, web.session.DiskStore('sessions'))
  web.config._session = session
else:
  session = web.config._session

def csrf_token():
  if not session.has_key('csrf_token'):
    from uuid import uuid4
    session.csrf_token=uuid4().hex
  return session.csrf_token
