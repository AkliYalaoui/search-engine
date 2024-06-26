from bs4 import BeautifulSoup
from urllib.parse import urlparse
from contrast_ratio import get_contrast_ratio
import re
import requests
from settings import *


with open("blacklist.txt") as f:
    domains = set(f.read().split("\n"))

def tracker_scripts(row):
    soup = BeautifulSoup(row["html"])
    scripts = soup.find_all("script", {"src": True})
    srcs = [s.get("src") for s in scripts]

    links = soup.find_all("a", {"href": True})
    href = [l.get("href") for l in links]

    all_domains = [urlparse(s).hostname for s in srcs + href]
    return len([a for a in all_domains if a in domains])

def get_anchor_tags_count(row):
    soup = BeautifulSoup(row["html"])
    links = soup.find_all("a", {"href": True})
    href = [l.get("href") for l in links]

    all_domains = [urlparse(s).hostname for s in href]
    return len([a for a in all_domains if a not in domains])

def get_aria_attrs_count(row):
    soup = BeautifulSoup(row["html"])

    # Find all elements with ARIA attributes
    aria_tags = soup.find_all(lambda tag: any(attr.startswith("aria") for attr in tag.attrs))
    aria_attributes = [list(filter(lambda attr: attr.startswith("aria"), tag.attrs.keys())) for tag in aria_tags]

    # Count the total number of ARIA attributes
    total_aria_attrs = sum(len(attr_list) if isinstance(attr_list, list) else 1 for attr_list in aria_attributes)

    return total_aria_attrs


def get_percentage_alt_img(row):
    soup = BeautifulSoup(row["html"])
    # Find all img tags and extract alt attribute
    img_tags = soup.find_all('img')
    alt_tags = [tag.get('alt') for tag in img_tags if tag.get('alt')]

    # Calculate the percentage
    total_images = len(img_tags)
    if total_images == 0:
        return 1
    images_with_alt = len(alt_tags)
    percentage = images_with_alt / total_images
    
    return percentage


def get_css_content(css_url, ROOT):
    get_url = css_url
    if not css_url.startswith("http"):
        get_url = ROOT +  css_url

    # Fetch the CSS content (if it's a URL)
    try:
      response = requests.get(get_url)
      if response.status_code == 200:
          return response.text
    except Exception as e:
      print(e)
      return ""


def get_percentage_size_units(row):
    soup = BeautifulSoup(row["html"])

    # Find all elements with style attribute
    elements_with_style = soup.find_all(lambda tag: 'style' in tag.attrs)

    elements_with_size_units = 0
    elements_with_px_units = 0

    for element in elements_with_style:
        styles = element.get('style')
        if styles:
            styles = styles.lower()
            if 'rem' in styles or 'em' in styles:
                elements_with_size_units += 1
            if 'px' in styles:
                elements_with_px_units += 1

     # Find CSS files and check for size units
    css_files = soup.find_all('link', rel='stylesheet')

    for css_file in css_files:
        css_url = css_file.get('href')
        if css_url:
            css_content = get_css_content(css_url, row["link"].replace(urlparse(row["link"]).path, ""))
            if css_content:
                size_matches = re.findall(r"(\d+(?:\.\d+)?(?:rem|em))", css_content)
                if size_matches:
                    elements_with_size_units += len(size_matches)

                px_matches = re.findall(r"[0-9]+px", css_content)
                if px_matches: 
                    elements_with_px_units += len(px_matches)

    total_elements = elements_with_px_units + elements_with_size_units
    if total_elements > 0:
        size_units_percentage = (elements_with_size_units / total_elements)
    else:
        size_units_percentage = 0

    return size_units_percentage

class Filter():
    def __init__(self, results):
        self.filtered = results.copy()

    def scripts_filter(self):
        scripts_count = self.filtered.apply(tracker_scripts, axis=1)
        if scripts_count.max() != scripts_count.min():
            normalized_count = (scripts_count - scripts_count.min()) / (scripts_count.max() - scripts_count.min())
        else:
            normalized_count = 0.0
        print("scripts_filter", normalized_count)
        self.filtered["rank"] = normalized_count

    def anchor_tags_filter(self):
        anchor_count = self.filtered.apply(get_anchor_tags_count, axis=1)
        if anchor_count.max() != anchor_count.min():
            normalized_count  = (anchor_count - anchor_count.min()) / (anchor_count.max() - anchor_count.min())
        else:
            normalized_count = 0.0
        print("anchor_tags_filter", normalized_count)
        self.filtered["rank"] -= normalized_count

    def alt_tags_filter(self):
        alt_percentages = self.filtered.apply(get_percentage_alt_img, axis=1)
        print("alt_tags_filter", alt_percentages)
        self.filtered["rank"] -= alt_percentages

    def aria_tags_filter(self):
        aria_attrs_count = self.filtered.apply(get_aria_attrs_count, axis=1)
        if aria_attrs_count.max() != aria_attrs_count.min():
            normalized_count  = (aria_attrs_count - aria_attrs_count.min()) / (aria_attrs_count.max() - aria_attrs_count.min())
        else:
            normalized_count = 0.0
        print("aria_tags_filter", normalized_count)
        self.filtered["rank"] -= 2* normalized_count

    def size_units_filter(self): 
        size_units_percentage  = self.filtered.apply(get_percentage_size_units, axis=1)
        print("size_units_filter", size_units_percentage)
        self.filtered["rank"] -= size_units_percentage 

    def contrast_ratio_filter(self):
        contrast_ratio = self.filtered.apply(lambda row: get_contrast_ratio(row["link"]), axis=1)
        if contrast_ratio.max() != contrast_ratio.min():
            normalized_count  = (contrast_ratio - contrast_ratio.min()) / (contrast_ratio.max() - contrast_ratio.min())
        else:
            normalized_count = 0.0
        print("contrast_ratio", normalized_count)
        self.filtered["rank"] -= normalized_count

    def sort(self, contrast_ratio):
        self.scripts_filter()
        self.anchor_tags_filter()
        self.alt_tags_filter()
        self.aria_tags_filter()
        self.size_units_filter()
        if contrast_ratio : 
            self.contrast_ratio_filter()
        self.filtered = self.filtered.sort_values("rank", ascending=True)
        self.filtered["rank"] = self.filtered["rank"]
        return self.filtered