from google_play_scraper.scraper import PlayStoreScraper
from google_play_scraper.util import PlayStoreException, PlayStoreCollections, PlayStoreCategories, PlayStoreUtils

import json
import pytest
import os

def test_single_app_rating_cn():
    scraper = PlayStoreScraper()
    app = scraper.get_app_details("com.getsomeheadspace.android", country="cn", lang="en")
    assert app["rating"] > 0

def test_single_app_rating_gb():
    scraper = PlayStoreScraper()
    app = scraper.get_app_details("com.getsomeheadspace.android")
    assert app["rating"] > 0

def test_term_no_exception():
    scraper = PlayStoreScraper()
    results = scraper.get_app_ids_for_query("mindful", country="gb", lang="en")
    assert len(results) > 0

def test_term_less_default():
    scraper = PlayStoreScraper()
    results = scraper.get_app_ids_for_query("mindful", country="gb", lang="en", num=10)
    assert len(results) < 50

def test_term_results_less_than_default():
    scraper = PlayStoreScraper()
    results = scraper.get_app_ids_for_query("tv", country="gb", lang="en")
    assert len(results) == 50

def test_app_details():
    # This is my app and so I have some control over the details
    scraper = PlayStoreScraper()
    results = scraper.get_app_details("io.github.dalewahl.carddecks", country="us", lang="en")
    assert results.get('id') == 'io.github.dalewahl.carddecks'
    assert results.get('title') == 'Pocket Decks: Conversation Starters, Trivia & More'
    assert results.get('developer_name') == 'Dale Wahl'
    assert results.get('category') == '/store/apps/category/ENTERTAINMENT' or results.get('category') == 'ENTERTAINMENT'
    assert results.get('icon_link') == 'https://play-lh.googleusercontent.com/Pmjuw_wBk-Pp2XFvuCHwJbLmcuooTDE_6IobaCe4yYCAatL_88-Ivr0_zco3Wei_ooY'
    assert type(results.get('num_downloads_approx')) == int
    assert 100 < results.get('num_downloads') < 500
    assert 100 < results.get('num_downloads') < 500
    assert results.get('published_date') == 'May 4, 2020'
    assert results.get('published_timestamp') == 1588615247
    assert results.get('pegi') == 'Teen'
    assert results.get('pegi_detail') == 'Language'
    assert results.get('os') == '5.0'
    assert results.get('description') == 'Download decks from the web or create your own! <br><br>This application allows you to choose a deck full of questions, conversation topics, trivia, or other games and flip through the deck. Play with friends and take turns answering questions or quiz each other.<br><br>Includes Conversation Starter games such as Never Have I Ever, Truth or Dare, Would You Rather, as well as decks of conversation topics. Trivia subjects include General Knowledge, Films, Music, Celebrities and more. Includes a deck of cards too, because why not?<br><br>Completely customizable:<br>Don&#39;t see a deck you want? Create it from scratch!<br>Don&#39;t like a card? Edit it to what you want or just delete it altogether!<br><br>Thanks to Open Trivia Database for some awesome questions!<br>https://opentdb.com/'
    assert results.get('num_of_reviews') < 5
    assert results.get('rating') >= 0

def test_no_term_gives_exception():
    scraper = PlayStoreScraper()
    with pytest.raises(PlayStoreException, match = "No term was given"):
        scraper.get_app_ids_for_query("", country="gb", lang="en")

def test_no_invalid_id_gives_exception():
    scraper = PlayStoreScraper()
    with pytest.raises(PlayStoreException, match = "Could not parse Play Store response for 872"):
        scraper.get_app_details('872')

def test_no_invalid_id_in_multiple_is_empty():
    scraper = PlayStoreScraper()
    assert len(list(scraper.get_multiple_app_details(['872']))) == 0

def test_no_invalid_id_in_multiple_writes_log():
    scraper = PlayStoreScraper()
    scraper.get_multiple_app_details(['872'])
    assert os.path.exists("nl_log.txt")
    fh = open('nl_log.txt')
    assert "Could not parse Play Store response for 872" in fh.read()
    fh.close()
    os.remove('nl_log.txt')

def test_log_file_write_message():
    scraper = PlayStoreScraper()
    scraper._log_error("gb","test")
    assert os.path.exists("gb_log.txt")
    fh = open('gb_log.txt')
    assert "test" in fh.read()
    fh.close()
    os.remove('gb_log.txt')
