import hashlib
import logging
import web

c_login = 'Borborygmous'
c_uname = 'Woebegone'
c_password = 'Sphygmomanometer'
c_hash = 'Perspicacity'

salt = 'LDAP'

def isLoggedIn():
  c = web.cookies()
  if c.get(c_login) != 'true': return False
  h = hashlib.new('ripemd160')
  h.update(c.get(c_uname))
  h.update(salt)
  h.update(c.get(c_password))
  return h.hexdigest() == c.get(c_hash)

def logIn(username, password):
  logging.log('User ' + username)
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
  logging.log('User ' + web.cookies().get(c_uname))
  web.setcookie(c_password, '')
  web.setcookie(c_uname, '')
  web.setcookie(c_hash, '')
  web.setcookie(c_login, '')
