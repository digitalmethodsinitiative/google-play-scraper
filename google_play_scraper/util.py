"""
Play Store Scraper utility classes
"""

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
	pass