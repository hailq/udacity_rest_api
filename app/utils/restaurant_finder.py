from geocode import getGeocodeLocation
import json
import httplib2

import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

foursquare_client_id = "0WXK3A1ZCOS4ZQCVMA0GIL0ETEYRPQQBQ5KW5PHGU0XDUE5C"
foursquare_client_secret = "QRMLMU0S2ZPEHR0DBQUB3H5FVIA3D4YJZTVA5XQ4AWH2YYNA"


def findARestaurant(mealType, location):
    # 1. Use getGeocodeLocation to get the latitude and longitude coordinates of the location string.
    lat, lng = getGeocodeLocation(location)

    # 2.  Use foursquare API to find a nearby restaurant with the latitude, longitude, and mealType strings.
    # HINT: format for url will be something like https://api.foursquare.com/v2/venues/search?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20130815&ll=40.7,-74&query=sushi
    url = (
        "https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&ll=%s,%s&query=%s&limit=1&v=20170130"
        % (foursquare_client_id, foursquare_client_secret, lat, lng, mealType)
    )

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # 3. Grab the first restaurant
    restaurant = result['response']['venues'][0]

    if restaurant:

        restaurant_name = restaurant['name']
        restaurant_address = ' '.join(restaurant['location']['formattedAddress'])

        venue_id = restaurant['id']

        # 4. Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
        url = url = (
            "https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&client_secret=%s&limit=1&v=20170130"
            % (venue_id, foursquare_client_id, foursquare_client_secret)
        )
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # 5. Grab the first image
        if result['response']['photos']['items']:
            image = result['response']['photos']['items'][0]
            image_url = image['prefix'] + '300x300' + image['suffix']
        else:
            # 6. If no image is available, insert default a image url
            image_url = 'http://pixabay.com/get/8926af5eb597ca51ca4c/1433440765/cheeseburger-34314_1280.png?direct'

        # 7. Return a dictionary containing the restaurant name, address, and image url
        return {'name': restaurant_name, 'address': restaurant_address, 'image': image_url}

    else:
        print 'No restaurant found for %s' % location
        return None
