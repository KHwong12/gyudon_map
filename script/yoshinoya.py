################################################################################
# Description: Collect attributes of yoshinoya stores in Japan
# day, holiday, holidayHours, holidayHoursIsRegular, intervals
################################################################################

import requests
import csv

from bs4 import BeautifulSoup

def get_data_yoshinoya(storeid):
    """

    Parameters
    ----------
    storeid: id of the shop, available in yoshinoya_id.csv

    Returns
    -------
    None if the storeid does not exist
    dict with following keys
    """

    store_details = {'storeid': storeid}

    url = 'https://stores.yoshinoya.com/{}'.format(storeid)

    try:
        r = requests.get(url, allow_redirects=False)
        r.raise_for_status()

    except:
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

    # Get lat and lng
    geo = soup.find('meta', {'name':'geo.position'})

    latlng = geo['content'].split(';')

    store_details['lat'] = latlng[0]
    store_details['lng'] = latlng[1]

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

    # Convert the special characters in the list (in string format) from js format to python format
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

        store_details[f'{dayOfTheWeek[:3]}_open'] = openingTime
        store_details[f'{dayOfTheWeek[:3]}_close'] = closingTime

    return store_details


def main():

    with open('yoshinoya_id.csv') as yoshinoya_id:
        id_reader = csv.reader(yoshinoya_id)

        # Skip the headers
        header = next(yoshinoya_id, None)

        with open('yoshinoya_rawdata.csv', 'w', newline='') as csvfile:

            for row in id_reader:

                storeid = row[0]

                print(f"Processing {storeid}...")

                store_row = get_data_yoshinoya(storeid)

                if store_row == None:

                    print(f"failed to request the page with storeid {storeid}")
                    continue

                writer = csv.DictWriter(csvfile, fieldnames = store_row.keys())

                writer.writerow(store_row)

            csvfile.close()


if __name__ == '__main__':
    main()
