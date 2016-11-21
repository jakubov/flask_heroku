"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

GOOGLE_MAPS_API_KEY = 'AIzaSyC6bDMjMQNBGGu_FS95DUpXNC4ppyxWhug'

GOOGLE_MAPS_API_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

OPENWEATHERMAP_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
OPENWEATHERMAP_API_KEY = '47c1704ee6778aef7c1fcb71e597208c'


@app.route('/')
def home():
    return render_template('loadsmart_ui.html')


@app.route('/home/')
def get_temps():
    temps_response = {}
    if request.query_string:
        print request.query_string
        address = request.query_string
        # address = '4031 18th ave'
        # address = '4031 18th ave'
        # address = '1600 Amphitheatre Parkway Mountain View CA'
        # address = '1600 Amphitheatre Parkway Mountain View'
        # address = '1600 Amphitheatre Parkway'
        # address = '48 east 22nd street'


        address_dict = {}
        address_data = get_address_zipcode(address)
        if address_data:
            if len(address_data) == 1:
                address_dict = address_data[0]
                current_temp = get_location_temperture(address_dict['zip_code'])
                address_dict['temp'] = current_temp
                temps_response['data'] = address_dict
                temps_response['status'] = 'success'
                return json.dumps(temps_response)
                # return 'Hello! Current Temperture in {}, {} is {} degrees'.format(address_temp_response['city'],
                #                                                                   address_temp_response['state'],
                #                                                                   current_temp)
            else:
                temps_response['status'] = 'failure'
                temps_response['reason'] = 'multiple locations'
                return json.dumps(temps_response)
        else:
            temps_response['status'] = 'failure'
            temps_response['reason'] = 'no results found'
            return json.dumps(temps_response)
    else:
        temps_response['status'] = 'failure'
        temps_response['reason'] = 'invalid query'
        return temps_response


def get_address_zipcode(address):
    url = GOOGLE_MAPS_API_BASE_URL + '?address=' + address + '&key=' + GOOGLE_MAPS_API_KEY
    r = requests.get(url)
    json_results = r.json()
    address_payload = []
    if json_results['status'] == 'OK':
        results = json_results['results']
        address_response = {}
        address_data = {}

        for result in results:
            formatted_address = result['formatted_address']
            formatted_address_split = formatted_address.split(",")
            if len(formatted_address_split) < 4:
                continue
            city = formatted_address_split[1].strip()
            state = formatted_address_split[2].strip().split(" ")[0]
            zip_code = formatted_address_split[2].strip().split(" ")[1]
            address_data['formatted_address'] = formatted_address
            address_data['city'] = city
            address_data['state'] = state
            address_data['zip_code'] = zip_code
            address_payload.append(address_data)
    return address_payload


def get_location_temperture(zip_code):
    url = OPENWEATHERMAP_BASE_URL + '?zip=' + zip_code + ', us' + '&appid=' + OPENWEATHERMAP_API_KEY
    r = requests.get(url)
    json_results = r.json()
    temp = json_results['main']['temp']
    temp = 9 / 5 * (int(temp) - 273) + 32
    return temp

# @app.route('/')
# def home():
#     """Render website's home page."""
#     return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
