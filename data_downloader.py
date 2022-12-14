import argparse
import json
import os
import time

import requests
import tqdm
from pexels_api import API

MAX_IMAGES = 1200
RESULTS_PER_PAGE = 100
PAGE_LIMIT = MAX_IMAGES / RESULTS_PER_PAGE

PEXELS_API_KEY = '563492ad6f917000010000016a8b628f9c414303b78470894a6168dd'
api = API(PEXELS_API_KEY)
photos_dict = {}
page = 1
counter = 0

parser = argparse.ArgumentParser()
parser.add_argument('query')
args = parser.parse_args()
query = args.query

# Step 1: Getting urls and meta information
while page < PAGE_LIMIT:
    api.search(query, page=page, results_per_page=RESULTS_PER_PAGE)
    photos = api.get_entries()
    for photo in tqdm.tqdm(photos):
        photos_dict[photo.id] = vars(photo)['_Photo__photo']
        counter += 1
        if not api.has_next_page:
            break
        page += 1

print(f"Finishing at page: {page}")
print(f"Images were processed: {counter}")

# Step 2: Downloading
PATH = f'./alcohol/{query}/'
RESOLUTION = 'original'

if photos_dict:
    os.makedirs(PATH, exist_ok=True)

    # Saving dict
    with open(os.path.join(PATH, f'{query}.json'), 'w') as fout:
        json.dump(photos_dict, fout)

    for val in tqdm.tqdm(photos_dict.values()):
        url = val['src'][RESOLUTION]
        fname = os.path.basename(val['src']['original'])
        image_path = os.path.join(PATH, fname)
        if not os.path.isfile(image_path):
            response = requests.get(url, stream=True)
            with open(image_path, 'wb') as outfile:
                outfile.write(response.content)
        else:
            # ignore if already downloaded
            print(f"File {image_path} exists")