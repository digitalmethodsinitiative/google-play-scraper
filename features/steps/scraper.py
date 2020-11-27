from behave import *
from google_play_scraper.scraper import PlayStoreScraper

@given('we have play store scraper installed')
def step_impl(context):
    context.scraper = PlayStoreScraper()

@when('we search for "{search_term}"')
def step_impl(context, search_term):
    context.results = context.scraper.get_app_ids_for_query(search_term, country="gb", lang="en")

@then('the scraper will return "{text}" results')
def step_impl(context, text):
    assert len(context.results) == int(text)

@then('the results length is "{json_len}"')
def step_impl(context, json_len):
    assert len(context.results) == int(json_len)

@when('we search for result from "{search_term}"')
def step_impl(context, search_term):
    results = context.scraper.get_app_ids_for_query(search_term, country="gb", lang="en")
    context.results = context.scraper.get_similar_app_ids_for_app(results[0])

@when('we search for the topic "{term}"')
def step_impl(context, term):
    context.results = context.scraper.get_app_ids_for_collection(collection=term, category="", num=50, country="gb")

@when('we search for the developer "{developer}"')
def step_impl(context, developer):
    context.results = context.scraper.get_app_ids_for_developer(developer, country="gb")

@when('we search for the app with id "{app_id}"')
def step_impl(context, app_id):
    context.results = context.scraper.get_app_details(app_id, country="gb")

@when(u'we search for "{num_apps}" apps')
def step_impl(context, num_apps):
    apps = context.scraper.get_app_ids_for_query("mindful", country="gb", lang="en", num=num_apps)
    context.results = list(context.scraper.get_multiple_app_details(apps, country="gb"))

@when(u'we search for another "{num_apps}" apps')
def step_impl(context, num_apps):
    apps = context.app_id + context.scraper.get_app_ids_for_query("mindful", country="gb", lang="en", num=num_apps)
    context.results = list(context.scraper.get_multiple_app_details(apps, country="gb"))

@when(u'we define an incorrect app id "{app_id}"')
def step_impl(context, app_id):
    context.app_id = [int(app_id)]
