#!/usr/bin/env python
#
# ogminer v0.1 2012-05-24
# License type: Apache
# http://mustafaturan.net/
# Demo: http://og-miner.appspot.com/
# Open Graph (OG) data can be called a Hash.
# So, OG data is a key-value store, where keys are stored in
# *property* attribute and *values* are stored in content
# attribute of *meta-tags* inside <head></head> section of
# the html body.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from django.utils import simplejson as json
import re

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('See http://github.com/mustafaturan/ogminer')
  
  def post(self):
  	# Get url to fetch
  	url = self.request.get('url')
  	if url == '': return
  	
  	# Optional desired keys for filtering
  	og_keys = self.request.get('og_keys')

  	# User-Agent
  	user_agent = "OGM v0.1 (Open Graph Miner)"

  	# Fetch url
  	result = urlfetch.fetch(url, headers={
  	  'User-Agent': user_agent, 'Accept': 'text/html'})
  	
  	# Parse OG data
  	if result.status_code == 200:
  	  og = og_parse(result.content, og_keys)
  	  # Print as json
  	  self.response.out.write(json.dumps(og))

def og_parse(rc, og_keys):
  # OG Object (list)
	# In here I prefered python list because OG supports to 
	# have arrays which means a OG hash key can be used more
	# than once.
  og = []
  rc = re.sub("([\n\r\t\s ]+)", ' ', rc)
  head_start_pos = rc.find("<head")
  rc = mb_substr(rc, head_start_pos, rc.find("head>", head_start_pos+4))
  og_meta_tags = re.findall('(<meta(([^a-zA-Z0-9]+)(property|content)([^a-zA-Z0-9=]*)=([^"]*)"([^"]+)")(([^a-zA-Z0-9]+)(property|content)([^a-zA-Z0-9=]*)=([^"]*)"([^"]+)")([^>]*)>|<meta(([^a-zA-Z0-9]+)(property|content)([^a-zA-Z0-9=]*)=([^\']*)\'([^\']+)\')(([^a-zA-Z0-9]+)(property|content)([^a-zA-Z0-9=]*)=([^\']*)\'([^\']+)\')([^>]*)>)', rc)
  for og_meta in og_meta_tags:
    c,p = None, None
    for i,val in enumerate(og_meta):
      if val == 'content':
        c = og_meta[i+3]
      elif val == "property":
        p = og_meta[i+3]

    if p and c:
      if og_keys != '':
        if p in og_keys: og.append({''+p: c})
      else:
        og.append({''+p: c})
  return og

def mb_substr(s,start,length=None,encoding="UTF-8"):
  u_s = s.decode(encoding)
  return (u_s[start:(start+length)] if length else u_s[start:]).encode(encoding)
                
def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
