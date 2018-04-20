import urllib2 #urllib2 only valide in py2
# the following 2 lines for version py3 
'''
from urllib.request import urlopen
import urllib.error
'''
import json

#TOKEN = "cc922578a7a1c6065a2aa91bc62b02e41a99afdb"
TOKEN = "2d31ffb23c3306c346c75264f9a42fd5ec0b8010"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"


class BitlyHelper:

    def shorten_url(self, longurl):
        try:
            url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
            # response = urlopen(url).read()  -- "urlopen(url).read()" 's is only applied under py3 
            response = urllib2.urlopen(url).read()
            jr = json.loads(response)
            return jr['data']['url']
        except Exception as e:
            print(e)
