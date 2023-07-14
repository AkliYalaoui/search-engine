import os

SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_ID = os.getenv("SEARCH_ID")
COUNTRY = "dz"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&num=10&gl=" + COUNTRY
RESULT_COUNT = 20

