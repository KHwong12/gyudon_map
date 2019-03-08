################################################################################
# Description: Collect attributes of yoshinoya stores in Japan
# Attribute includes 'storeid','brand','name','lat','lon','postalCode','address',
#                    'DOW_open', 'DOW_close' (DOW implies day of the week)
################################################################################

import requests
import csv

from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


def get_data_yoshinoya(storeid):
    """
    Get the data of the store with given storeid

    Parameters
    ----------
    storeid: id of the shop, available in yoshinoya_id.csv

    Returns
    -------
    None if the storeid does not exist
    dict with following keys
    'storeid','brand','name','lat','lon','postalCode','address',
    'DOW_open', 'DOW_close' (DOW implies day of the week)
    """

    store_details = {'storeid': storeid}

    url = 'https://stores.yoshinoya.com/{}'.format(storeid)

    try:
        r = requests.get(url, allow_redirects=False)

        # Catch responses > 300
        if r.status_code >= 300:
            raise HTTPError

    except HTTPError:
        print("Page not found. Status code is not 200.")
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Get brand and name of the store
    LocationNamebrand = soup.find('span', {'class': "LocationName-brand"})

    if 'ysn' in storeid:
        store_details['brand'] = '吉野家'
    elif 'hnmr' in storeid:
        store_details['brand'] = '吉野家×はなまるうどん'

    name = LocationNamebrand.text.strip(store_details['brand'])

    store_details['name'] = name.strip(' ')

    # Get lat and lon
    geo = soup.find('meta', {'name':'geo.position'})

    latlon = geo['content'].split(';')

    store_details['lat'] = latlon[0]
    store_details['lon'] = latlon[1]

    # Get location attributes
    location = soup.find('address')

    # First span in the address class is the postalCode
    postalCode_class = location.span.extract()

    store_details['postalCode'] = postalCode_class.text

    # Remove the prefix of the address
    store_details['address'] = location.text.strip('〒 ')

    # Get day-specific opening hours
    hours = soup.find('div',
            {'class': 'c-location-hours-details-wrapper js-location-hours-table'})

    # Convert the special characters in the list (in string format) from js to python format
    for old, new in [('true', 'True'),('false', 'False')]:
        hours['data-days'] = hours['data-days'].replace(old, new)

    # Convert the opening hours' list from string to array
    openinghours_list = eval(hours['data-days'])

    for day in openinghours_list:

        dayOfTheWeek = day['day']

        try:
            openingTime = day['intervals'][0]['start']
            closingTime = day['intervals'][0]['end']

        # Attribute 'intervals' is an empty list if the store is closed on that day
        except IndexError:
            openingTime = None
            closingTime = None

        # Create key in the form of 'MON_open', 'MON_close', 'TUE_open', etc.
        store_details[f'{dayOfTheWeek[:3]}_open'] = openingTime
        store_details[f'{dayOfTheWeek[:3]}_close'] = closingTime

    return store_details


def main():
    """
    Get details of the store with given csv storing the storeid of all yoshinoya stores
    """

    outFile = r'../product/yoshinoya_rawdata.csv'

    with open(r'../data/yoshinoya_id.csv') as yoshinoya_id:

        # Reader to read store id
        id_reader = csv.reader(yoshinoya_id)

        # Skip the headers
        header = next(yoshinoya_id, None)

        # Keys from the get_data function
        headers = ['storeid','brand','name','lat','lon','postalCode','address',
                    'MON_open','MON_close','TUE_open','TUE_close','WED_open','WED_close',
                    'THU_open','THU_close','FRI_open','FRI_close','SAT_open','SAT_close',
                    'SUN_open','SUN_close']

        with open(outFile, 'w', newline='') as csvfile:

            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)

            # Write the headers
            writer.writeheader()

            for row in id_reader:

                storeid = row[0]

                print(f"Processing {storeid}...")

                store_row = get_data_yoshinoya(storeid)

                if store_row == None:

                    print(f"failed to request the page with storeid {storeid}")
                    continue

                writer.writerow(store_row)

            csvfile.close()


if __name__ == '__main__':
    main()
