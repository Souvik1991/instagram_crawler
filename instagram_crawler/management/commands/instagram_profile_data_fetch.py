import urllib
import urlparse
import mechanize
import json

import time
import re

from pyquery import PyQuery as pq
from termcolor import colored

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from instagram_crawler.models import VisitedProfile, HavetoVisit, InstagramProfileData, HashTagFound

URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
EMAIL_REGEX = re.compile(ur'[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?', re.MULTILINE)
PHONE_NUMBER_REGEX = r"""((?:(?:\+|0{0,2})91(\s*[\-|\' \']\s*)?|[0]?)?[0-9]\d{9})"""
HASH_TAG_REGEX = re.compile(r"#(\w+)")

BASE_LINK = 'https://www.instagram.com/'
POST_LINK = 'https://www.instagram.com/p/{}/'
BASE_SCREEN_NAME = 'thebigbhookad'
BASE_PROFILE_ID = 34175411
MIN_FOLLOWER = 6000

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

# Save the data in visited table
def _save_in_visited_table(data_object):
	try:
		visited_profile = VisitedProfile(
			user_name = data_object.get('user_name'), 
			instagram_profile_id = data_object.get('profile_id'), 
			url = data_object.get('url')
		)
		visited_profile.save()
		print colored('Log : {} user successfully saved in visited table.'.format(data_object.get('user_name')), 'green')

	except: pass

# Delete the profile data from have to visit table
def _delete_from_have_to_visit(data_object):
	try: 
		have_to_visit_data = HavetoVisit.objects.get(Q(instagram_profile_id=data_object.get('profile_id')) & Q(user_name=data_object.get('user_name')))
		have_to_visit_data.delete()
		print colored('Log : {} user data deleted from have to visit table.'.format(data_object.get('user_name')), 'red')

	except HavetoVisit.DoesNotExist: pass

# Find out what link to visit
def _find_visit_url():
	selected_links = HavetoVisit.objects.all()[0:1]
	if len(selected_links) > 0:
		# selected_links = all_present_links[0:1]
		return {
			'previous_data': True,
			'url': selected_links[0].url,
			'profile_id': selected_links[0].instagram_profile_id,
			'user_name': selected_links[0].user_name
		} 

	else:
		url = '{}{}/'.format(BASE_LINK, BASE_SCREEN_NAME)
		try:
			VisitedProfile.objects.get(Q(user_name=BASE_SCREEN_NAME) | Q(instagram_profile_id=BASE_PROFILE_ID))
		except VisitedProfile.DoesNotExist:
			return {
				'previous_data': False,
				'url': url,
				'profile_id': BASE_PROFILE_ID,
				'user_name': BASE_SCREEN_NAME
			}

	return None

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

# Save the user data
def _save_user_data(data, url):
	try:
		user = data.get('entry_data').get('ProfilePage')[0].get('user')
		if user.get('is_private'): return False
		if user.get('followed_by').get('count', 0) > MIN_FOLLOWER:
			phone_number = re.findall(PHONE_NUMBER_REGEX, user.get('biography')) 
			email = re.findall(EMAIL_REGEX, user.get('biography')) 
			website = re.findall(URL_REGEX, user.get('biography')) 

			instagram_user = InstagramProfileData(
				name = user.get('full_name'),
				url = url,
				country_code = data.get('country_code'),
				language = data.get('language_code'),

				user_name = user.get('username'),
				follower_count = user.get('followed_by').get('count', 0),
				follows_count = user.get('follows').get('count', 0),
				post_count = user.get('media').get('count', 0),
				profile_pic_url = user.get('profile_pic_url'),
				instagram_profile_id = int(user.get('id')),
				biography = user.get('biography'),
				external_url = user.get('external_url'),

				email = json.dumps(email),
				website = json.dumps(website),
				phone = json.dumps(phone_number)
			)
			instagram_user.save()

			print colored('Log : New instagram user : {}, successfully saved.'.format(user.get('username')), 'green')
			return instagram_user

	except Exception as e: print colored(e, 'red')

def _save_hashtags_from_post(user, data):
	try:
		posts = data.get('entry_data').get('ProfilePage')[0].get('user').get('media').get('nodes')
		for post in posts:
			hash_tags = re.findall(HASH_TAG_REGEX, post.get('caption'))
			for tag in hash_tags:
				try:
					hash_tag = HashTagFound.objects.get(hash_tag=tag, profile_id=user)
					hash_tag.count = hash_tag.count + 1
					hash_tag.save()

				except HashTagFound.DoesNotExist:
					hash_tag_object = HashTagFound(
						hash_tag = tag,
						profile_id = user
					)
					hash_tag_object.save()

					if 'india' in tag.lower() and not user.is_indian:
						user.is_indian = True
						user.save()

		print colored('Log : All hashtags successfully saved.', 'blue')
	except: pass

# Get other user profile data from comments
def _get_user_from_comments(data):
	try:
		user = data.get('entry_data').get('ProfilePage')[0].get('user')
		if user.get('is_private'): return False

		nodes = user.get('media').get('nodes')
		if nodes:
			for node in nodes:
				link = POST_LINK.format(node.get('code'))
				print colored('Log : Visiting POST link : {}'.format(link), 'blue')
				html = _get_html_content(link)
				if html:
					jQuery = pq(html)
					data = _find_json_from_html(jQuery)
					if data:
						try:
							comment_nodes = data.get('entry_data').get('PostPage')[0].get('media').get('comments').get('nodes')
							for c_node in comment_nodes:
								try:
									VisitedProfile.objects.get(Q(user_name=c_node.get('user').get('username')) & Q(instagram_profile_id=int(c_node.get('user').get('id'))))
								except VisitedProfile.DoesNotExist:
									# print 'Log : Got new have to Visit user : {}'.format(c_node.get('user').get('username'))
									have_to_visit = HavetoVisit(
										user_name = c_node.get('user').get('username'),
										instagram_profile_id = int(c_node.get('user').get('id')),
										url = '{}{}'.format(BASE_LINK, c_node.get('user').get('username'))
									)
									have_to_visit.save()

							# Saving liked user in the post
							like_nodes = data.get('entry_data').get('PostPage')[0].get('media').get('likes').get('nodes')
							for l_node in like_nodes:
								try:
									VisitedProfile.objects.get(Q(user_name=l_node.get('user').get('username')) & Q(instagram_profile_id=int(l_node.get('user').get('id'))))
								except VisitedProfile.DoesNotExist:
									# print 'Log : Got new have to Visit user : {}'.format(l_node.get('user').get('username'))
									have_to_visit = HavetoVisit(
										user_name = l_node.get('user').get('username'),
										instagram_profile_id = int(l_node.get('user').get('id')),
										url = '{}{}'.format(BASE_LINK, l_node.get('user').get('username'))
									)
									have_to_visit.save()

						except: pass
	except: pass

# Main class, from where the execution starts
class Command(BaseCommand):
	help = 'Crawl the instagram save data if user have more than 6K follower'
	def handle(self, *args, **options):
		try:
			while True:
				try:
					data = None
					received_url_data = _find_visit_url()
					if received_url_data:
						print colored('Log : Found url to visit : {}'.format(received_url_data.get('url')), 'green')
						# Getting the html content from the link
						html = _get_html_content(received_url_data.get('url'))
						if html:
							print colored('Log : HTML successfully fetched.', 'green')
							# Parsing html
							jQuery = pq(html)
							data = _find_json_from_html(jQuery)
							if data:
								print colored('Log : JSON data successfully fetched.', 'green')
								instagram_user = _save_user_data(data, received_url_data.get('url'))
								if instagram_user:
									_save_hashtags_from_post(instagram_user, data)

						# Save the link is u
						_save_in_visited_table(received_url_data)

						if received_url_data.get('previous_data'):
							_delete_from_have_to_visit(received_url_data)

						# Fetch more user data to visit next
						if data:
							_get_user_from_comments(data)

					else:
						print 'Log : Crawl Successfully completed !'
						break

					print colored('============================================', 'red')

				except Exception as e: print colored(e, 'red')

		except KeyboardInterrupt as e: print colored("Log : Keyboard interrupt detected.", 'red')
