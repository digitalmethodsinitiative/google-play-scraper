"""
Google Play Store Scraper
"""
import datetime
import requests
import json
import re

from urllib.parse import quote_plus
from google_play_scraper.util import PlayStoreException, PlayStoreCollections


class PlayStoreScraper:
	"""
	Google Play Store scraper

	This class implements methods to retrieve information about Google Play
	Store apps in various ways. The methods are fairly straightforward. Much
	has been adapted from the javascript-based google-play-scraper package, which
	can be found at https://github.com/facundoolano/google-play-scraper.
	"""
	PLAYSTORE_URL = "https://play.google.com"

	def get_app_ids_for_query(self, term, num=50, page=1, country="nl", lang="nl"):
		"""
		Retrieve suggested app IDs for search query

		:param str term:  Search query
		:param int num:  Amount of items to return per page, default 50
		:param int page:  Amount of pages to return
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of App IDs returned for search query
		"""
		url = self.PLAYSTORE_URL + "/store/search?c=apps&q="
		url += quote_plus(term)
		url += "&hl=" + lang
		url += "&gl=" + country

		amount = int(num) * int(page)
		apps = []

		try:
			result = requests.get(url).text
			data = self.extract_json_block(result, "ds:3")
			data = json.loads(data)
		except json.JSONDecodeError:
			raise PlayStoreException("Could not parse search query response")
		except IndexError:
			return []

		apps += [app[12][0] for app in data[0][1][0][0][0]][:amount]

		# part two
		# not all apps are loaded on the page initially, so we need to make
		# subsequent requests via the internal API to request the additional
		# apps. This request payload was borrowed from google-play-scraper.
		body = '[[["qnKhOb","[[null,[[10,[10,50]],true,null,[96,27,4,8,57,30,110,79,11,16,49,1,3,9,12,104,55,56,51,10,34,77]],null,\\"%token%\\"]]",null,"generic"]]]'
		token = data[0][1][0][0][7][1]

		url = self.PLAYSTORE_URL + "/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&bl=boq_playuiserver_20190424.04_p0"
		url += "&hl=" + lang
		url += "&gl=" + country
		url += "&authuser=0&soc-app=121&soc-platform=1&soc-device=1"
		url += quote_plus(term)

		while token:
			next_request_payload = body.replace("%token%", token)
			apps_page = requests.post(url, data={"f.req": next_request_payload}, headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
			apps_page = apps_page.text[4:].strip()
			apps_page = json.loads(apps_page)
			apps_page = json.loads(apps_page[0][2])

			apps += [app[12][0] for app in apps_page[0][0][0]]

			# no token means no next page
			token = apps_page[0][0][7][1] if apps_page[0][0][7] else None

		return apps

	def get_app_ids_for_collection(self, collection="", category="", age="", num=50, lang="nl", country="nl"):
		"""
		Retrieve app IDs in given Play Store collection

		Collections are e.g. 'top free apps'.

		:param str collection:  Collection ID. One of the values in
		                        `PlayStoreCollections`. Seems to only make the
		                        difference between 'new' or 'top' results
		:param str category: Category ID. Empty by default. One of the values
		                     in PlayStoreCategories.
		:param str age:  Age bracket. Empty by default. One of the values in
		                 PlayStoreAgeBrackets.
		:param int num:  Amount of results to return. Defaults to 50.
		:param str lang:  Language code to search with, default 'nl'
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.

		:return:  List of App IDs in collection.
		"""
		if not collection:
			collection = PlayStoreCollections.TOP_FREE

		url = self.PLAYSTORE_URL + "/store/apps"

		if "new" in collection:
			url += "/new"
		else:
			url += "/top"

		if category:
			url += "/category/%s" % category

		url += "?hl=" + lang
		url += "&gl=" + country

		if age:
			url += "&age=" + age

		try:
			result = requests.get(url).text
			block = self.extract_json_block(result, "ds:3")
			data = json.loads(block)
		except (json.JSONDecodeError, PlayStoreException):
			raise PlayStoreException("Could not parse Play Store response")

		return [app[12][0] for app in data[0][1][0][0][0]]

	def get_app_ids_for_developer(self, developer_id, num=60, country="nl", lang="nl"):
		"""
		Retrieve App IDs linked to given developer

		:param str developer_id:  Developer ID
		:param int num:  Number of results to return. Defaults to 60.
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of App IDs linked to developer
		"""
		try:
			developer_id = int(developer_id)
			url = self.PLAYSTORE_URL + "/store/apps/dev?id="
		except ValueError:
			url = self.PLAYSTORE_URL + "/store/apps/dev?id="

		url += quote_plus(str(developer_id))

		url += "&hl=" + lang
		url += "&gl=" + country

		try:
			result = requests.get(url).text
			data = self.extract_json_block(result, "ds:3")
			data = json.loads(data)
		except (json.JSONDecodeError, PlayStoreException):
			raise PlayStoreException("Could not parse Play Store response")

		return [app[12][0] for app in data[0][1][0][0][0]][:num]

	def get_similar_app_ids_for_app(self, app_id, country="nl", lang="nl"):
		"""
		Retrieve list of App IDs of apps similar to given app

		This one is a bit special because we first request the app details page
		to get the link to the 'similar apps' page, and then request that page.
		So this costs 2 requests per call.

		:param str app_id:  App ID to find similar apps for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of similar app IDs
		"""
		url = self.PLAYSTORE_URL + "/store/apps/details?id="
		url += quote_plus(app_id)

		url += "&hl=" + lang
		url += "&gl=" + country

		try:
			result = requests.get(url).text
			data = self.extract_json_block(result, "ds:7")
			data = json.loads(data)
			similar_url = self.PLAYSTORE_URL + data[1][1][0][0][3][4][2]
		except (json.JSONDecodeError, PlayStoreException):
			raise PlayStoreException("Could not parse Play Store response")

		try:
			result = requests.get(similar_url).text
			data = self.extract_json_block(result, "ds:3")
			result = json.loads(data)
		except json.JSONDecodeError:
			pass

		return [app[12][0] for app in result[0][1][0][0][0]]

	def get_permissions_for_app(self, app_id, lang="en", short=True):
		"""
		Get a list of permissions for a given app

		:param string app_id:  App ID to get permissions for
		:param string lang:  Language, defaults to 'en'. Parts of the
		                     permission description seems to be in english no
		                     matter the value of this parameter.
		:param bool short:  Include 'category' of permissions?
		:return list:  List of permissions, as strings
		"""
		url = self.PLAYSTORE_URL + "/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&f.sid=-697906427155521722&bl=boq_playuiserver_20190903.08_p0&hl=" + lang + "&authuser&soc-app=121&soc-platform=1&soc-device=1&_reqid=1065213"
		body = {"f.req": '[[["xdSrCf","[[null,[\\"' + app_id + '\\",7],[]]]",null,"1"]]]'}

		result = requests.post(url, data=body,
							   headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}).text
		result = result[5:].strip()

		try:
			data = json.loads(result)
		except json.JSONDecodeError:
			raise PlayStoreException("Could not parse Play Store response")

		try:
			data = json.loads(data[0][2])
		except json.JSONDecodeError:
			return []

		groups = []
		for list in data:
			if not list:
				continue
			for item in list:
				groups.append(item)

		result = []
		for group in groups:
			if not group:
				continue
			elif not group[0]:
				result.append(group[1])
			else:
				for permission in group[2]:
					if short:
						result.append(permission[1])
					else:
						result.append(group[0] + " -> " + permission[1])

		return result

	def get_app_details(self, app_id, country="nl", lang="nl"):
		"""
		Get app details for given app ID

		:param str app_id:  App ID to retrieve details for
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return dict:  App details, as returned by the Play Store.
		"""
		url = self.PLAYSTORE_URL + "/store/apps/details?id="
		url += quote_plus(app_id)

		url += "&hl=" + lang
		url += "&gl=" + country

		try:
			result = requests.get(url).text

			pricing = json.loads(self.extract_json_block(result, "ds:3"))
			info = json.loads(self.extract_json_block(result, "ds:5"))
			version = json.loads(self.extract_json_block(result, "ds:8"))
			pegi = json.loads(self.extract_json_block(result, "ds:11"))
			rating = json.loads(self.extract_json_block(result, "ds:14"))

		except (json.JSONDecodeError, PlayStoreException):
			raise PlayStoreException("Could not parse Play Store response")

		app = {
			"img_src": info[0][12][1][3][2],
			"title": info[0][0][0],
			"link": url,
			"id": app_id,
			"developer_link": self.PLAYSTORE_URL + info[0][12][5][5][4][2],
			"developer_name": info[0][12][5][1],
			"description": info[0][10][0][1],
			"price_inapp": info[0][12][12][0] if info[0][12][12] else "",
			"category": info[0][12][25],
			"num_downloads": info[0][12][9][2],
			"num_downloads_approx": info[0][12][9][1],
			"published": datetime.datetime.fromtimestamp(int(info[0][12][8][0])).strftime("%c"),
			"published_timestamp": info[0][12][8][0],
			"pegi": pegi[0][1][2][9][0],
			"filesize": version[0],
			"os": version[2],
			"software": version[1],
			"price": "%i %s" % (pricing[0][2][0][0][0][1][0][0], pricing[0][2][0][0][0][1][0][1]) if pricing[0][
				2] else 0
		}

		try:
			app["rating"] = rating[0][0][0][7][0][1]
		except TypeError:
			app["rating"] = 0

		return app

	def get_multiple_app_details(self, app_ids, country="nl", lang="nl"):
		"""
		Get app details for a list of app IDs

		:param list app_id:  App IDs to retrieve details for
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return generator:  A list (via a generator) of app details
		"""
		for app_id in app_ids:
			yield self.get_app_details(app_id)

	def extract_json_block(self, html, block_id):
		"""
		Extract a block of JSON data from a Play Store page source code

		Blocks of JSON with scrapeable data are embedded in the source code of
		Google Play Store pages in a predictable way, so we can extract them
		in a predictable way too. They are defined using a JavaScript function
		called 'AF_initDataCallBack' (though sometimes capitalised differently)
		which takes a function returning the JSON as one of its arguments. This
		method extracts that function argument from the JavaScript source code.

		:param str html:  HTML to extract JSON block from
		:param str block_id: ID of the block, e.g. 'ds:3'
		:return str:  JSON (unparsed) for that block ID
		"""
		prefix = re.compile(r"AF_init[dD]ata[cC]all[bB]ack\s*\({[^{}]*key:\s*'" + re.escape(block_id) + ".*?data:")
		suffix = re.compile(r"}\s*\)\s*;")

		try:
			block = prefix.split(html)[1]
			block = suffix.split(block)[0]
		except IndexError:
			raise PlayStoreException("Could not extract block %s" % block_id)

		block = block.strip()
		block = re.sub(r"^function\s*\([^)]*\)\s*{", "", block)
		block = re.sub("}$", "", block)

		return block