import urllib
import urlparse
import mechanize
import json
import re
import time

from pyquery import PyQuery as pq
from termcolor import colored

from django.conf import settings
from django.core.management.base import BaseCommand

from instagram_crawler.models import *

URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
EMAIL_REGEX = re.compile(ur'[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?', re.MULTILINE)
PHONE_NUMBER_REGEX = r"""((?:(?:\+|0{0,2})91(\s*[\-|\' \']\s*)?|[0]?)?[0-9]\d{9})"""

PROFILE_LINK = 'https://www.instagram.com/{}/'

# Get the html content from the link
def _get_html_content(link):
	html = None
	try:
		print colored('Log : Trying to get html content in try block.', 'green')
		br = mechanize.Browser()
		br.set_handle_robots(False) # Do not read the robot.txt
		br.addheaders = [('User-agent', 'Firefox')] # Setting the browser type
		html = br.open(link).read()
		return html

	except:
		print colored('Log : Trying to get html content in except block.', 'yellow')
		try:
			html = urllib.urlopen(link).read()
			return html
		except: return html


def _get_next_link():
	profile = foundProfileUsingHashTag.objects.filter(done=False).order_by('id')[0:1]
	if len(profile) > 0: return profile[0]
	else: return None

# find json from html
def _find_json_from_html(jQuery):
	print colored('Log : Finding json from html.', 'green')
	all_scripts = jQuery('body').find('script[type="text/javascript"]')
	for script in all_scripts:
		script = pq(script)
		script_text = script.text().strip()
		if script_text and '._sharedData' in script_text:
			script_text = script_text.replace('window._sharedData = ', '').replace('};','}')
			return json.loads(script_text)

	return None

def _save_data(user, link, visit_link):
	try:
		finalProfile.objects.get(instagram_profile_id = user.get('id'))
	except finalProfile.DoesNotExist:
		phone_number = re.findall(PHONE_NUMBER_REGEX, user.get('biography')) 
		email = re.findall(EMAIL_REGEX, user.get('biography')) 
		website = re.findall(URL_REGEX, user.get('biography')) 

		finalProfile.objects.create(
			name = user.get('full_name'),
			url = link,
			user_name = visit_link.username,
			follower_count = user.get('followed_by').get('count'),
			follows_count = user.get('follows').get('count'),
			post_count = user.get('media').get('count'),
			profile_pic_url = user.get('profile_pic_url_hd'),
			instagram_profile_id = user.get('id'),
			biography = user.get('biography'),
			external_url = user.get('external_url'),
			email = json.dumps(email),
			website = json.dumps(website),
			phone = json.dumps(phone_number)
		)


# Main class, from where the execution starts
class Command(BaseCommand):
	help = 'Crawl the instagram save data if user have more than 6K follower'
	def handle(self, *args, **options):
		try:
			while True:
				try:
					visit_link = _get_next_link()
					if visit_link:
						link = PROFILE_LINK.format(visit_link.username)
						print colored('Log : Found new link to visit:{}'.format(link), 'blue')
						html = _get_html_content(link)
						if html:
							jQuery = pq(html)
							data = _find_json_from_html(jQuery)

							if data.get('entry_data') and data.get('entry_data').get('ProfilePage') and data.get('entry_data').get('ProfilePage')[0].get('user').get('followed_by').get('count') > 25000:
								_save_data(data.get('entry_data').get('ProfilePage')[0].get('user'), link, visit_link)

						visit_link.done = True
						visit_link.save()			

					else:
						print colored('Log : Going to sleep', 'blue')
						time.sleep(5)
						print colored('Log : Waking up', 'blue')

				except Exception as e: print colored(e, 'red')
		except KeyboardInterrupt as e: print colored("Log : Keyboard interrupt detected.", 'red')

