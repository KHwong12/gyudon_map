################################################################################
# Description: Collect attributes of matsuya stores in Japan
# Attribute includes 'storeid','brand','name','lat','lon','postalCode','address',
#                    'business_hour'
################################################################################

"""
TODO: Investigate the other APIs from the script of webpage
https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/address/list

https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/transport/node/list
https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/transport/node/list?type=station.airport

https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop?code={}
https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop/list

https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/weather

https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/route/shape
"""

import requests
import csv

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


def get_data_matsuya(storeid):
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

    # Add the leading zeros to the code
    storeid = f'{storeid:010d}'

    url = f'https://pkg.navitime.co.jp/matsuyafoods/spot/detail?code={storeid}'
    url_api = f'https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop?code={storeid}'

    store_details = {'storeid': storeid}

    try:
        r = requests.get(url, allow_redirects=False)
        r_api = requests.get(url_api, allow_redirects=False)

        # Catch HTTP404 error
        r.raise_for_status()
        r_api.raise_for_status()

    except requests.exceptions.HTTPError:
        return None

    api = r_api.json()

    item = api['items'][0]

    store_details['brand'] = item['categories'][0]['name']

    store_details['name'] = item['name'].strip('{} '.format(store_details['brand']))

    store_details['lat'] = item['coord']['lat']
    store_details['lon'] = item['coord']['lon']

    store_details['postalCode'] = item['postal_code']

    store_details['address'] = item['address_name']

    # Details of opening hours are available in the rendered website
    soup = BeautifulSoup(r.text, 'html.parser')

    # First to third dd in the webpage are address, phone number and openinghours respectively
    openinghours = soup.find_all('dd',
    {'class': 'col-xs-9 w_1_detail_2_1_2-td-value table-style-cell'})[2]

    business_hour = openinghours.text

    # Remove spaces and newline symbols
    for old, new in [('\n', ''),(' ', '')]:
        business_hour = business_hour.replace(old, new)

    store_details['business_hour'] = business_hour

    return store_details

def main():
    """
    Get the details of the shop by brute-force searching the id of the shop
    """

    # Approximate minimum and maximum storeid are searched manually
    storeid_min = 1
    storeid_max = 1402

    outFile = r'../product/matsuya_rawdata.csv'

    # Keys from the get_data function
    headers = ['storeid','brand','name','lat','lon','postalCode','address',
                'business_hour']

    with open(outFile, 'w', newline='') as csvfile:

        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

        # Write the headers
        writer.writeheader()

        for storeid in range(storeid_min,storeid_max+1):

            print(f"Processing {storeid}...")

            store_row = get_data_matsuya(storeid)

            if store_row == None:

                print(f"failed to request the page with storeid {storeid}")
                continue

            writer.writerow(store_row)

        csvfile.close()


if __name__ == '__main__':
    main()
