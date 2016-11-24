Loadsmart coding challenge
==========================

API endpoints:

Weather Queries:
    Takes a free-formatted location address send by the UI (jquery ajax call) or curl command.

    Assumptions made:
    - Google Geocoding API is used to get the zipcode for the given address
    - Weather is fetched from Open Weather Map’s API.  Any request for the same zip code that were made within
    less than hour since last request are pulled an weather_requests table (based on the assumption that
    the temperature for a Zipcode doesn’t vary within 1­hour windows).
    - Addresses that belong to a zip code that already in the db will re-use the temperature
    based on the assumption that the temperature does not vary within the same Zipcode.

    Usage:
        GET https://obscure-cove-65098.herokuapp.com/api/temperature/?query=<address>

    e.g:

     curl -H "Content-type: application/json" -X GET https://obscure-cove-65098.herokuapp.com/api/temperature/?query=10013
      or
     curl -H "Content-type: application/json" -G -v "https://obscure-cove-65098.herokuapp.com/api/temperature" --data-urlencode "query=39 wooster st new york"

    response:

    {
        "status": "success",
        "data":
            {
                "state": "NY", "city": "New York", "temp":39
             }
    }


Usage Queries:
    Downloads a json file output (when run via browser) or json stdout (via curl) that
    reports app usage.  Please note that the api uses fake ip addresses generator to make the dataset usage more
    'realistic' when testing (in live environment the fake ip generator should be replaced by request.remote_addr)

    Usage:

    single ip_address:
        GET https://obscure-cove-65098.herokuapp.com/api/usage/<ip_address>

    e.g.:
        curl -H "Content-type: application/json" -X GET https://obscure-cove-65098.herokuapp.com/api/usage/192.0.2.12

    response:

    {
        "data": [
            {
                "ip_address": "192.0.2.12",
                "total_hits": 1
            }
        ]
    }

    all ip_addresses:
        GET https://obscure-cove-65098.herokuapp.com/api/usage/

    response:

    {
        "data": [
            {
                "ip_address": "192.0.2.14",
                "total_hits": 1
            },
            {
                "ip_address": "192.0.2.6",
                "total_hits": 2
            },
            {
                "ip_address": "192.0.2.12",
                "total_hits": 1
            }
        ],
        "total_hits": 4,
        "total_ip_addresses": 3
    }

Database:
    postgreSQL hosted on Heroku (tables created via Heroku CLI):

    obscure-cove-65098::DATABASE=> CREATE TABLE weather_requests_ip_tracker (
    obscure-cove-65098::DATABASE(>   ip_address varchar(50),
    obscure-cove-65098::DATABASE(>   hit_count integer
    obscure-cove-65098::DATABASE(> );
    obscure-cove-65098::DATABASE=> CREATE TABLE weather_requests (
    obscure-cove-65098::DATABASE(>   id serial not null,
    obscure-cove-65098::DATABASE(>   zip_code varchar(10),
    obscure-cove-65098::DATABASE(>   location varchar(100),
    obscure-cove-65098::DATABASE(>   temperature smallint,
    obscure-cove-65098::DATABASE(>   ip_address varchar(50),
    obscure-cove-65098::DATABASE(>   created_at timestamp default current_timestamp
    obscure-cove-65098::DATABASE(> );


Unit Tests:
    All unit tests are in test.py