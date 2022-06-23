"""
Google Play Store Scraper
"""
import datetime
import requests
import json
import time
from bs4 import BeautifulSoup

from urllib.parse import quote_plus
from google_play_scraper.util import PlayStoreException, PlayStoreCollections, WebsiteMappings


class PlayStoreScraper:
	"""
	Google Play Store scraper

	This class implements methods to retrieve information about Google Play
	Store apps in various ways. The methods are fairly straightforward. Much
	has been adapted from the javascript-based google-play-scraper package, which
	can be found at https://github.com/facundoolano/google-play-scraper.
	"""
	PLAYSTORE_URL = "https://play.google.com"

	@staticmethod
	def extract_all_app_ids_from_page(page_source):
		"""
		Uses the WebsiteMappings.app_detail_link_subdomain to find any link on
		a provided page source and returns the app id from that link.

		:param str page_source: Raw page source from request.get()
		:return List: List of app ids
		"""
		soup = BeautifulSoup(page_source, 'html.parser')
		return [link.get('href').split(WebsiteMappings.app_detail_link_subdomain)[1] for link in soup.find_all('a') if WebsiteMappings.app_detail_link_subdomain in link.get('href')]

	def get_app_ids_for_query(self, term, num=50, page=1, country="nl", lang="nl"):
		"""
		Retrieve suggested app IDs for search query

		:param str term:  Search query
		:param int num:  Amount of items to return per page, default 50
		:param int page:  Amount of pages to return
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of Play IDs returned for search query
		"""

		if term is None or term == "":
			raise PlayStoreException('No term was given')

		url = self.PLAYSTORE_URL + "/store/search?c=apps&q="
		url += quote_plus(term)
		url += "&hl=" + lang
		url += "&gl=" + country

		amount = int(num) * int(page)
		apps = []

		try:
			result = requests.get(url).text
		except ConnectionError as ce:
			raise PlayStoreException("Could not not connect to store: {}".format(str(ce)))

		# Some queries return a promenent result
		try:
			first_result = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['first_result'])
		except (TypeError, IndexError):
			try:
				first_result = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['first_result_2'])
			except (TypeError, IndexError):
				# Could not identify first result
				first_result = None

		if first_result:
			apps.append(first_result.split(WebsiteMappings.app_detail_link_subdomain)[1])
			# Collect blocks of apps from promenent result page
			try:
				try:
					app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['list_of_apps'])
				except (TypeError, IndexError):
					# Second generic mapping found... depends on country
					app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['list_of_apps_2'])
			except Exception as e:
				raise PlayStoreException('Generic query failed for country %s url %s: %s' % (country, url, str(e)))
		else:
			# Collect blocks of apps from generic results page
			try:
				try:
					app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['list_of_apps_generic'])
				except (TypeError, IndexError):
					# Second generic mapping found... depends on country
					app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['list_of_apps_generic_2'])
			except Exception as e:
				raise PlayStoreException('Generic query failed for country %s url %s: %s' % (country, url, str(e)))
			# Check if results are comprehensive
			potential_results = len(self.extract_all_app_ids_from_page(result))
			if not potential_results == len(app_list):
				self._log_error(country, 'App Query Warning: Results (%i) do not equal potential results (%i)' % (len(app_list), potential_results))
				# TODO how to warn user?

		for app in app_list:
			# Collect app id from each block
			apps.append(WebsiteMappings.get_nested_item(app, WebsiteMappings.query_mapping['app_id_in_list']))

		return apps[:amount]

		# 2022-06-01 Google redesign and unsure how to reimpliment token
		# They are using an infiniate scroll as opposed to pagination
		# Prior implementation below:
		# part two
		# not all apps are loaded on the page initially, so we need to make
		# subsequent requests via the internal API to request the additional
		# apps. This request payload was borrowed from google-play-scraper.
		body = '[[["qnKhOb","[[null,[[10,[10,50]],true,null,[96,27,4,8,57,30,110,79,11,16,49,1,3,9,12,104,55,56,51,10,34,77]],null,\\"%token%\\"]]",null,"generic"]]]'
		try:
			data = WebsiteMappings.extract_json_block(result, "ds:3")
			data = json.loads(data)
			token = data[0][1][0][0][7][1] if data[0][1][0][0][7] else None
		except json.JSONDecodeError:
			token = None
			self._log_error(country,
				PlayStoreException("json.JSONDecodeError: unable to obtain token for additional results"))
		except IndexError:
			token = None
			self._log_error(country,
				PlayStoreException("Index error: unable to obtain token for additional results"))

		url = self.PLAYSTORE_URL + "/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&bl=boq_playuiserver_20190424.04_p0"
		url += "&hl=" + lang
		url += "&gl=" + country
		url += "&authuser=0&soc-app=121&soc-platform=1&soc-device=1"
		url += quote_plus(term)

		while token:
			next_request_payload = body.replace("%token%", token)
			apps_page = requests.post(url, data={"f.req": next_request_payload},
									  headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
			apps_page = apps_page.text[4:].strip()
			apps_page = json.loads(apps_page)
			apps_page = json.loads(apps_page[0][2])

			apps += [app[12][0] for app in apps_page[0][0][0]]

			# no token means no next page
			token = apps_page[0][0][7][1] if apps_page[0][0][7] else None

		return apps[:amount]

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

		:return:  List of Play IDs in collection.
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
			block = WebsiteMappings.extract_json_block(result, "ds:3")
			data = json.loads(block)
		except (json.JSONDecodeError, PlayStoreException):
			raise PlayStoreException("Could not parse Play Store response")

		return [app[12][0] for app in data[0][1][0][0][0]]

	def get_app_ids_for_developer(self, developer_id, num=60, country="nl", lang="nl"):
		"""
		Retrieve Play IDs linked to given developer

		:param str developer_id:  Developer ID
		:param int num:  Number of results to return. Defaults to 60.
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of Play IDs linked to developer
		"""
		try:
			developer_id = int(developer_id)
			url = self.PLAYSTORE_URL + "/store/apps/dev?id="
			normal_dev_layout = False
		except ValueError:
			url = self.PLAYSTORE_URL + "/store/apps/developer?id="
			normal_dev_layout = True

		url += quote_plus(str(developer_id))

		url += "&hl=" + lang
		url += "&gl=" + country

		try:
			result = requests.get(url).text
		except ConnectionError as ce:
			raise PlayStoreException("Could not not connect to store: {}".format(str(ce)))

		# Collect all potential app IDs on page
		potential_apps = self.extract_all_app_ids_from_page(result)

		try:
			# Collects specific results from JSON object
			if normal_dev_layout:
				app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping['list_of_apps_developer'])
			else:
				app_list = WebsiteMappings.find_item_from_json_mapping(result, WebsiteMappings.query_mapping[
					'list_of_apps_developer_id'])
		except Exception as e:
			raise PlayStoreException('Generic query failed for country %s url %s: %s' % (country, url, str(e)))

		# These normal dev pages only seem to have the specific apps we are looking for (as opposed to other results with "similar apps" or "app you might be interesed in"
		if not len(potential_apps) == len(app_list):
			self._log_error(country, 'App Query Warning: Results (%i) do not equal potential results (%i)' % (len(app_list), potential_results))
			# TODO how to warn user?

		# Collect app IDs from app_list
		if normal_dev_layout:
			apps = [WebsiteMappings.get_nested_item(app, WebsiteMappings.query_mapping['app_id_in_list']) for app in app_list]
		else:
			apps = [WebsiteMappings.get_nested_item(app, WebsiteMappings.query_mapping['app_id_in_list_dev_id']) for app in app_list]

		return apps[:num]


	def get_similar_app_ids_for_app(self, app_id, country="nl", lang="nl"):
		"""
		Retrieve list of Play IDs of apps similar to given app

		This one is a bit special because we first request the app details page
		to get the link to the 'similar apps' page, and then request that page.
		So this costs 2 requests per call.

		:param str app_id:  Play ID to find similar apps for
		:param str country:  Two-letter country code for the store to search in.
		                     Defaults to 'nl'.
		:param str lang:  Language code to search with, default 'nl'

		:return list:  List of similar app IDs
		"""
		url = self.PLAYSTORE_URL + WebsiteMappings.app_detail_link_subdomain
		url += quote_plus(app_id)

		url += "&hl=" + lang
		url += "&gl=" + country

		result = requests.get(url).text
		soup = BeautifulSoup(result, 'html.parser')

		# Check for collection links; there is currently only one to the similar apps
		possible_collections = [link.get('href') for link in soup.find_all('a') if WebsiteMappings.collection_subdomain in link.get('href')]
		if len(possible_collections) > 1:
			raise PlayStoreException("Similar apps link criteria changed; unable to find link to similar apps!")
		elif len(possible_collections) == 0:
			raise PlayStoreException("No similar apps link found; check if similar apps link exists at link and inform developers if necessary: %s" % url)

		similar_url = self.PLAYSTORE_URL + possible_collections[0]

		try:
			result = requests.get(similar_url).text
		except ConnectionError as ce:
			raise PlayStoreException("Could not not connect to store: {}".format(str(ce)))

		return self.extract_all_app_ids_from_page(result)

	def get_permissions_for_app(self, app_id, lang="en", short=True):
		"""
		Get a list of permissions for a given app
		TODO: What is this URL?

		:param string app_id:  Play ID to get permissions for
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

		:param str app_id:  Play ID to retrieve details for
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return dict:  Play details, as returned by the Play Store.
		"""
		url = self.PLAYSTORE_URL + "/store/apps/details?id="
		url += quote_plus(app_id)

		url += "&hl=" + lang
		url += "&gl=" + country

		request_result = self._app_connection(url, retry=1)

		app = {
			'id': app_id,
			'link': url,
		}
		for k, v in WebsiteMappings.app_details_mapping.items():
			try:
				app[k] = WebsiteMappings.find_item_from_json_mapping(request_result, v)
			except PlayStoreException:
				raise PlayStoreException("Could not parse Play Store response for {0}".format(app_id))
			except Exception as e:
				self._log_error(country, 'App Detail error on detail %s: %s' % (k, str(e)))
				if 'errors' in app.keys():
					app['errors'].append(k)
				else:
					app['errors'] = [k]
		if 'errors' in app.keys():
			plural = 's' if len(app['errors']) > 1 else ''
			app['errors'] = 'Detail%s not found for key%s: %s' % (plural, plural, ', '.join(app['errors']))

		return app

	def get_multiple_app_details(self, app_ids, country="nl", lang="nl"):
		"""
		Get app details for a list of app IDs

		:param list app_ids:  Play IDs to retrieve details for
		:param str country:  Two-letter country code of store to search in,
		                     default 'nl'
		:param str lang:  Language code to search with, default 'nl'

		:return generator:  A list (via a generator) of app details
		"""
		for app_id in app_ids:
			try:
				time.sleep(1)
				yield self.get_app_details(app_id, country=country, lang=lang)
			except PlayStoreException as pse:
				self._log_error(country, pse.message)
				continue
			except Exception as e:
				self._log_error(country, e)
				continue

	def _app_connection(self, url, sleeptime=2, retry=0):
		"""
			Extracted method for app connection

			:param string url : The URL to query
		"""
		try:
			return requests.get(url).text
		except ConnectionError:
			if retry > 0:
				if sleeptime > 0:
					time.sleep(sleeptime)
				retry = retry - 1
				self._app_connection(url, sleeptime=sleeptime, retry=retry)
			else:
				raise PlayStoreException("Could not connect to : {0}".format(url))

	def _log_error(self, app_store_country, message):
		"""
		Write the error to a local file to capture the error.

			:param str app_store_country: the country for the app store
			:param str message: the error message to log

		"""
		app_log = "{0}_log.txt".format(app_store_country)
		errortime = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
		fh = open(app_log, "a")
		fh.write("%s %s \n" % (errortime, message))
		fh.close()
