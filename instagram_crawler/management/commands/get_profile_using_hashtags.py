import json
import urllib, urllib2

from termcolor import colored
from instagram_crawler.models import *

from django.conf import settings
from django.core.management.base import BaseCommand

HASHTAGS = [
	'indianphotographer',
	'indianphotographers',
	'indianphotography',
	'indianphotographersclub', 
	'indianphotographyclub',
	'travelinindia',
	'lonelyplanetindia',
	'mymumbai'
]
TOKEN = '1542414732.f5fc7d4.439556a359924ef9b57d792db19ecdea'
API_LINK = 'https://api.instagram.com/v1/tags/{}/media/recent?access_token={}'

def _make_network_call(actionLink = "", method = "get", headerObject = {}, dataObject = {}):
	try:
		if actionLink:
			headerObject['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'
			headerObject['Accept'] = 'application/json, text/plain, */*'
			headerObject['Content-type'] = 'application/x-www-form-urlencoded;charset=utf-8' if(not headerObject.get('Content-type')) else headerObject['Content-type']

			if method == "post":
				data = urllib.urlencode(dataObject).encode("utf-8")
				req = urllib2.Request(actionLink, data, headerObject)
				response = urllib2.urlopen(req)

			else:
				req = urllib2.Request(actionLink, None, headerObject)
				response = urllib2.urlopen(req)

			return response.read()

	except Exception as e:
		print 'Error : During makeNetWorkCall method call !!', e
	return None

# Main class, from where the execution starts
class Command(BaseCommand):
	help = 'Crawl the instagram save data if user have more than 6K follower'
	def handle(self, *args, **options):
		try:
			for tag in HASHTAGS:
				print colored("Log : Current tag is: {}.".format(tag), 'green')
				next_link = None
				while True:
					try:
						if next_link: return_data = _make_network_call(next_link, 'get')
						else: return_data = _make_network_call(API_LINK.format(tag, TOKEN), 'get')

						return_data = json.loads(return_data)
						if return_data.get('data'):
							for data in return_data.get('data'):
								try:
									foundProfileUsingHashTag.objects.get(profile_id=data.get('user').get('id'), username=data.get('user').get('username'))
								except foundProfileUsingHashTag.DoesNotExist:
									print 'Log : Saving User : {}'.format(data.get('user').get('username'))
									foundProfileUsingHashTag.objects.create(
										hashtag = tag,
										username = data.get('user').get('username'),
										profile_id = data.get('user').get('id')
									)

						if return_data.get('pagination') and return_data.get('pagination').get('next_url'): next_link = return_data.get('pagination').get('next_url')
						else: break
						# break

					except Exception as e: print colored(e, 'red')
		except KeyboardInterrupt as e: print colored("Log : Keyboard interrupt detected.", 'red')
