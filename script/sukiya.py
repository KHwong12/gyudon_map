################################################################################
# Description: Collect attributes of sukiya stores in Japan

################################################################################

import requests
import csv

from bs4 import BeautifulSoup


def get_data_sukiya(shopid):
    """
    Get the data of the shop
    return None if the shopid does not exist
    """

    """
    Get the name of the shop by brute-force searching the id of the shop
    """

    url = f'https://maps.sukiya.jp/jp/detail/{shopid}.html'
    r = requests.get(url, allow_redirects=False)

    print(shopid, r.status_code)

    # Pass all urls non-exist store id which will be redirected to the index page
    if r.status_code == 302:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Get name of the shop
    shop = soup.find('div', {'class': 'shop'})

    shopdetails = shop.text.strip('\n').split('\u3000')

    brand = shopdetails[0]
    name = shopdetails[1]

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

    # Extract the postalcode, which is stored in the span class of the address data list
    postal = location.span.extract()

    postalcode = postal.text.strip('〒')

    # Get address
    address = location.dd.text.strip('\n')

    """
    Get business hours and other details using API
    """

    # Query the API by the name of the shop
    api_url = f'https://maps.sukiya.jp/api/search/?name={name}'

    r_api_json = requests.get(api_url).json()

    # data of the store (in dict format) is bonded in a list, thus [0] is needed
    datalist = r_api_json['mapdata'][0]

    lat = datalist['lat']
    lng = datalist['lng']
    business_hour1 = datalist['business_hour1']
    business_hour2 = datalist['business_hour2']
    business_hour3 = datalist['business_hour3']

    print(shopid,brand,name,lat,lng,postalcode,address)

    return [shopid,brand,name,lat,lng,postalcode,address,business_hour1,business_hour2,business_hour3]


def main():

    # minimum and maximum shopid through manual searching
    shopid_min = 1
    shopid_max = 2100

    with open('sukiya_rawdata.csv', 'w', newline='') as csvfile:

        writer = csv.writer(csvfile)

        # Write the headings
        writer.writerow(['shopid','brand','name','lat','lng','postalcode','address',
                        'business_hour1','business_hour2','business_hour3'])

        for shopid in range(shopid_min,shopid_max):

            store_row = get_data_sukiya(shopid)

            if store_row == None:
                continue

            writer.writerow(store_row)

        csvfile.close()

if __name__ == '__main__':
    main()
