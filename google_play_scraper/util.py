"""
Play Store Scraper utility classes
"""
import re
import json


class WebsiteMappings:
    """
    Mappings for the different website elements to allow easier updates
    """
    app_details_mapping = {
        'title': ['ds:4', 1, 2, 0, 0],
        'developer_name': ['ds:4', 1, 2, 68, 0],
        'developer_link': ['ds:4', 1, 2, 68, 1, 4, 2],
        'price_inapp': ['ds:4', 1, 2, 19, 0],
        'category': ['ds:4', 1, 2, 79, 0, 0, 1, 4, 2],
        'video_link': ['ds:4', 1, 2, 100, 1, 2, 0, 2],
        'icon_link': ['ds:4', 1, 2, 95, 0, 3, 2],
        'num_downloads_approx': ['ds:4', 1, 2, 13, 1],
        'num_downloads': ['ds:4', 1, 2, 13, 2],
        'published_date': ['ds:4', 1, 2, 10, 0],
        'published_timestamp': ['ds:4', 1, 2, 10, 1, 0],
        'pegi': ['ds:4', 1, 2, 9, 0],
        'pegi_detail': ['ds:4', 1, 2, 9, 2, 1],
        'os': ['ds:4', 1, 2, 140, 1, 1, 0, 0, 1],
        'rating': ['ds:4', 1, 2, 51, 0, 1],
        'description': ['ds:4', 1, 2, 72, 0, 1],
        'price': ['ds:4', 1, 2, 57, 0, 0, 0, 0, 1, 0, 2],
        'num_of_reviews': ['ds:4', 1, 2, 51, 2, 1],
        'developer_email': ['ds:4', 1, 2, 69, 1, 0],
        'developer_address': ['ds:4', 1, 2, 69, 2, 0],
        'developer_website': ['ds:4', 1, 2, 69, 0, 5, 2],
        'developer_privacy_policy_link': ['ds:4', 1, 2, 99, 0, 5, 2],
        'data_safety_list': ['ds:4', 1, 2, 136, 1],
        'updated_on': ['ds:4', 1, 2, 145, 0, 0],
        'app_version': ['ds:4', 1, 2, 140, 0, 0, 0]
    }

    query_mapping = {
        'list_of_apps': ['ds:4', 0, 1, 2, 22, 0],
        'list_of_apps_2': ['ds:4', 0, 1, 3, 22, 0],
        'list_of_apps_generic': ['ds:4', 0, 1, 0, 22, 0],
        'list_of_apps_generic_2': ['ds:4', 0, 1, 1, 22, 0],
        'app_id_in_list': [0, 0, 0],
        'first_result': ['ds:4', 0, 1, 0, 23, 16, 2, 41, 0, 2],
        'first_result_2': ['ds:4', 0, 1, 1, 23, 16, 2, 41, 0, 2],
        'list_of_apps_developer': ['ds:3', 0, 1, 0, 22, 0],
        'list_of_apps_developer_id': ['ds:3', 0, 1, 0, 21, 0],
        'app_id_in_list_dev_id': [0, 0],
    }

    # Subdomain for collections
    # Can be used to identify links for additional collections
    # Used for similar links on app detail page as only Similar links uses
    collection_subdomain = '/store/apps/collection/'

    # Subdomain for app detail pages
    # Can be used to identify links to app pages
    app_detail_link_subdomain = '/store/apps/details?id='

    @staticmethod
    def get_nested_item(item_holder, list_of_indexes):
        """
        Recursive function to use list of indexes to get nested item
        """
        index = list_of_indexes[0]
        if len(list_of_indexes) > 1:
            return WebsiteMappings.get_nested_item(item_holder[index], list_of_indexes[1:])
        else:
            return item_holder[index]

    @staticmethod
    def extract_json_block(html, block_id):
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
        block = re.sub(r", sideChannel: {$", "", block)

        return block

    @staticmethod
    def find_item_from_json_mapping(google_app_detail_request_result, app_detail_mapping):
        """
        Takes the request.get().text result from a Google App Detail page and uses the
        self.extract_json_block function along with a nested index mapping to retreive
        a specific item.
        """
        # find specific json block
        ds_json_block = app_detail_mapping[0]
        json_block_raw = WebsiteMappings.extract_json_block(google_app_detail_request_result, ds_json_block)
        json_block = json.loads(json_block_raw)

        return WebsiteMappings.get_nested_item(json_block, app_detail_mapping[1:])


class PlayStoreUtils:
    """
    Helper class to access the names of the other classes
    """

    def get_entries(self, clazz_name):
        """
        Get the members and their names from the function

        : param obj clazz_name: Name of the class to be read
        : return obj json: A JSON object of name against values
        """
        method_names = {}
        for collection in dir(clazz_name):
            if not collection.startswith('__'):
                method_names[str(collection.replace('_', ' '))] = getattr(clazz_name, str(collection))
        return json.dumps({'names': method_names})


class PlayStoreCollections:
    """
    Play store collection IDs
    Borrowed from https://github.com/facundoolano/google-play-scraper. These are
    the various collections displayed in the Play Store, usually on the front
    page.
    """
    TOP_FREE = "topselling_free"
    TOP_PAID = "topselling_paid"
    GROSSING = "topgrossing"
    TRENDING = "movers_shakers"
    TOP_FREE_GAMES = "topselling_free_games"
    TOP_PAID_GAMES = "topselling_paid_games"
    TOP_GROSSING_GAMES = "topselling_grossing_games"
    NEW_FREE = "topselling_new_free"
    NEW_PAID = "topselling_new_paid"
    NEW_FREE_GAMES = "topselling_new_free_games"
    NEW_PAID_GAMES = "topselling_new_paid_games"


class PlayStoreCategories:
    """
    Play Store category IDs

    Borrowed from https://github.com/facundoolano/google-play-scraper. These are
    the app's categories.
    """
    APPLICATION = "APPLICATION"
    ANDROID_WEAR = "ANDROID_WEAR"
    ART_AND_DESIGN = "ART_AND_DESIGN"
    AUTO_AND_VEHICLES = "AUTO_AND_VEHICLES"
    BEAUTY = "BEAUTY"
    BOOKS_AND_REFERENCE = "BOOKS_AND_REFERENCE"
    BUSINESS = "BUSINESS"
    COMICS = "COMICS"
    COMMUNICATION = "COMMUNICATION"
    DATING = "DATING"
    EDUCATION = "EDUCATION"
    ENTERTAINMENT = "ENTERTAINMENT"
    EVENTS = "EVENTS"
    FINANCE = "FINANCE"
    FOOD_AND_DRINK = "FOOD_AND_DRINK"
    HEALTH_AND_FITNESS = "HEALTH_AND_FITNESS"
    HOUSE_AND_HOME = "HOUSE_AND_HOME"
    LIBRARIES_AND_DEMO = "LIBRARIES_AND_DEMO"
    LIFESTYLE = "LIFESTYLE"
    MAPS_AND_NAVIGATION = "MAPS_AND_NAVIGATION"
    MEDICAL = "MEDICAL"
    MUSIC_AND_AUDIO = "MUSIC_AND_AUDIO"
    NEWS_AND_MAGAZINES = "NEWS_AND_MAGAZINES"
    PARENTING = "PARENTING"
    PERSONALIZATION = "PERSONALIZATION"
    PHOTOGRAPHY = "PHOTOGRAPHY"
    PRODUCTIVITY = "PRODUCTIVITY"
    SHOPPING = "SHOPPING"
    SOCIAL = "SOCIAL"
    SPORTS = "SPORTS"
    TOOLS = "TOOLS"
    TRAVEL_AND_LOCAL = "TRAVEL_AND_LOCAL"
    VIDEO_PLAYERS = "VIDEO_PLAYERS"
    WEATHER = "WEATHER"
    GAME = "GAME"
    GAME_ACTION = "GAME_ACTION"
    GAME_ADVENTURE = "GAME_ADVENTURE"
    GAME_ARCADE = "GAME_ARCADE"
    GAME_BOARD = "GAME_BOARD"
    GAME_CARD = "GAME_CARD"
    GAME_CASINO = "GAME_CASINO"
    GAME_CASUAL = "GAME_CASUAL"
    GAME_EDUCATIONAL = "GAME_EDUCATIONAL"
    GAME_MUSIC = "GAME_MUSIC"
    GAME_PUZZLE = "GAME_PUZZLE"
    GAME_RACING = "GAME_RACING"
    GAME_ROLE_PLAYING = "GAME_ROLE_PLAYING"
    GAME_SIMULATION = "GAME_SIMULATION"
    GAME_SPORTS = "GAME_SPORTS"
    GAME_STRATEGY = "GAME_STRATEGY"
    GAME_TRIVIA = "GAME_TRIVIA"
    GAME_WORD = "GAME_WORD"
    FAMILY = "FAMILY"
    FAMILY_ACTION = "FAMILY_ACTION"
    FAMILY_BRAINGAMES = "FAMILY_BRAINGAMES"
    FAMILY_CREATE = "FAMILY_CREATE"
    FAMILY_EDUCATION = "FAMILY_EDUCATION"
    FAMILY_MUSICVIDEO = "FAMILY_MUSICVIDEO"
    FAMILY_PRETEND = "FAMILY_PRETEND"


class PlayStoreAgeBrackets:
    """
    Play Store age bracket IDs

    Borrowed from https://github.com/facundoolano/google-play-scraper. These are
    the app's age brackets, which can be used to restrict search results.
    """
    FIVE_UNDER = "AGE_RANGE1"
    SIX_EIGHT = "AGE_RANGE2"
    NINE_UP = "AGE_RANGE3"


class PlayStoreException(BaseException):
    """
    Thrown when an error occurs in the Play Store scraper
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "PlayStoreException, {0}".format(self.message)
        else:
            return "PlayStoreException raised"
