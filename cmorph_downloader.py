import re
import calendar
import os
from datetime import date
from pathlib import Path
import sys
from bs4 import BeautifulSoup
import os.path
from urllib.request import urlopen, urlretrieve
import urllib.parse
import requests

year=int(sys.argv[1])
month=int(sys.argv[2])
print("This is year",year)

def day_iter(year, month):
    for i in range(1, calendar.monthrange(year, month)[1] + 1):
        yield i

def construct_path(day):
    return f'https://www.ncei.noaa.gov/data/cmorph-high-resolution-global-precipitation-estimates/access/30min/8km/%04d/%02d/{day:02d}/' % (year, month)


for day in day_iter(year, month):

  # target page containing links to the image files
    target_page = construct_path(day)
    print(target_page)

  # local path
    dest_path = f'/home/emir/cmorph/{year}/{month:02d}/{day:02d}/'
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)
            # NOTE: this implementation (easily modified) assumes link hrefs contain absolute
            # URL's with 'http://' protocol prefix e.g. http://example.com/dir/image.jpg and that
            # all links on the target_page point to desired image files.

    img_urls = []

    page = urlopen(target_page).read()
    soup = BeautifulSoup(page, 'html.parser')
            # print(soup)
    for link in soup.findAll('a', attrs={'href': re.compile('_(\d+)\.nc$')}):
        print(link)
        img_urls.append(link.get('href'))

    counter = 1
    
    for img_url in img_urls:

        img_filename = Path(img_url).name

        img_dest = dest_path + '/' + img_filename
        
                # recreate url with a url-encoded img_filename to handle whitespace in filenames
        # img_url_clean = img_url.rsplit('/', 1)[0] + '/' + urllib.parse.quote(img_filename)
        img_url_clean = img_url.rsplit('/', 1)[0] + '/' + img_filename
        img_url_clean = target_page+ img_url_clean.split('/')[0]
        print("clean", img_url_clean)
        print(str(counter) + ":\t " + img_dest)
        counter += 1
        
        # urlretrieve(img_url_clean, img_dest)
        request = requests.get(img_url_clean, timeout=30, stream=True)

        # Open the output file and make sure we write in binary mode
        with open(img_dest, 'wb') as fh:
            # Walk through the request response in chunks of 1024 * 1024 bytes, so 1MiB
            for chunk in request.iter_content(1024 * 1024):
                # Write the chunk to the file
                fh.write(chunk)
                # Optionally we can check here if the download is taking too long

    print("DONE!")
    print("Saved " + str(counter - 1) + " files.")

exit()