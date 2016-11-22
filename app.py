"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import sys
import requests
import json
import re
import datetime
from datetime import timedelta
import logging

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

GOOGLE_MAPS_API_KEY = 'AIzaSyC6bDMjMQNBGGu_FS95DUpXNC4ppyxWhug'

GOOGLE_MAPS_API_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

OPENWEATHERMAP_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
OPENWEATHERMAP_API_KEY = '47c1704ee6778aef7c1fcb71e597208c'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class WeatherRequests(db.Model):
    __tablename__ = "weather_requests"
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(10))
    location = db.Column(db.String(100))
    temperature = db.Column(db.Integer())
    created_at = db.Column(db.DateTime())

    def __init__(self, zip_code, temperature, location, created_at):
        self.zip_code = zip_code
        self.temperature = temperature
        self.location = location
        self.created_at = created_at

    def __repr__(self):
        return '<zip_code %r>' % self.zip_code


@app.route('/')
def home():
    return render_template('loadsmart_ui.html')


@app.route('/home/', methods=["GET"])
def get_temps():
    temperature_response = {}
    if request.query_string:
        address = request.query_string.strip()
        logging.info('*** got address {}'.format(address))
        address_dict = {}
        zip_code = None
        address_data = None

        # parse search string for a zip code
        reg = re.compile('\d{5}')
        regex_result = reg.findall(address)
        if regex_result:
            zip_code = regex_result[0]
            logging.info('*** got zip code {}'.format(zip_code))
            res = db.session.query(WeatherRequests).filter(WeatherRequests.zip_code == zip_code).first()
            if res:
                current_temp = res.temperature
                location = res.location.split(',')
                address_dict['city'] = location[0]
                address_dict['state'] = location[1]

                current_time = datetime.datetime.utcnow()
                created_at = datetime.datetime.strptime(str(res.created_at), '%Y-%m-%d %H:%M:%S')
                diff = current_time - created_at
                if diff < timedelta(minutes=6):
                    address_dict['temp'] = current_temp
                    temperature_response['data'] = address_dict
                    temperature_response['status'] = 'success'
                    return json.dumps(temperature_response)
                else:
                    # zip codes exists but an hour lapsed - get updated current temp
                    current_temp = get_location_temperture(zip_code)
                    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                    res.temperature = current_temp
                    res.created_at = current_time
                    db.session.commit()

                    address_dict['temp'] = current_temp
                    temperature_response['data'] = address_dict
                    temperature_response['status'] = 'success'
                    return json.dumps(temperature_response)
            else:
                address_data = get_address_zipcode(zip_code)
        else:
            address_data = get_address_zipcode(address)

        if address_data:
            if len(address_data) == 1:
                address_dict = address_data[0]
                zip_code = address_dict['zip_code']
                current_temp = get_location_temperture(zip_code)
                current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                location = address_dict['city'] + ',' + address_dict['state']
                # if not db.session.query(WeatherRequests).filter(WeatherRequests.zip_code == zip_code).count():
                w_req = WeatherRequests(zip_code, current_temp, location, current_time)
                db.session.add(w_req)
                db.session.commit()

                address_dict['temp'] = current_temp
                temperature_response['data'] = address_dict
                temperature_response['status'] = 'success'
                return json.dumps(temperature_response)
            else:
                temperature_response['status'] = 'failure'
                temperature_response['reason'] = 'multiple locations'
                return json.dumps(temperature_response)
        else:
            temperature_response['status'] = 'failure'
            temperature_response['reason'] = 'no results found'
            return json.dumps(temperature_response)
    else:
        temperature_response['status'] = 'failure'
        temperature_response['reason'] = 'invalid query'
        return temperature_response


def get_address_zipcode(address):
    url = GOOGLE_MAPS_API_BASE_URL + '?address=' + address + '&key=' + GOOGLE_MAPS_API_KEY
    r = requests.get(url)
    json_results = r.json()
    address_payload = []
    if json_results['status'] == 'OK':
        results = json_results['results']
        address_data = {}

        for result in results:
            formatted_address = result['formatted_address']
            formatted_address_split = formatted_address.split(",")

            if len(formatted_address_split) < 3:
                continue
            if len(formatted_address_split) == 4:
                city = formatted_address_split[1].strip()
                state = formatted_address_split[2].strip().split(" ")[0]
                zip_code = formatted_address_split[2].strip().split(" ")[1]
            if len(formatted_address_split) == 3:
                city = formatted_address_split[0].strip()
                state = formatted_address_split[1].strip().split(" ")[0]
                zip_code = formatted_address_split[1].strip().split(" ")[1]

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
