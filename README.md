# Google Play Store Scraper
This defines a lightweight Python class that can be used to scrape app 
information from the Google Play Store. It defines a couple of methods that can
be used to get relevant app IDs given a set of parameters, and a couple of 
methods to then scrape data about these app IDs.

Much of this has been adapted from 
[google-play-scraper](https://github.com/facundoolano/google-play-scraper), a 
nodeJS-based scraper that does similar things. But this scraper uses Python.

## Getting started
The following scrapes app details about all apps similar to the first result 
for the 'fortnite' search query:

```
from google_play_scraper.scraper import PlayStoreScraper

scraper = PlayStoreScraper()
results = scraper.get_app_ids_for_query("fortnite")
similar = scraper.get_similar_app_ids_for_app(results[0])

app_details = scraper.get_multiple_app_details(similar)
print(list(app_details))
```

Documentation is not available separately yet, but the code is relatively
simple and you can look in the `scraper.py` file to see what methods are 
available and what their parameters are.

## Credits & License
This scraper was developed by the 
[Digital Methods Initiative](https://digitalmethods.net), and is distributed
under the MIT license. See LICENSE for details. We additionally thank Iain 
Emsley for his contributions to the code.