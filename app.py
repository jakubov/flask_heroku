"""
Loadsmart Weather app
"""

import os
import sys
import requests
import json
import re
import datetime
from datetime import timedelta
import logging
import random

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


GOOGLE_MAPS_API_KEY = 'AIzaSyC6bDMjMQNBGGu_FS95DUpXNC4ppyxWhug'
GOOGLE_MAPS_API_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

OPENWEATHERMAP_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
OPENWEATHERMAP_API_KEY = '47c1704ee6778aef7c1fcb71e597208c'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

fake_ip_addresses = ['192.0.2.1',
                     '192.0.2.2',
                     '192.0.2.3',
                     '192.0.2.4',
                     '192.0.2.5',
                     '192.0.2.6',
                     '192.0.2.7',
                     '192.0.2.8',
                     '192.0.2.9',
                     '192.0.2.10',
                     '192.0.2.11',
                     '192.0.2.12',
                     '192.0.2.13',
                     '192.0.2.14'
                     ]


class WeatherRequests(db.Model):
    __tablename__ = "weather_requests"
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(10))
    location = db.Column(db.String(100))
    temperature = db.Column(db.Integer())
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime())

    def __init__(self, zip_code, temperature, location, ip_address, created_at):
        self.zip_code = zip_code
        self.temperature = temperature
        self.location = location,
        self.ip_address = ip_address,
        self.created_at = created_at

    def __repr__(self):
        return '<zip_code %r>' % self.zip_code


class WeatherRequestsTracker(db.Model):
    __tablename__ = "weather_requests_ip_tracker"
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime())

    def __init__(self, ip_address, created_at):
        self.ip_address = ip_address
        self.created_at = created_at

    def __repr__(self):
        return '<ip_address %r>' % self.ip_address

@app.route('/')
def home():
    return render_template('loadsmart_ui.html')


@app.route('/api/temperature/', methods=["GET"])
def get_temperature():
    temperature_response = {}
    if request.query_string:
        track_request_ip_address()
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

            # first to a table look up for the zip code
            res = db.session.query(WeatherRequests).filter(WeatherRequests.zip_code == zip_code).first()
            if res:
                current_temp = res.temperature
                location = res.location.split(',')
                address_dict['city'] = location[0]
                address_dict['state'] = location[1]

                current_time = datetime.datetime.utcnow()
                created_at = datetime.datetime.strptime(str(res.created_at), '%Y-%m-%d %H:%M:%S')
                diff = current_time - created_at
                # if request was made less than 1 hour, then return the temperature
                if diff < timedelta(minutes=60):
                    address_dict['temp'] = current_temp
                    temperature_response['data'] = address_dict
                    temperature_response['status'] = 'success'
                    return json.dumps(temperature_response)
                else:
                    # else get updated temperature
                    current_temp = get_location_temperature(zip_code)
                    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                    res.temperature = current_temp
                    res.created_at = current_time
                    db.session.commit()

                    address_dict['temp'] = current_temp
                    temperature_response['data'] = address_dict
                    temperature_response['status'] = 'success'
                    return json.dumps(temperature_response)
            else:
                # do an address-zip code lookup
                address_data = get_address_zipcode(zip_code)
        else:
            # query string does not contain a zip code, so do an address-zip code lookup
            address_data = get_address_zipcode(address)

        if address_data:
            # to keep the UI and app simple, will only handle query that return single address
            if len(address_data) == 1:
                address_dict = address_data[0]
                zip_code = address_dict['zip_code']
                res = db.session.query(WeatherRequests).filter(WeatherRequests.zip_code == zip_code).first()
                if res:
                    current_temp = res.temperature
                    location = res.location.split(',')
                    address_dict['city'] = location[0]
                    address_dict['state'] = location[1]

                    current_time = datetime.datetime.utcnow()
                    created_at = datetime.datetime.strptime(str(res.created_at), '%Y-%m-%d %H:%M:%S')
                    diff = current_time - created_at
                    if diff < timedelta(minutes=60):
                        address_dict['temp'] = current_temp
                        temperature_response['data'] = address_dict
                        temperature_response['status'] = 'success'
                        return json.dumps(temperature_response)
                    else:
                        # zip codes exists but an hour lapsed - get updated current temp
                        current_temp = get_location_temperature(zip_code)
                        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                        res.temperature = current_temp
                        res.created_at = current_time
                        db.session.commit()

                        address_dict['temp'] = current_temp
                        temperature_response['data'] = address_dict
                        temperature_response['status'] = 'success'
                        return json.dumps(temperature_response)
                else:
                    current_temp = get_location_temperature(zip_code)
                    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    location = address_dict['city'] + ',' + address_dict['state']
                    w_req = WeatherRequests(zip_code, current_temp, location,
                                            random.choice(fake_ip_addresses), current_time)
                    db.session.add(w_req)
                    db.session.commit()

                    address_dict['temp'] = current_temp
                    temperature_response['data'] = address_dict
                    temperature_response['status'] = 'success'
                    return json.dumps(temperature_response)
            else:
                # result returned multiple addresses, tell user to modify search
                temperature_response['status'] = 'failure'
                temperature_response['reason'] = 'found multiple locations'
                return json.dumps(temperature_response)
        else:
            temperature_response['status'] = 'failure'
            temperature_response['reason'] = 'no results found'
            return json.dumps(temperature_response)
    else:
        temperature_response['status'] = 'failure'
        temperature_response['reason'] = 'invalid query'
        return temperature_response


@app.route('/api/usage/', methods=["GET"])
def get_ip_address_app_usage():
    temperature_response = {}
    usage_list = []
    usage_dict = {}
    results = db.session.query(WeatherRequestsTracker).all()
    if results:
        for result in results:
            usage_dict['ip_address'] = result.ip_address
            usage_dict['created_at'] = str(result.created_at)
            usage_list.append(usage_dict)
    temperature_response['data'] = usage_list
    temperature_response['data'] = {'total': len(results)}
    return jsonify(temperature_response)


def track_request_ip_address():
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    # request.remote_addr
    _req_tracker = WeatherRequestsTracker(random.choice(fake_ip_addresses), current_time)
    db.session.add(_req_tracker)
    db.session.commit()


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
            reg = re.compile('\d{5}')
            regex_result = reg.findall(formatted_address)
            formatted_address_split = formatted_address.split(",")

            if len(formatted_address_split) < 3 or not regex_result:
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


def get_location_temperature(zip_code):
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
