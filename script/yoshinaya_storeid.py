################################################################################
# Description: Get the id number of Yoshinoya stores by recursively 'clicking'
#              the pages listing all prefectures, then all cities
################################################################################

import requests
import csv

from bs4 import BeautifulSoup


url = 'https://stores.yoshinoya.com'
outFile = 'data/yoshinoya_id.csv'

# Get the list storing names and links of all prefectures
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
prefectures = soup.find_all('a', {"class": "Directory-listLink"}, href=True)

with open(outFile, 'w', newline='') as csvfile:

    writer = csv.writer(csvfile)

    # Write the headers
    writer.writerow(['storeid', 'pre_name', 'city_name', 'brand', 'num'])

    for prefecture in prefectures:

        # Get the link listing all regions in one prefecture
        pre_name = prefecture['href']
        pre_url = f"{url}/{pre_name}"

        r_pre = requests.get(pre_url)
        prefecture_soup = BeautifulSoup(r_pre.text, 'html.parser')

        cities = prefecture_soup.find_all('a', {"class": "Directory-listLink"}, href=True)

        for city in cities:

            # Get the name of the city by collecting the text of parnet's span
            city_name = city.parent.span.text

            print(f"Processing stores in {pre_name} / {city_name}")

            # Collect the store details if there is only one store in the region
            if city['data-count'] == '(1)':

                storeid = city['href'].strip('../')
                brand = storeid.split('_')[0]
                num = storeid.split('_')[1]

                print([storeid, pre_name, city_name, brand, num])
                writer.writerow([storeid, pre_name, city_name, brand, num])

            # Look into the city level index page
            else:

                city_url = f"{url}/{city['href']}"

                r_city = requests.get(city_url)
                city_soup = BeautifulSoup(r_city.text, 'html.parser')

                stores = city_soup.find_all('a', {"class": "Teaser-titleLink"}, href=True)

                for store in stores:

                    storeid = store['href'].strip('../')
                    brand = storeid.split('_')[0]
                    num = storeid.split('_')[1]

                    print([storeid, pre_name, city_name, brand, num])
                    writer.writerow([storeid, pre_name, city_name, brand, num])

    csvfile.close()
