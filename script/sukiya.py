#coding=utf-8

################################################################################
# Description: Collect attributes of nakau stores in Japan
# Attribute includes 'storeid','brand','name','lat','lon','postalCode','address',
#                    'business_hour1','business_hour2','business_hour3'
################################################################################

import requests
import csv

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


def get_data_sukiya(storeid):
    """
    Get the data of the store with given storeid

    Parameters
    ----------
    storeid (int)

    Returns
    -------
    None if the storeid does not exist

    dict with following keys
    'storeid','brand','name','lat','lon','postalCode','address',
    'business_hour1','business_hour2','business_hour3'
    """

    # Initialise dict
    store_details = {'storeid': storeid}

    url = f'https://maps.sukiya.jp/jp/detail/{storeid}.html'

    try:
        r = requests.get(url, allow_redirects=False)

        # Catch responses > 300
        if r.status_code >= 300:
            raise HTTPError

    except HTTPError:
        print("Page not found. Status code is not 200.")
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Get name of the shop
    shop = soup.find('div', {'class': 'shop'})

    shopdetails = shop.text.strip('\n').split('\u3000')

    store_details['brand'] = shopdetails[0]
    store_details['name'] = shopdetails[1]

    # Get data on shop location
    location = soup.find('dl', {"class": "address"})

    # Extract the google map link of the details
    maplink = location.div.extract()

    """
    # split the url to google map, which is in the format on http://maps.google.co.jp/maps?q=34.7429584410997,134.84215994866
    latlng = maplink.a['href'].strip('http://maps.google.co.jp/maps?q=').split(',')

    lat = latlng[0]
    lng = latlng[1]
    """

    # Extract the postalCode, which is stored in the span class of the address data list
    postal = location.span.extract()

    store_details['postalCode'] = postal.text.strip('〒')

    # Get address
    store_details['address'] = location.dd.text.strip('\n')

    """
    Get business hours and other details using API
    """

    # Query the API by the name of the shop
    api_url = 'https://maps.sukiya.jp/api/search/?name={}'.format(store_details['name'])

    r_api = requests.get(api_url).json()

    # data of the store (in dict format) is bounded inside a list, thus [0] is needed
    datalist = r_api['mapdata'][0]

    store_details['lat'] = datalist['lat']
    store_details['lon'] = datalist['lng']
    store_details['business_hour1'] = datalist['business_hour1']
    store_details['business_hour2'] = datalist['business_hour2']
    store_details['business_hour3'] = datalist['business_hour3']

    print(store_details)

    return store_details


def main():
    """
    Get the details of the shop by brute-force searching the id of the shop
    """

    # Approximate minimum and maximum storeid are searched manually
    storeid_min = 1
    storeid_max = 2100

    outFile = r'../product/sukiya_rawdata.csv'

    # Keys from the get_data function
    headers = ['storeid','brand','name','lat','lon','postalCode','address',
                'business_hour1','business_hour2','business_hour3']

    with open(outFile, 'w', newline='') as csvfile:

        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

        # Write the headers
        writer.writeheader()

        for storeid in range(storeid_min,storeid_max+1):

            print(f"Processing {storeid}...")

            store_row = get_data_sukiya(storeid)

            if store_row == None:

                print(f"failed to request the page with storeid {storeid}")
                continue

            writer.writerow(store_row)

        csvfile.close()


if __name__ == '__main__':
    main()
