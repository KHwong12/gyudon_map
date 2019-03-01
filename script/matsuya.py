################################################################################
# Description: Collect attributes of matsuya stores in Japan
#
################################################################################

"""
List of APIs from the script of webpage
https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/address/list

https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/transport/node/list
https://pkg.navitime.co.jp/matsuyafoods/api/proxy1/transport/node/list?type=station.airport

https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop?code={}
https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop/list
pkg.navitime.co.jp/matsuyafoods/api/proxy1/weather
pkg.navitime.co.jp/matsuyafoods/api/proxy1/route/shape
"""

import requests
import csv

from bs4 import BeautifulSoup

def get_data_matsuya(storeid):
    """

    Parameters
    ----------
    storeid

    Returns
    -------
    None if the storeid does not exist

    dict with following keys
    """

    # Add the leading zeros to the code
    storeid = f'{storeid:010d}'

    url = f'https://pkg.navitime.co.jp/matsuyafoods/spot/detail?code={storeid}'
    url_api = f'https://pkg.navitime.co.jp/matsuyafoods/api/proxy2/shop?code={storeid}'

    store_details = {'storeid': storeid}

    try:
        r = requests.get(url, allow_redirects=False)
        r_api = requests.get(url_api, allow_redirects=False)

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

    # minimum and maximum shopid through manual searching
    storeid_min = 1
    storeid_max = 1402

    with open('matsuya_rawdata2.csv', 'w', newline='') as csvfile:

        writer = csv.writer(csvfile)

        # Write the headings
        writer.writerow(['storeid','brand','name','lat','lon','postalCode','address',
                        'business_hour'])

        for storeid in range(storeid_min,storeid_max+1):

            print(f"Processing {storeid}...")

            store_row = get_data_matsuya(storeid)

            if store_row == None:

                print(f"failed to request the page with storeid {storeid}")
                continue

            print(store_row)

            writer = csv.DictWriter(csvfile, fieldnames = store_row.keys())

            writer.writerow(store_row)

        csvfile.close()


if __name__ == '__main__':
    main()
