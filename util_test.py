from google_play_scraper.util import PlayStoreException, PlayStoreCollections, PlayStoreCategories, PlayStoreUtils, PlayStoreAgeBrackets

import json
import pytest
import os

def test_category_exists():
    category = PlayStoreCategories()
    assert category.BEAUTY == "BEAUTY"

def test_category_does_not_exist():
    category = PlayStoreCategories()
    with pytest.raises(AttributeError, match="'PlayStoreCategories' object has no attribute 'METHOD'"):
        category.METHOD

def test_collection_exists():
    collection = PlayStoreCollections()
    assert collection.TOP_FREE == 'topselling_free'

def test_collection_does_not_exist():
    collection = PlayStoreCollections()
    with pytest.raises(AttributeError, match="'PlayStoreCollections' object has no attribute 'NOTHING'"):
        collection.NOTHING

def test_app_utils():
    utils = PlayStoreUtils()
    json_object = json.loads(utils.get_entries(PlayStoreCollections()))
    assert "names" in json_object

def test_bracket_exists():
    brackets = PlayStoreAgeBrackets()
    assert brackets.FIVE_UNDER == "AGE_RANGE1"

def test_bracket_does_not_exist():
    brackets = PlayStoreAgeBrackets()
    with pytest.raises(AttributeError, match="'PlayStoreAgeBrackets' object has no attribute 'METHOD'"):
        brackets.METHOD
