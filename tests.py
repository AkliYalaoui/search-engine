import pandas as pd
from filter import Filter
import requests


links = ["https://baleares.craigslist.org/", "https://www.w3.org/WAI/", "https://www.bbc.co.uk/accessibility", "https://www.a11yproject.com/", "https://www.dailymail.co.uk/home/index.html", "https://www.rottentomatoes.com/"]

htmls = []
for link in links : 
    data = requests.get(link, timeout=5)
    html = data.text
    htmls.append(html)


# Create a DataFrame with test cases
test_cases = pd.DataFrame({
    "link": links ,
    "html" : htmls,
    "rank" : [1, 2, 3, 4, 5, 6], 
    "expected_order" : ["https://www.w3.org/WAI/", "https://www.bbc.co.uk/accessibility", "https://www.a11yproject.com/", "https://baleares.craigslist.org/", "https://www.dailymail.co.uk/home/index.html", "https://www.rottentomatoes.com/"]
})

# Instantiate the Filter class
filter_obj = Filter(test_cases)

# Test filter()
def test_filter():
    filter_obj.filter()
    actual_rank = filter_obj.filtered["rank"]
    print(filter_obj.filtered["link"])
    print(actual_rank)


# Run the tests
test_filter()