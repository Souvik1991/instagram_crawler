from __future__ import unicode_literals

from django.db import models

# Create your models here.
# Save the profile data which have been visited
class VisitedProfile(models.Model):
	user_name = models.CharField(max_length=100)
	instagram_profile_id = models.IntegerField(null=False, unique=True)
	url = models.CharField(max_length=200)

	class Meta:
		db_table = 'visited_profile'

# Save the data which profile have to visit
# Once visited it will deleted from here
class HavetoVisit(models.Model):
	user_name = models.CharField(max_length=100)
	instagram_profile_id = models.IntegerField(null=False, unique=True)
	url = models.CharField(max_length=200)

	class Meta:
		db_table = 'have_to_visit'

# The saved user data
class InstagramProfileData(models.Model):
	"""Stores instagram user information"""
	name = models.CharField(max_length=150)
	url = models.CharField(max_length=200)
	country_code = models.CharField(max_length=10)
	language = models.CharField(max_length=10)
	is_indian = models.BooleanField(default=False)

	user_name = models.CharField(max_length=100)
	follower_count = models.IntegerField(null=False, default=0)
	follows_count = models.IntegerField(null=False, default=0)
	post_count = models.IntegerField(null=False, default=0)
	profile_pic_url = models.CharField(max_length=250)
	instagram_profile_id = models.IntegerField(null=False, unique=True)
	biography = models.TextField(max_length=1500)
	external_url = models.CharField(max_length=250)

	email = models.TextField(max_length=500, default="[]")
	website = models.TextField(max_length=500, default="[]")
	phone = models.TextField(max_length=500, default="[]")

	class Meta:
		db_table = 'instagram_profile_data'

# Total hastag found in total post parsed
class HashTagFound(models.Model):
	hash_tag = models.CharField(max_length=250)
	profile_id = models.ForeignKey(InstagramProfileData)
	count = models.IntegerField(null=False, default=1)

	class Meta:
		db_table = 'hash_tags'


class foundProfileUsingHashTag(models.Model):
	hashtag = models.CharField(max_length=200)
	username = models.CharField(max_length=200)
	profile_id = models.CharField(max_length=200)
	done = models.BooleanField(default=False)

	class Meta:
		db_table = 'profile_found'


class finalProfile(models.Model):
	name = models.CharField(max_length=150)
	url = models.CharField(max_length=200)

	user_name = models.CharField(max_length=100)
	follower_count = models.IntegerField(null=False, default=0)
	follows_count = models.IntegerField(null=False, default=0)
	post_count = models.IntegerField(null=False, default=0)
	profile_pic_url = models.CharField(max_length=250)
	instagram_profile_id = models.IntegerField(null=False, unique=True)
	biography = models.TextField(max_length=1500)
	external_url = models.CharField(max_length=250)

	email = models.TextField(max_length=500, default="[]")
	website = models.TextField(max_length=500, default="[]")
	phone = models.TextField(max_length=500, default="[]")

	class Meta:
		db_table = 'final_profile'
