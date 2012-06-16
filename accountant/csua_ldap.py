import ldap
import logging
import os
import sys

ldapURI = 'ldaps://ldap.CSUA.berkeley.EDU:636/'
ldapBindUser = 'cn=root,dc=CSUA,dc=Berkeley,dc=EDU'
salt = 'LDAP'
ldapTrace = 0

def getCredentials():
  command = []
  if os.uname()[1] == 'soda':
    logging.warning('Fix this function')
    command.append('ssh mail')
  command.append('ssh root@soda')
  command.append('cat /etc/libnss-ldap.secret')
  logging.log('Executing: ' + ' '.join(command))
  ldapBindPw = os.popen(' '.join(command)).read().strip()
  return (ldapBindUser, ldapBindPw)

def init():
  logging.log('Loading Credentials')
  (bindUser, bindPw) = getCredentials()
  if bindUser == '' or bindPw == '':
    logging.error('Could not get credentials')
    sys.exit(1)
  try:
    logging.log('Connecting to server')
    ldapC = ldap.initialize(ldapURI, ldapTrace, sys.stderr)
    logging.log('Signing in to the server')
    ldapC.simple_bind_s(bindUser, bindPw)
  except ldap.LDAPError, e:
    logging.error("LDAPError " + e)
    sys.exit(1)
  return ldapC


def getUser(username):
  try:
    logging.log('Retrieving user ' + username)
    result = ldapConnection().search_s("ou=People,dc=CSUA,dc=Berkeley,dc=EDU", ldap.SCOPE_SUBTREE, '(uid=' + username + ')')
    retval = None
    if len(result) > 0:
      retval = result[0][1]
    else:
      logging.warning('User ' + username + ' not found')
    return retval
  except ldap.LDAPError, e:
    logging.error("LDAPError " + e)
    sys.exit(1)
  #except Exception, e:
    #logging.warning(e)
  return None
  
def checkUser(username):
  return getUser(username) != None

def checkLogin(data):
  user = getUser(data.username)
  logging.log('Checking if password is correct')
  return user != None and user['userPassword'][0] == data.password

def checkNewUser(username):
  return not checkUser(username)

_ldapConnection = None
def ldapConnection():
  global _ldapConnection
  if _ldapConnection == None:
    _ldapConnection = init()
  return _ldapConnection
