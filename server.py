#!/usr/bin/env python
import accountant
import web

urls = (
        '/?', 'index',
        '/accountant', accountant.app,
        '/favicon.ico', 'favicon',
        '/(js|css|images)/(.*)', 'media'
)

app = web.application(urls, locals())

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

class index:
  def GET(this):
    f = open('templates/index.html', 'r')
    return f.read()

if __name__ == "__main__":
  app.run()
