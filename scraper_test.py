from google_play_scraper.scraper import PlayStoreScraper
from google_play_scraper.util import PlayStoreException, PlayStoreCollections, PlayStoreCategories, PlayStoreUtils

import json
import pytest
import os

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
    results = scraper.get_app_ids_for_query("racism", country="gb", lang="en")
    print(len(results))
    assert len(results) == 50

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