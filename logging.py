import inspect

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

def log(message):
  parent = inspect.stack()[1]
  mod = inspect.getmodule(parent[0]).__name__
  print '[%s%s.%s:%d%s]: %s' % (bcolors.OKGREEN, mod, parent[3], parent[2],
                                bcolors.ENDC, str(message))

def warning(message, fromException = True):
  parent = inspect.stack()[1]
  mod = inspect.getmodule(parent[0]).__name__
  print '[%s%s.%s:%d%s]: %s' % (bcolors.WARNING, mod, parent[3], parent[2],
                                bcolors.ENDC, str(message))

def error(message, fromException = True):
  parent = inspect.stack()[1]
  mod = inspect.getmodule(parent[0]).__name__
  print '[%s%s.%s:%d%s]: %s' % (bcolors.FAIL, mod, parent[3], parent[2], 
                                bcolors.ENDC, str(message))
